"""
Foundation Layer · voice_edit · models.py

Pydantic models for every request, response, and internal data structure
in the voice-edit pipeline. Keep these in sync with the SQL migration
and editable_fields.yaml.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict


# ---------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------

class EditSource(str, Enum):
    VOICE  = "voice"
    TEXT   = "text"
    UPLOAD = "upload"
    UNDO   = "undo"
    SYSTEM = "system"


class SessionStatus(str, Enum):
    ACTIVE    = "active"
    PAUSED    = "paused"
    EXPIRED   = "expired"
    COMPLETED = "completed"


class ChannelType(str, Enum):
    VOICE = "voice"
    WEB   = "web"


# ---------------------------------------------------------------------
# JSON Patch — RFC 6902 subset we actually use
# ---------------------------------------------------------------------

class JsonPatchOp(BaseModel):
    """
    Single JSON Patch operation. We support add/replace/remove/copy/move
    plus a custom 'append' op for list[T] fields (cleaner UX than
    knowing the next index).
    """
    op:    Literal["add", "replace", "remove", "copy", "move", "append"]
    path:  str = Field(..., description="JSON Pointer, e.g. /hero/headline")
    value: Any | None = None
    from_: str | None = Field(None, alias="from")

    model_config = ConfigDict(populate_by_name=True)


# ---------------------------------------------------------------------
# Intent parser output
# ---------------------------------------------------------------------

class ParsedIntent(BaseModel):
    """
    What intent_parser.py returns. Either a confident patch or a
    clarifying question — never both.
    """
    confident: bool

    # If confident: the operations to apply
    patch: list[JsonPatchOp] = Field(default_factory=list)
    confidence: float = Field(0.0, ge=0.0, le=1.0)
    explanation: str | None = None     # human-readable summary for read-back

    # If not confident: ask the customer
    clarifying_question: str | None = None
    candidates: list[dict[str, Any]] = Field(default_factory=list)
    # candidates is a small list like:
    # [{"label":"Hero headline","path":"/hero/headline"},
    #  {"label":"Page title (browser tab)","path":"/meta/title"}]

    # Always returned
    requires_confirmation: bool = False
    affected_fields: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------
# Session
# ---------------------------------------------------------------------

class SessionChannel(BaseModel):
    type: ChannelType
    vapi_call_id: str | None = None
    client_id: str | None = None      # browser tab / device id
    attached_at: datetime


class EditSession(BaseModel):
    id: UUID
    business_id: UUID
    surface_id: str
    channels: list[SessionChannel] = Field(default_factory=list)
    status: SessionStatus
    pending_edit: dict[str, Any] | None = None
    last_activity_at: datetime
    expires_at: datetime
    handoff_token: str | None = None
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------------
# Request / response envelopes
# ---------------------------------------------------------------------

class CreateSessionRequest(BaseModel):
    business_id: UUID
    surface_id: str
    channel: SessionChannel
    expires_in_minutes: int = 60 * 24    # 24h default


class CreateSessionResponse(BaseModel):
    session: EditSession
    handoff_url: str | None = None       # link customer can open in browser


class VoiceEditRequest(BaseModel):
    transcript: str
    locale: str = "en-US"
    # Optional context to help the parser disambiguate
    last_visible_section: str | None = None     # what they were looking at on screen


class TextEditRequest(BaseModel):
    """Direct typed/form edit — bypasses intent parsing."""
    patch: list[JsonPatchOp]
    actor: Literal["customer", "agent"] = "customer"


class UploadRequest(BaseModel):
    filename: str
    mime_type: str
    size_bytes: int
    surface_field_hint: str | None = None    # e.g. user dropped on a logo slot
    user_provided_label: str | None = None


class UploadPresignedResponse(BaseModel):
    asset_id: UUID
    upload_url: str           # supabase storage signed URL
    storage_path: str         # e.g. business/{id}/logo-2026-04-29.png
    expires_at: datetime
    detected_kind: str | None = None  # filled after classification on /complete


class ConfirmRequest(BaseModel):
    pending_edit_id: UUID
    confirmed: bool


class UndoRequest(BaseModel):
    """If event_id omitted, undo most recent reversible event."""
    event_id: UUID | None = None


# ---------------------------------------------------------------------
# Standard response envelope
# ---------------------------------------------------------------------

class EditEventSummary(BaseModel):
    id: UUID
    source: EditSource
    transcript: str | None
    affected_fields: list[str]
    state_after_summary: str | None     # one-line "your headline now reads X"
    requires_confirmation: bool
    pending: bool                       # True iff awaiting confirmation
    created_at: datetime


class VoiceEditResponse(BaseModel):
    """
    Returned to the caller (VAPI agent or web client). Voice agent
    speaks `agent_should_say` verbatim.
    """
    success: bool
    event: EditEventSummary | None = None

    # What the voice agent should say next
    agent_should_say: str

    # If parser was unsure
    clarifying_question: str | None = None
    candidates: list[dict[str, Any]] = Field(default_factory=list)

    # If applied: snapshot for the frontend to optimistically render
    state_diff: dict[str, Any] | None = None


# ---------------------------------------------------------------------
# Surface schema (what the frontend asks for to render the form)
# ---------------------------------------------------------------------

class FieldDef(BaseModel):
    path: str
    aliases: list[str]
    type: str
    confirm: bool
    max_length: int | None = None
    enum_values: list[str] | None = None
    validator: str | None = None
    post_hook: str | None = None


class SurfaceSchema(BaseModel):
    id: str
    display_name: str
    product: str
    schema_version: int
    fields: dict[str, FieldDef]
