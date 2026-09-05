"""
Switchboard API — Phase 1 (SWITCHBOARD_BUILD.md §3.2, §5 rollout P1).

Ships this phase: auth exchange, bootstrap, thread history, sending a
message (sync reply -- no SSE/stream yet, see EMBED_GUIDE note), pins.
Deliberately NOT in this phase (flagged, not silently skipped): the
WS/SSE /switchboard/events presence-push channel, the VAPI call endpoint,
and the action-library-driven proactive DM pipeline -- all P2/P3 per the
spec's own rollout table.

Every endpoint below (except /auth/exchange, which is how you GET a
Switchboard token in the first place) depends on require_switchboard_auth
and filters every query by the verified workspace_id/user_id from that
token -- never by a client-supplied parameter (Addendum C.7).
"""
import logging
import os
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from app.database import supabase
from app.switchboard.auth import (
    SwitchboardAuthError, mint_switchboard_jwt, require_switchboard_auth,
    resolve_workspace, verify_host_token,
)
from app.switchboard.composer import generate_reply
from app.switchboard.entitlements import get_entitlement_mask

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/switchboard", tags=["switchboard"])

_WIDGET_JS_PATH = os.path.join(os.path.dirname(__file__), "..", "static", "switchboard", "v1.js")


@router.get("/v1.js")
def widget_bundle():
    return FileResponse(_WIDGET_JS_PATH, media_type="application/javascript")


class ExchangeRequest(BaseModel):
    access_token: str
    host: str = "an"


class ExchangeResponse(BaseModel):
    token: str
    workspace_id: str
    role: str
    expires_in: int


@router.post("/auth/exchange", response_model=ExchangeResponse)
async def exchange_auth(body: ExchangeRequest):
    try:
        identity = await verify_host_token(body.access_token, host=body.host)
        membership = resolve_workspace(identity["user_id"], identity.get("email"))
        token = mint_switchboard_jwt(identity["user_id"], membership["workspace_id"], membership["role"])
    except SwitchboardAuthError as e:
        raise HTTPException(e.status, e.detail)
    from app.switchboard.auth import SWITCHBOARD_JWT_TTL_SECONDS
    return ExchangeResponse(
        token=token, workspace_id=membership["workspace_id"],
        role=membership["role"], expires_in=SWITCHBOARD_JWT_TTL_SECONDS,
    )


@router.get("/bootstrap")
def bootstrap(claims: dict = Depends(require_switchboard_auth)):
    workspace_id, user_id = claims["workspace_id"], claims["user_id"]

    agents = (
        supabase.schema("foundation").table("ai_employees")
        .select("id,biblical_name,role,department,department_label,color,bg")
        .eq("is_active", True).execute().data
    )
    entitlements = get_entitlement_mask(workspace_id)

    pins = (
        supabase.schema("foundation").table("sb_pins")
        .select("agent_slug,sort_order").eq("client_id", workspace_id).eq("user_id", user_id)
        .order("sort_order").execute().data
    )
    threads = (
        supabase.schema("foundation").table("sb_threads")
        .select("agent_slug,unread_count,last_message_at")
        .eq("client_id", workspace_id).eq("user_id", user_id).execute().data
    )
    unread_by_agent = {t["agent_slug"]: t["unread_count"] for t in threads}

    settings_row = (
        supabase.schema("foundation").table("sb_settings")
        .select("*").eq("client_id", workspace_id).eq("user_id", user_id).execute().data
    )
    settings = settings_row[0] if settings_row else {
        "corner": "bottom-left", "hidden": False, "default_agent": None,
        "bubble_color": "#B4672B", "lang": "en", "voice_id": None,
    }

    return {
        "workspace_id": workspace_id,
        "roster": [
            {**a, "unlocked": entitlements.get(a["id"], False), "unread": unread_by_agent.get(a["id"], 0)}
            for a in agents
        ],
        "pins": pins,
        "settings": settings,
        "total_unread": sum(unread_by_agent.values()),
    }


