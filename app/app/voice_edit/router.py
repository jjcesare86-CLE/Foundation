"""
Foundation Layer · voice_edit · router.py

Mount this router on the foundation-api FastAPI app:

    from foundation.voice_edit.router import router as voice_edit_router
    app.include_router(voice_edit_router, prefix="/voice-edit")

All endpoints require the standard PIPELINE_API_KEY auth header (handled
by the existing verify_api_key dependency in the parent app).
"""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse

from . import edit_engine, intent_parser, session_manager, upload_classifier
from .models import (
    ConfirmRequest,
    CreateSessionRequest,
    CreateSessionResponse,
    EditEventSummary,
    EditSource,
    JsonPatchOp,
    ParsedIntent,
    SessionChannel,
    SurfaceSchema,
    TextEditRequest,
    UndoRequest,
    UploadPresignedResponse,
    UploadRequest,
    VoiceEditRequest,
    VoiceEditResponse,
)

# In the parent app, replace this no-op with your real auth dep:
#   from foundation.auth import verify_api_key
def verify_api_key(request: Request) -> None:
    expected = os.getenv("PIPELINE_API_KEY")
    if not expected:
        return  # auth disabled in dev
    got = request.headers.get("X-API-Key") or request.headers.get("Authorization", "").removeprefix("Bearer ")
    if got != expected:
        raise HTTPException(status_code=401, detail="Invalid API key")


router = APIRouter(tags=["voice_edit"], dependencies=[Depends(verify_api_key)])


# ---------------------------------------------------------------------
# Surface schema (frontend asks for this on mount)
# ---------------------------------------------------------------------
@router.get("/surfaces/{surface_id}/schema", response_model=SurfaceSchema)
def get_surface_schema(surface_id: str) -> SurfaceSchema:
    cfg = edit_engine.get_surface_config(surface_id)
    return SurfaceSchema(
        id=surface_id,
        display_name=surface_id.replace("_", " ").title(),
        product=_product_for_surface(surface_id),
        schema_version=1,
        fields=cfg["fields"],
    )


def _product_for_surface(surface_id: str) -> str:
    return {
        "brand_portfolio": "shared",
        "website": "AN",
        "voice_agent_prompt": "VoiceMIO",
        "social_brand_launcher": "AN",
    }.get(surface_id, "shared")


# ---------------------------------------------------------------------
# Sessions
# ---------------------------------------------------------------------
@router.post("/sessions", response_model=CreateSessionResponse)
def create_session(req: CreateSessionRequest) -> CreateSessionResponse:
    return session_manager.get_or_create_session(req)


@router.get("/sessions/{session_id}")
def get_session(session_id: UUID) -> dict[str, Any]:
    s = session_manager.get_session(session_id)
    if not s:
        raise HTTPException(404, "Session not found")
    return s.model_dump(mode="json")


@router.post("/sessions/resume")
def resume_session(token: str, channel: SessionChannel) -> dict[str, Any]:
    """Email-link landing page hits this with the JWT and a fresh client_id."""
    try:
        s = session_manager.resume_from_token(token, channel)
    except Exception as e:
        raise HTTPException(401, f"Invalid handoff token: {e}")
    return s.model_dump(mode="json")


