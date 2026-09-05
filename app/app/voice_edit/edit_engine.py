"""
Foundation Layer · voice_edit · edit_engine.py

The "apply" half of the system. Given a ParsedIntent, this:
  1. Validates the patch against the surface's editable_fields whitelist
     — anything not whitelisted is REJECTED, even if the parser
     generated it.
  2. Runs field-level validators (phone, email, address, hours).
  3. Computes the inverse patch (so undo works).
  4. Applies the patch to the target document in Supabase.
  5. Writes an edit_event row.
  6. Triggers any post_hooks (logo variants, favicon, etc.) async.
  7. Returns a summary the API layer can hand back to VAPI / web.

Everything here is server-side — no Anthropic calls. Cheap and fast.
"""

from __future__ import annotations

import copy
import os
from typing import Any
from uuid import UUID, uuid4
from datetime import datetime

import yaml
from supabase import Client, create_client

from .models import (
    EditEventSummary,
    EditSource,
    JsonPatchOp,
    ParsedIntent,
)


# ---------------------------------------------------------------------
# Config loading — editable_fields.yaml
# ---------------------------------------------------------------------

_CONFIG_PATH = os.getenv(
    "VOICE_EDIT_CONFIG",
    os.path.join(os.path.dirname(__file__), "config", "editable_fields.yaml"),
)

with open(_CONFIG_PATH, "r", encoding="utf-8") as _f:
    _CONFIG = yaml.safe_load(_f)


def get_surface_config(surface_id: str) -> dict[str, Any]:
    cfg = _CONFIG.get("surfaces", {}).get(surface_id)
    if not cfg:
        raise ValueError(f"Unknown surface: {surface_id}")
    return cfg


def get_allowed_paths(surface_id: str) -> set[str]:
    cfg = get_surface_config(surface_id)
    return {f["path"] for f in cfg["fields"].values()}


def get_field_def_by_path(surface_id: str, path: str) -> tuple[str, dict] | None:
    """Return (field_key, field_def) for the field whose `path` matches."""
    cfg = get_surface_config(surface_id)
    for key, fdef in cfg["fields"].items():
        if fdef["path"] == path or path.startswith(fdef["path"] + "/"):
            return key, fdef
    return None


# ---------------------------------------------------------------------
# Supabase client
# ---------------------------------------------------------------------

_supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_ROLE_KEY"),  # service role bypasses RLS
)


# ---------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------

class ValidationError(ValueError):
    pass


def validate_patch(surface_id: str, patch: list[JsonPatchOp]) -> None:
    """Raise ValidationError if any op touches a non-whitelisted path."""
    allowed = get_allowed_paths(surface_id)
    for op in patch:
        # An op's path is allowed if it equals or descends into an allowed path.
        ok = any(op.path == ap or op.path.startswith(ap + "/") for ap in allowed)
        if not ok:
            raise ValidationError(
                f"Path {op.path!r} is not voice-editable on surface {surface_id!r}."
            )


def run_field_validators(surface_id: str, patch: list[JsonPatchOp]) -> None:
    """Run named validators from editable_fields.yaml. Best-effort."""
    from . import validators as _v   # local import — avoids hard dep at import time
    for op in patch:
        if op.value is None:
            continue
        match = get_field_def_by_path(surface_id, op.path)
        if not match:
            continue
        _, fdef = match
        validator_name = fdef.get("validator")
        if not validator_name:
            continue
        validator = getattr(_v, validator_name, None)
        if validator is None:
            # Skipping unknown validators is intentional — config can list
            # validators that haven't shipped yet without breaking edits.
            continue
        validator(op.value)   # raises ValidationError on bad input


# ---------------------------------------------------------------------
# JSON Pointer + patch application (RFC 6901/6902, with our `append`)
# ---------------------------------------------------------------------

def _split_pointer(path: str) -> list[str]:
    if path == "":
        return []
    if not path.startswith("/"):
        raise ValueError(f"Bad JSON Pointer: {path!r}")
    # RFC 6901 escaping: ~1 → /, ~0 → ~
    return [seg.replace("~1", "/").replace("~0", "~") for seg in path[1:].split("/")]


def _get_at(doc: Any, segments: list[str]) -> Any:
    cur = doc
    for seg in segments:
        if isinstance(cur, list):
            cur = cur[int(seg)]
        else:
            cur = cur[seg]
    return cur


def _set_at(doc: Any, segments: list[str], value: Any) -> None:
    parent = _get_at(doc, segments[:-1])
    last = segments[-1]
    if isinstance(parent, list):
        idx = len(parent) if last == "-" else int(last)
        if last == "-" or idx == len(parent):
            parent.append(value)
        else:
            parent[idx] = value
    else:
        parent[last] = value


def _remove_at(doc: Any, segments: list[str]) -> Any:
    """Returns the removed value (used for inverse patch)."""
    parent = _get_at(doc, segments[:-1])
    last = segments[-1]
    if isinstance(parent, list):
        return parent.pop(int(last))
    return parent.pop(last)