def _get_or_create_thread(workspace_id: str, user_id: str, agent_slug: str) -> dict:
    existing = (
        supabase.schema("foundation").table("sb_threads")
        .select("*").eq("client_id", workspace_id).eq("user_id", user_id).eq("agent_slug", agent_slug)
        .execute().data
    )
    if existing:
        return existing[0]
    row = {"client_id": workspace_id, "user_id": user_id, "agent_slug": agent_slug}
    return supabase.schema("foundation").table("sb_threads").insert(row).execute().data[0]


@router.get("/threads/{agent_slug}")
def get_thread(agent_slug: str, limit: int = 50, claims: dict = Depends(require_switchboard_auth)):
    workspace_id, user_id = claims["workspace_id"], claims["user_id"]
    if not get_entitlement_mask(workspace_id).get(agent_slug, False):
        raise HTTPException(403, "this agent is not unlocked for your workspace")
    thread = _get_or_create_thread(workspace_id, user_id, agent_slug)
    messages = (
        supabase.schema("foundation").table("sb_messages")
        .select("*").eq("thread_id", thread["id"]).order("created_at", desc=True).limit(limit).execute().data
    )
    messages.reverse()
    if thread.get("unread_count"):
        supabase.schema("foundation").table("sb_threads").update({"unread_count": 0}).eq("id", thread["id"]).execute()
    return {"thread": thread, "messages": messages}


class SendMessageRequest(BaseModel):
    text: str


@router.post("/threads/{agent_slug}/messages")
def send_message(agent_slug: str, body: SendMessageRequest, claims: dict = Depends(require_switchboard_auth)):
    workspace_id, user_id = claims["workspace_id"], claims["user_id"]
    if not get_entitlement_mask(workspace_id).get(agent_slug, False):
        raise HTTPException(403, "this agent is not unlocked for your workspace")

    agent = supabase.schema("foundation").table("ai_employees").select("*").eq("id", agent_slug).execute().data
    if not agent:
        raise HTTPException(404, "unknown agent")
    agent = agent[0]

    thread = _get_or_create_thread(workspace_id, user_id, agent_slug)
    history = (
        supabase.schema("foundation").table("sb_messages")
        .select("sender,body").eq("thread_id", thread["id"]).order("created_at", desc=True).limit(30).execute().data
    )
    history.reverse()

    supabase.schema("foundation").table("sb_messages").insert(
        {"thread_id": thread["id"], "sender": "user", "kind": "text", "body": body.text}
    ).execute()

    try:
        reply_text = generate_reply(agent, thread, history, body.text)
    except Exception as e:
        logger.exception("switchboard reply generation failed for agent=%s thread=%s", agent_slug, thread["id"])
        reply_text = "Sorry -- I hit an error generating a reply. Try again in a moment."

    reply_row = supabase.schema("foundation").table("sb_messages").insert(
        {"thread_id": thread["id"], "sender": "agent", "kind": "text", "body": reply_text}
    ).execute().data[0]

    from datetime import datetime, timezone
    supabase.schema("foundation").table("sb_threads").update(
        {"last_message_at": datetime.now(timezone.utc).isoformat()}
    ).eq("id", thread["id"]).execute()

    return {"reply": reply_row}


class PinRequest(BaseModel):
    agent_slug: str
    action: str  # "add" | "remove"
    sort_order: Optional[int] = 0


@router.post("/pins")
def set_pin(body: PinRequest, claims: dict = Depends(require_switchboard_auth)):
    workspace_id, user_id = claims["workspace_id"], claims["user_id"]
    if body.action == "add":
        supabase.schema("foundation").table("sb_pins").upsert(
            {"client_id": workspace_id, "user_id": user_id, "agent_slug": body.agent_slug, "sort_order": body.sort_order}
        ).execute()
    elif body.action == "remove":
        supabase.schema("foundation").table("sb_pins").delete().eq("client_id", workspace_id).eq(
            "user_id", user_id
        ).eq("agent_slug", body.agent_slug).execute()
    else:
        raise HTTPException(400, "action must be 'add' or 'remove'")
    return {"ok": True}