# ---------------------------------------------------------------------
# Voice edit — the centerpiece
# ---------------------------------------------------------------------
@router.post("/sessions/{session_id}/voice-edit", response_model=VoiceEditResponse)
async def voice_edit(session_id: UUID, req: VoiceEditRequest) -> VoiceEditResponse:
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(404, "Session not found")

    surface_cfg = edit_engine.get_surface_config(session.surface_id)
    schema_for_parser = _schema_for_parser(surface_cfg)
    current_state, _, _ = edit_engine.fetch_target_document(
        session.surface_id, session.business_id
    )

    klass, parsed = await intent_parser.route_voice_input(
        transcript=req.transcript,
        surface_schema=schema_for_parser,
        current_state=current_state,
        last_visible_section=req.last_visible_section,
    )

    # ---- Non-edit utterances ----
    if klass == "undo":
        try:
            event = edit_engine.undo_event(session_id=session_id)
        except edit_engine.ValidationError as e:
            return VoiceEditResponse(
                success=False,
                agent_should_say=f"I couldn't undo that — {e}.",
            )
        return VoiceEditResponse(
            success=True,
            event=event,
            agent_should_say=event.state_after_summary or "Reverted.",
        )

    if klass == "confirm":
        return await _apply_pending(session_id)

    if klass == "cancel":
        session_manager.set_pending_edit(session_id, None)
        return VoiceEditResponse(success=True, agent_should_say="Got it, cancelled.")

    if klass in ("question", "chitchat"):
        return VoiceEditResponse(
            success=True,
            agent_should_say="",  # let the conversational agent handle it
        )

    # ---- Edit path ----
    assert parsed is not None

    if not parsed.confident:
        # Need a clarifying question
        return VoiceEditResponse(
            success=True,
            agent_should_say=parsed.clarifying_question or "Could you clarify which one?",
            clarifying_question=parsed.clarifying_question,
            candidates=parsed.candidates,
        )

    # Confident — but maybe needs verbal confirmation
    if parsed.requires_confirmation:
        pending_id = uuid4()
        session_manager.set_pending_edit(session_id, {
            "pending_id": str(pending_id),
            "transcript": req.transcript,
            "parsed": parsed.model_dump(mode="json"),
        })
        say = (
            parsed.explanation
            or "Just to confirm, I'll make that change."
        ) + " Should I go ahead?"
        return VoiceEditResponse(
            success=True,
            agent_should_say=say,
            event=EditEventSummary(
                id=pending_id,
                source=EditSource.VOICE,
                transcript=req.transcript,
                affected_fields=parsed.affected_fields,
                state_after_summary=parsed.explanation,
                requires_confirmation=True,
                pending=True,
                created_at=datetime.utcnow(),
            ),
        )

    # Confident + no confirmation needed → apply immediately
    try:
        event = edit_engine.commit_edit(
            session_id=session_id,
            business_id=session.business_id,
            surface_id=session.surface_id,
            intent=parsed,
            source=EditSource.VOICE,
            transcript=req.transcript,
            intent_model=intent_parser.MODEL_PARSE,
        )
    except edit_engine.ValidationError as e:
        return VoiceEditResponse(
            success=False,
            agent_should_say=f"I can't change that — {e}",
        )

    return VoiceEditResponse(
        success=True,
        event=event,
        agent_should_say=parsed.explanation or "Done.",
        state_diff={"affected": parsed.affected_fields},
    )


async def _apply_pending(session_id: UUID) -> VoiceEditResponse:
    session = session_manager.get_session(session_id)
    pending = session.pending_edit if session else None
    if not pending:
        return VoiceEditResponse(success=False, agent_should_say="There's nothing to confirm.")

    parsed = ParsedIntent(**pending["parsed"])
    try:
        event = edit_engine.commit_edit(
            session_id=session_id,
            business_id=session.business_id,
            surface_id=session.surface_id,
            intent=parsed,
            source=EditSource.VOICE,
            transcript=pending.get("transcript"),
            intent_model=intent_parser.MODEL_PARSE,
        )
    except edit_engine.ValidationError as e:
        return VoiceEditResponse(success=False, agent_should_say=f"Sorry — {e}")

    session_manager.set_pending_edit(session_id, None)
    return VoiceEditResponse(
        success=True,
        event=event,
        agent_should_say=parsed.explanation or "Done.",
    )


# ---------------------------------------------------------------------
# Direct text/form edit (web form, no LLM)
# ---------------------------------------------------------------------
@router.post("/sessions/{session_id}/text-edit", response_model=EditEventSummary)
def text_edit(session_id: UUID, req: TextEditRequest) -> EditEventSummary:
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(404, "Session not found")

    intent = ParsedIntent(
        confident=True,
        patch=req.patch,
        confidence=1.0,
        explanation="Saved",
        requires_confirmation=False,
        affected_fields=[op.path for op in req.patch],
    )
    try:
        return edit_engine.commit_edit(
            session_id=session_id,
            business_id=session.business_id,
            surface_id=session.surface_id,
            intent=intent,
            source=EditSource.TEXT,
        )
    except edit_engine.ValidationError as e:
        raise HTTPException(400, str(e))


# ---------------------------------------------------------------------
# Confirm / undo
# ---------------------------------------------------------------------
@router.post("/sessions/{session_id}/confirm", response_model=VoiceEditResponse)
async def confirm(session_id: UUID, req: ConfirmRequest) -> VoiceEditResponse:
    if not req.confirmed:
        session_manager.set_pending_edit(session_id, None)
        return VoiceEditResponse(success=True, agent_should_say="Cancelled.")
    return await _apply_pending(session_id)


@router.post("/sessions/{session_id}/undo", response_model=EditEventSummary)
def undo(session_id: UUID, req: UndoRequest) -> EditEventSummary:
    try:
        return edit_engine.undo_event(session_id=session_id, event_id=req.event_id)
    except edit_engine.ValidationError as e:
        raise HTTPException(400, str(e))