def apply_patch(doc: dict, patch: list[JsonPatchOp]) -> dict:
    """Apply patch in-place to a *copy* of doc. Returns the new doc."""
    new_doc = copy.deepcopy(doc)
    for op in patch:
        segs = _split_pointer(op.path)
        if op.op == "add" or op.op == "replace":
            _set_at(new_doc, segs, op.value)
        elif op.op == "append":
            target = _get_at(new_doc, segs)
            if not isinstance(target, list):
                raise ValidationError(f"append requires list at {op.path}")
            target.append(op.value)
        elif op.op == "remove":
            _remove_at(new_doc, segs)
        elif op.op == "copy":
            src_segs = _split_pointer(op.from_)
            _set_at(new_doc, segs, copy.deepcopy(_get_at(new_doc, src_segs)))
        elif op.op == "move":
            src_segs = _split_pointer(op.from_)
            val = _remove_at(new_doc, src_segs)
            _set_at(new_doc, segs, val)
        else:
            raise ValidationError(f"Unknown op: {op.op}")
    return new_doc


def compute_inverse_patch(
    original: dict, patch: list[JsonPatchOp]
) -> list[JsonPatchOp]:
    """
    Build a patch that undoes the given patch when applied to the
    *post-patch* document. Simple strategy: capture before-values now.
    """
    inverse: list[JsonPatchOp] = []
    for op in patch:
        segs = _split_pointer(op.path)
        if op.op in ("add", "append"):
            # Inverse of add/append is remove
            if op.op == "append":
                # post-patch index = original list length
                target = _get_at(original, segs) if _exists(original, segs) else []
                idx = len(target)
                inverse.append(JsonPatchOp(op="remove", path=f"{op.path}/{idx}"))
            else:
                inverse.append(JsonPatchOp(op="remove", path=op.path))
        elif op.op == "replace":
            old = _get_at(original, segs)
            inverse.append(JsonPatchOp(op="replace", path=op.path, value=old))
        elif op.op == "remove":
            old = _get_at(original, segs)
            inverse.append(JsonPatchOp(op="add", path=op.path, value=old))
        elif op.op in ("copy", "move"):
            # Conservative: snapshot whole doc, restore on undo
            inverse.append(JsonPatchOp(op="replace", path="", value=copy.deepcopy(original)))
    # Reverse so undo applies in correct order
    return list(reversed(inverse))


def _exists(doc: Any, segments: list[str]) -> bool:
    try:
        _get_at(doc, segments)
        return True
    except (KeyError, IndexError, TypeError):
        return False


# ---------------------------------------------------------------------
# Subtree snapshots for the audit log (don't store full doc on every edit)
# ---------------------------------------------------------------------

def snapshot_subtrees(doc: dict, patch: list[JsonPatchOp]) -> dict[str, Any]:
    """For each path in the patch, capture the value at the parent level."""
    snap: dict[str, Any] = {}
    for op in patch:
        segs = _split_pointer(op.path)
        parent_path = "/" + "/".join(segs[:-1]) if segs[:-1] else ""
        if parent_path in snap:
            continue
        try:
            snap[parent_path or "/"] = copy.deepcopy(
                _get_at(doc, segs[:-1]) if segs else doc
            )
        except (KeyError, IndexError, TypeError):
            snap[parent_path or "/"] = None
    return snap


# ---------------------------------------------------------------------
# Read / write the target document via Supabase
# ---------------------------------------------------------------------

def fetch_target_document(surface_id: str, business_id: UUID) -> tuple[dict, str, str]:
    """
    Returns (current_state, target_table, target_column).
    """
    cfg = get_surface_config(surface_id)
    table = cfg["target_table"]
    column = cfg["target_column"]

    # business_profiles is keyed by id; everything else is keyed by business_id
    key_col = "id" if table == "business_profiles" else "business_id"

    res = (
        _supabase.table(table)
        .select(f"{column}")
        .eq(key_col, str(business_id))
        .single()
        .execute()
    )
    state = (res.data or {}).get(column) or {}
    return state, table, column


def write_target_document(
    surface_id: str, business_id: UUID, new_state: dict
) -> None:
    cfg = get_surface_config(surface_id)
    table = cfg["target_table"]
    column = cfg["target_column"]
    key_col = "id" if table == "business_profiles" else "business_id"

    _supabase.table(table).update({column: new_state}).eq(
        key_col, str(business_id)
    ).execute()


# ---------------------------------------------------------------------
# The main commit function
# ---------------------------------------------------------------------

