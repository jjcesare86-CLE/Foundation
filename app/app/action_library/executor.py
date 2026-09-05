"""
create_action / approve_action / reject_action / execute_action.

Demo-mode gating lives here: execute_action never calls a real external API
when is_demo_mode() says to simulate — it writes a structured
{"mode": "simulated", "would_have": ...} result and marks the row
'simulated', never 'executed'. This never raises outward; approve_action
calls it and stores whatever comes back, including failures.

Proof-of-Work (UNLAZY_AND_PROOF_OF_WORK.md §2.2/§2.4): this module is
where every action's completion claim gets a receipt, centrally, so no
individual handler can skip it. A simulated action can never be
'verified' — it gets verify_method='none', verification_status='pending'
— that's the literal rule from the spec ("Broker methods that cannot
verify must set verify_method='none' and verification_status='pending'
— never 'verified'"), enforced here rather than trusted per-handler.
"""
import logging
from datetime import datetime, timezone
from typing import Optional

from app.database import supabase
from app.action_library.registry import ACTION_REGISTRY, is_demo_mode

logger = logging.getLogger(__name__)


def create_action(
    action_type: str,
    draft: dict,
    payload: Optional[dict] = None,
    agent_id: Optional[str] = None,
    client_id: Optional[str] = None,
    requested_by: Optional[str] = None,
    status: str = "pending",
) -> dict:
    row = {
        "action_type": action_type,
        "draft": draft,
        "payload": payload or {},
        "agent_id": agent_id,
        "client_id": client_id,
        "requested_by": requested_by,
        "status": status,
    }
    result = supabase.schema("foundation").table("agent_actions").insert(row).execute()
    return result.data[0]


def get_action(action_id: str) -> Optional[dict]:
    result = (
        supabase.schema("foundation").table("agent_actions")
        .select("*").eq("id", action_id).execute()
    )
    return result.data[0] if result.data else None


def list_actions(status: Optional[str] = None, agent_id: Optional[str] = None, client_id: Optional[str] = None) -> list[dict]:
    query = supabase.schema("foundation").table("agent_actions").select("*").order("created_at", desc=True)
    if status:
        query = query.eq("status", status)
    if agent_id:
        query = query.eq("agent_id", agent_id)
    if client_id:
        query = query.eq("client_id", client_id)
    return query.execute().data


def update_draft(action_id: str, draft: dict) -> dict:
    result = (
        supabase.schema("foundation").table("agent_actions")
        .update({"draft": draft, "updated_at": datetime.now(timezone.utc).isoformat()})
        .eq("id", action_id).execute()
    )
    return result.data[0]


def reject_action(action_id: str, rejected_by: str, reason: Optional[str] = None) -> dict:
    result = (
        supabase.schema("foundation").table("agent_actions")
        .update({
            "status": "rejected",
            "approved_by": rejected_by,
            "approved_at": datetime.now(timezone.utc).isoformat(),
            "error": reason,
        })
        .eq("id", action_id).execute()
    )
    return result.data[0]


def approve_action(action_id: str, approved_by: str) -> dict:
    """Marks approved, then immediately executes. A downstream failure lands
    as status='failed' with the error on the row — this call itself doesn't
    raise for that case, only for a bad action_id or wrong starting status."""
    action = get_action(action_id)
    if not action:
        raise ValueError(f"action {action_id} not found")
    if action["status"] != "pending":
        raise ValueError(f"action {action_id} is {action['status']}, not pending")

    supabase.schema("foundation").table("agent_actions").update({
        "status": "approved",
        "approved_by": approved_by,
        "approved_at": datetime.now(timezone.utc).isoformat(),
    }).eq("id", action_id).execute()

    return execute_action(action_id)


def execute_action(action_id: str) -> dict:
    action = get_action(action_id)
    if not action:
        raise ValueError(f"action {action_id} not found")

    action_type = action["action_type"]
    handler = ACTION_REGISTRY.get(action_type)

    if handler is None:
        return _finalize(action_id, "failed", error=f"no handler registered for action_type={action_type}")

    demo = is_demo_mode(action_type)
    try:
        raw = handler(action["draft"], action["payload"], demo)
        result = {"mode": "simulated" if demo else "live", **raw}
        ok = result.get("ok", True)
        status = "simulated" if (demo and ok) else ("executed" if ok else "failed")
        return _finalize(action_id, status, result=result, error=None if ok else result.get("detail"), demo=demo)
    except Exception as e:
        logger.exception(f"action {action_id} ({action_type}) execution failed")
        return _finalize(action_id, "failed", error=str(e), demo=demo)


def _finalize(action_id: str, status: str, result: Optional[dict] = None, error: Optional[str] = None, demo: bool = False) -> dict:
    now = datetime.now(timezone.utc).isoformat()
    update = {"status": status, "executed_at": now}
    if result is not None:
        update["result"] = result
    update["error"] = error

    # Proof-of-Work receipt fields — derived here, not trusted from the
    # handler, so no action type can silently skip verification.
    update["claimed_outcome"] = status
    if demo:
        # A simulated call never gets to claim it happened. verified_at
        # stays unset -- there is nothing to timestamp.
        update["verify_method"] = "none"
        update["verification_status"] = "pending"
        update["evidence"] = result
    elif status == "executed":
        update["verify_method"] = (result or {}).get("verify_method", "api_response")
        update["verification_status"] = "verified"
        update["evidence"] = _extract_evidence(result)
        update["verified_at"] = now
    elif status == "failed":
        update["verify_method"] = "api_response"
        update["verification_status"] = "failed"
        update["evidence"] = _extract_evidence(result) if result else {"error": error}
    # 'rejected' and other non-execution statuses don't touch these fields.

    updated = (
        supabase.schema("foundation").table("agent_actions")
        .update(update).eq("id", action_id).execute()
    )
    return updated.data[0]


def _extract_evidence(result: Optional[dict]) -> Optional[dict]:
    """Pulls the identifying fields out of a handler's result -- external
    ids, status codes, counts -- and drops the noise (mode/ok/would_have)."""
    if not result:
        return None
    noise = {"mode", "ok", "would_have", "detail"}
    evidence = {k: v for k, v in result.items() if k not in noise}
    return evidence or None