# ---------------------------------------------------------------------
# Uploads
# ---------------------------------------------------------------------
@router.post("/sessions/{session_id}/upload", response_model=UploadPresignedResponse)
def upload_presign(session_id: UUID, req: UploadRequest) -> UploadPresignedResponse:
    """
    Step 1 of drag-drop: frontend asks for a signed URL, then PUTs the
    file directly to Supabase Storage. After upload completes, frontend
    hits /upload/{asset_id}/complete.
    """
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(404, "Session not found")

    asset_id = uuid4()
    safe_name = req.filename.replace("/", "_").replace("..", "_")
    storage_path = f"business/{session.business_id}/{asset_id}_{safe_name}"

    # Generate signed upload URL via Supabase Storage admin API
    bucket = "voice-edit-assets"
    res = edit_engine._supabase.storage.from_(bucket).create_signed_upload_url(storage_path)
    # res = {"signedURL": "...", "path": "...", "token": "..."}

    return UploadPresignedResponse(
        asset_id=asset_id,
        upload_url=res["signedURL"],
        storage_path=storage_path,
        expires_at=datetime.now(tz=timezone.utc) + timedelta(minutes=15),
    )


@router.post("/sessions/{session_id}/upload/{asset_id}/complete", response_model=EditEventSummary)
async def upload_complete(
    session_id: UUID,
    asset_id: UUID,
    req: UploadRequest,
    image_meta: dict | None = None,
) -> EditEventSummary:
    """
    Step 2: file has been uploaded. Classify it, attach to the right
    field, write the audit event.

    `image_meta` (optional from frontend): {"width": int, "height": int, "has_alpha": bool}
    """
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(404, "Session not found")

    # Pull the bytes only if we'll need vision classification (ambiguous case)
    classification = await upload_classifier.classify_upload(
        filename=req.filename,
        mime_type=req.mime_type,
        width=(image_meta or {}).get("width"),
        height=(image_meta or {}).get("height"),
        has_alpha=(image_meta or {}).get("has_alpha"),
        image_bytes=None,    # let the classifier ask for bytes if it really needs them
        surface_id=session.surface_id,
        user_provided_label=req.user_provided_label,
        surface_field_hint=req.surface_field_hint,
    )

    if classification.needs_user_confirmation or not classification.suggested_field_path:
        # Park as a "pending asset" rather than auto-attaching.
        # The frontend will ask the user where it goes.
        return EditEventSummary(
            id=asset_id,
            source=EditSource.UPLOAD,
            transcript=None,
            affected_fields=[],
            state_after_summary=f"Uploaded — where should this {classification.kind} go?",
            requires_confirmation=True,
            pending=True,
            created_at=datetime.utcnow(),
        )

    storage_path = f"business/{session.business_id}/{asset_id}_{req.filename}"
    public_url = f"{os.getenv('SUPABASE_URL')}/storage/v1/object/public/voice-edit-assets/{storage_path}"

    intent = ParsedIntent(
        confident=True,
        patch=[
            JsonPatchOp(
                op="replace",
                path=classification.suggested_field_path,
                value=public_url,
            )
        ],
        confidence=classification.confidence,
        explanation=f"{classification.kind.replace('_', ' ').title()} updated.",
        requires_confirmation=False,
        affected_fields=[classification.suggested_field_path],
    )

    return edit_engine.commit_edit(
        session_id=session_id,
        business_id=session.business_id,
        surface_id=session.surface_id,
        intent=intent,
        source=EditSource.UPLOAD,
        asset_id=asset_id,
        asset_path=storage_path,
    )


# ---------------------------------------------------------------------
# Audit log
# ---------------------------------------------------------------------
@router.get("/sessions/{session_id}/events")
def list_events(session_id: UUID, limit: int = 50) -> list[dict[str, Any]]:
    res = (
        edit_engine._supabase.table("edit_events")
        .select("*")
        .eq("session_id", str(session_id))
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )
    return res.data or []


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------
def _schema_for_parser(surface_cfg: dict) -> dict:
    """
    Reduce the YAML config to just what the parser needs — paths,
    aliases, types. No validators, no internal flags.
    """
    return {
        "fields": [
            {
                "key": key,
                "path": fdef["path"],
                "aliases": fdef.get("aliases", []),
                "type": fdef.get("type", "string"),
                "enum_values": fdef.get("enum_values"),
                "max_length": fdef.get("max_length"),
                "confirm": fdef.get("confirm", False),
            }
            for key, fdef in surface_cfg["fields"].items()
        ]
    }
