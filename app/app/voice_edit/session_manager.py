"""
Foundation Layer · voice_edit · session_manager.py

Manages the edit_session lifecycle. Key responsibility: keeping the
phone call, the form, and the email-link handoff all pointing at the
SAME session row so edits propagate everywhere.

Handoff token = short-lived JWT signed with VOICE_EDIT_HANDOFF_SECRET.
The customer can click an emailed link any time within `expires_at`
and the session resumes with their previous state intact.
"""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID, uuid4

import jwt   # PyJWT
from supabase import Client, create_client

from .models import (
    ChannelType,
    CreateSessionRequest,
    CreateSessionResponse,
    EditSession,
    SessionChannel,
    SessionStatus,
)


# ---------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------

_SUPABASE_URL = os.getenv("SUPABASE_URL")
_SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
_HANDOFF_SECRET = os.getenv("VOICE_EDIT_HANDOFF_SECRET", "CHANGE-ME-IN-RENDER")
_HANDOFF_ALGO = "HS256"
_PUBLIC_BASE_URL = os.getenv("VOICE_EDIT_PUBLIC_BASE_URL", "https://app.automaitionnation.com")

_supabase: Client = create_client(_SUPABASE_URL, _SUPABASE_KEY)


# ---------------------------------------------------------------------
# JWT helpers
# ---------------------------------------------------------------------

def _sign_handoff_token(session_id: UUID, business_id: UUID, exp: datetime) -> str:
    payload = {
        "sid": str(session_id),
        "biz": str(business_id),
        "iat": int(datetime.now(tz=timezone.utc).timestamp()),
        "exp": int(exp.timestamp()),
    }
    return jwt.encode(payload, _HANDOFF_SECRET, algorithm=_HANDOFF_ALGO)


def verify_handoff_token(token: str) -> dict[str, Any]:
    """Returns decoded payload {sid, biz, iat, exp} or raises jwt.InvalidTokenError."""
    return jwt.decode(token, _HANDOFF_SECRET, algorithms=[_HANDOFF_ALGO])


def build_handoff_url(token: str, surface_id: str) -> str:
    return f"{_PUBLIC_BASE_URL}/edit/{surface_id}?t={token}"


# ---------------------------------------------------------------------
# Create / find / attach
# ---------------------------------------------------------------------

def get_or_create_session(req: CreateSessionRequest) -> CreateSessionResponse:
    """
    If an active session already exists for (business_id, surface_id),
    attach the new channel to it instead of creating a duplicate.
    This is what makes a mid-call email-link handoff work seamlessly.
    """
    existing = (
        _supabase.table("edit_sessions")
        .select("*")
        .eq("business_id", str(req.business_id))
        .eq("surface_id", req.surface_id)
        .eq("status", SessionStatus.ACTIVE.value)
        .gte("expires_at", datetime.now(tz=timezone.utc).isoformat())
        .limit(1)
        .execute()
    )

    if existing.data:
        row = existing.data[0]
        session = _attach_channel(UUID(row["id"]), req.channel)
    else:
        session = _create_new_session(req)

    handoff_url = (
        build_handoff_url(session.handoff_token, session.surface_id)
        if session.handoff_token else None
    )
    return CreateSessionResponse(session=session, handoff_url=handoff_url)


def _create_new_session(req: CreateSessionRequest) -> EditSession:
    session_id = uuid4()
    expires_at = datetime.now(tz=timezone.utc) + timedelta(minutes=req.expires_in_minutes)
    handoff_token = _sign_handoff_token(session_id, req.business_id, expires_at)

    channel_dump = req.channel.model_dump(mode="json")

    row = {
        "id": str(session_id),
        "business_id": str(req.business_id),
        "surface_id": req.surface_id,
        "channels": [channel_dump],
        "status": SessionStatus.ACTIVE.value,
        "expires_at": expires_at.isoformat(),
        "handoff_token": handoff_token,
    }
    res = _supabase.table("edit_sessions").insert(row).execute()
    return _row_to_session(res.data[0])


def _attach_channel(session_id: UUID, channel: SessionChannel) -> EditSession:
    """Add a new channel (e.g. customer opened the email link in browser)."""
    res = (
        _supabase.table("edit_sessions")
        .select("*")
        .eq("id", str(session_id))
        .single()
        .execute()
    )
    row = res.data
    channels = row["channels"] or []

    # De-dupe: don't add the same channel type+id twice
    new_channel_dump = channel.model_dump(mode="json")
    if not any(_channels_match(c, new_channel_dump) for c in channels):
        channels.append(new_channel_dump)

    update = (
        _supabase.table("edit_sessions")
        .update({"channels": channels})
        .eq("id", str(session_id))
        .execute()
    )
    return _row_to_session(update.data[0])


def _channels_match(a: dict, b: dict) -> bool:
    if a.get("type") != b.get("type"):
        return False
    if a["type"] == ChannelType.VOICE.value:
        return a.get("vapi_call_id") == b.get("vapi_call_id")
    if a["type"] == ChannelType.WEB.value:
        return a.get("client_id") == b.get("client_id")
    return False


def get_session(session_id: UUID) -> EditSession | None:
    res = (
        _supabase.table("edit_sessions")
        .select("*")
        .eq("id", str(session_id))
        .maybe_single()
        .execute()
    )
    return _row_to_session(res.data) if res.data else None


def resume_from_token(token: str, channel: SessionChannel) -> EditSession:
    """Customer clicked the email link — verify token, attach the new channel."""
    payload = verify_handoff_token(token)
    return _attach_channel(UUID(payload["sid"]), channel)


def expire_session(session_id: UUID) -> None:
    _supabase.table("edit_sessions").update(
        {"status": SessionStatus.EXPIRED.value}
    ).eq("id", str(session_id)).execute()


def complete_session(session_id: UUID) -> None:
    _supabase.table("edit_sessions").update(
        {"status": SessionStatus.COMPLETED.value}
    ).eq("id", str(session_id)).execute()


def set_pending_edit(session_id: UUID, pending: dict | None) -> None:
    _supabase.table("edit_sessions").update(
        {"pending_edit": pending}
    ).eq("id", str(session_id)).execute()


# ---------------------------------------------------------------------
# Row → model coercion
# ---------------------------------------------------------------------

def _row_to_session(row: dict) -> EditSession:
    channels = [SessionChannel(**c) for c in (row.get("channels") or [])]
    return EditSession(
        id=UUID(row["id"]),
        business_id=UUID(row["business_id"]),
        surface_id=row["surface_id"],
        channels=channels,
        status=SessionStatus(row["status"]),
        pending_edit=row.get("pending_edit"),
        last_activity_at=datetime.fromisoformat(row["last_activity_at"].replace("Z", "+00:00")),
        expires_at=datetime.fromisoformat(row["expires_at"].replace("Z", "+00:00")),
        handoff_token=row.get("handoff_token"),
        created_at=datetime.fromisoformat(row["created_at"].replace("Z", "+00:00")),
        updated_at=datetime.fromisoformat(row["updated_at"].replace("Z", "+00:00")),
    )