def commit_edit(
    *,
    session_id: UUID,
    business_id: UUID,
    surface_id: str,
    intent: ParsedIntent,
    source: EditSource,
    transcript: str | None = None,
    intent_model: str | None = None,
    asset_id: UUID | None = None,
    asset_path: str | None = None,
) -> EditEventSummary:
    """
    Validate → apply → audit. Atomic-ish: we update the document and the
    edit_events row sequentially. If event-log write fails, the document
    write has already happened — we accept that tradeoff for simplicity.
    """
    if not intent.confident or not intent.patch:
        raise ValidationError("Cannot commit a non-confident intent.")

    validate_patch(surface_id, intent.patch)
    run_field_validators(surface_id, intent.patch)

    current_state, _, _ = fetch_target_document(surface_id, business_id)
    inverse = compute_inverse_patch(current_state, intent.patch)
    new_state = apply_patch(current_state, intent.patch)

    state_before = snapshot_subtrees(current_state, intent.patch)
    state_after = snapshot_subtrees(new_state, intent.patch)

    write_target_document(surface_id, business_id, new_state)

    event_id = uuid4()
    event_row = {
        "id": str(event_id),
        "session_id": str(session_id),
        "business_id": str(business_id),
        "surface_id": surface_id,
        "source": source.value,
        "transcript": transcript,
        "patch": [op.model_dump(by_alias=True, exclude_none=True) for op in intent.patch],
        "inverse_patch": [op.model_dump(by_alias=True, exclude_none=True) for op in inverse],
        "state_before": state_before,
        "state_after": state_after,
        "asset_id": str(asset_id) if asset_id else None,
        "asset_path": asset_path,
        "actor_type": "customer",
        "intent_model": intent_model,
        "intent_confidence": intent.confidence,
    }
    _supabase.table("edit_events").insert(event_row).execute()

    # Fire-and-forget post hooks
    _trigger_post_hooks(surface_id, intent.patch, business_id)

    return EditEventSummary(
        id=event_id,
        source=source,
        transcript=transcript,
        affected_fields=intent.affected_fields,
        state_after_summary=intent.explanation,
        requires_confirmation=intent.requires_confirmation,
        pending=False,
        created_at=datetime.utcnow(),
    )


# ---------------------------------------------------------------------
# Undo
# ---------------------------------------------------------------------

def undo_event(*, session_id: UUID, event_id: UUID | None = None) -> EditEventSummary:
    """
    Apply the inverse_patch of the latest reversible event in this
    session (or a specific event_id), and write a new edit_event with
    source='undo'.
    """
    q = (
        _supabase.table("edit_events")
        .select("*")
        .eq("session_id", str(session_id))
        .is_("reversed_at", "null")
        .neq("source", "undo")
    )
    if event_id:
        q = q.eq("id", str(event_id))
    else:
        q = q.order("created_at", desc=True).limit(1)

    res = q.execute()
    rows = res.data or []
    if not rows:
        raise ValidationError("No reversible event found for this session.")
    target = rows[0]

    business_id = UUID(target["business_id"])
    surface_id = target["surface_id"]
    inverse_ops = [JsonPatchOp(**op) for op in target["inverse_patch"]]

    current_state, _, _ = fetch_target_document(surface_id, business_id)
    new_state = apply_patch(current_state, inverse_ops)
    write_target_document(surface_id, business_id, new_state)

    # Mark the original event as reversed
    undo_event_id = uuid4()
    _supabase.table("edit_events").update(
        {"reversed_by": str(undo_event_id), "reversed_at": "now()"}
    ).eq("id", target["id"]).execute()

    # Insert the undo event
    undo_row = {
        "id": str(undo_event_id),
        "session_id": str(session_id),
        "business_id": str(business_id),
        "surface_id": surface_id,
        "source": EditSource.UNDO.value,
        "patch": [op.model_dump(by_alias=True, exclude_none=True) for op in inverse_ops],
        "inverse_patch": target["patch"],   # reversing the undo gets you back
        "state_before": target["state_after"],
        "state_after": target["state_before"],
        "actor_type": "customer",
    }
    _supabase.table("edit_events").insert(undo_row).execute()

    return EditEventSummary(
        id=undo_event_id,
        source=EditSource.UNDO,
        transcript=None,
        affected_fields=[],
        state_after_summary=f"Reverted: {target.get('transcript') or 'last change'}",
        requires_confirmation=False,
        pending=False,
        created_at=datetime.utcnow(),
    )


# ---------------------------------------------------------------------
# Post-hook dispatcher (background tasks)
# ---------------------------------------------------------------------

def _trigger_post_hooks(
    surface_id: str, patch: list[JsonPatchOp], business_id: UUID
) -> None:
    """
    Reads the post_hook field from each touched field and enqueues the
    job. We use a Supabase 'jobs' table (or Render background worker)
    rather than blocking the request.
    """
    cfg = get_surface_config(surface_id)
    triggered: set[str] = set()
    for op in patch:
        match = get_field_def_by_path(surface_id, op.path)
        if not match:
            continue
        _, fdef = match
        hook = fdef.get("post_hook")
        if hook and hook not in triggered:
            triggered.add(hook)
            _enqueue_job(hook, {"business_id": str(business_id), "path": op.path})


def _enqueue_job(hook_name: str, payload: dict) -> None:
    try:
        _supabase.table("jobs").insert({
            "type": hook_name,
            "payload": payload,
            "status": "queued",
        }).execute()
    except Exception:
        # Don't let post-hook failures break the edit. Log and move on.
        # (Replace with real logging in production.)
        pass
