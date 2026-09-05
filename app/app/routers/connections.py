"""
Foundation API — Connections Hub Router.

/connections/callback/{provider} is deliberately left UNGATED in main.py
(OAuth callbacks need to reach it with no API key) -- everything else
here requires require_api_key today. That's a real gap, not a final
design: the AN client dashboard has no client-facing auth/JWT of its own
yet, so there's nothing to gate these on besides the internal key, which
must never reach a browser. Until AN has a client session token, these
non-callback endpoints should be called server-side from AN's own backend
(an-sales-pipeline), not directly from the browser -- noted in the
completion report, not silently solved here.
"""
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from app.database import supabase
from app.services.connection_broker import encrypt_token
from app.connections import google_oauth

# Two router objects so main.py can gate one and leave the other public:
# `router` = the OAuth callback only (providers redirect the browser here
# directly, no API key on the request). `admin_router` = everything else,
# gated behind require_api_key in main.py.
router = APIRouter(prefix="/connections", tags=["connections"])
admin_router = APIRouter(prefix="/connections", tags=["connections"])

# In-memory state-nonce store. Fine for a single-instance deploy; move to
# a table if foundation-api ever runs >1 instance (nonces would need to
# survive a request landing on a different instance than initiate did).
_pending_states: dict[str, dict] = {}

CARD_COPY = {
    ("google", "gmail"): "Let Esther send emails from your address",
    ("google", "calendar"): "Let Naomi book appointments on your calendar",
    ("ghl_social", None): "Let Nathan post and reply for you",
    ("stripe", None): "Let Joanna send invoices and take payments",
}


@admin_router.get("/{client_id}")
def list_connections(client_id: str):
    """Card states for the hub. Never returns a token, encrypted or not."""
    rows = supabase.schema("foundation").table("client_connections").select(
        "id,provider,provider_scope,external_account_id,display_name,status,token_expires_at,last_verified_at,error_detail"
    ).eq("client_id", client_id).execute().data
    return {"client_id": client_id, "connections": rows}


class InitiateRequest(BaseModel):
    client_id: str
    provider_scope: Optional[str] = None  # e.g. "gmail" | "calendar", provider-specific


@admin_router.post("/{provider}/initiate")
def initiate(provider: str, body: InitiateRequest):
    if provider != "google":
        raise HTTPException(400, f"provider {provider!r} doesn't use direct OAuth in v1 (GHL handles social, Stripe uses Connect onboarding)")
    if not body.provider_scope:
        raise HTTPException(400, "provider_scope required for google (gmail | calendar)")

    state = google_oauth.new_state_nonce()
    _pending_states[state] = {"client_id": body.client_id, "provider_scope": body.provider_scope, "created_at": datetime.now(timezone.utc)}

    try:
        url = google_oauth.build_authorize_url(body.provider_scope, state)
    except RuntimeError as e:
        raise HTTPException(503, str(e))
    return {"authorize_url": url}


@router.get("/callback/{provider}", response_class=HTMLResponse)
def callback(provider: str, code: str = "", state: str = "", error: str = ""):
    """Token exchange, encrypt, store, close the popup. Public — OAuth
    providers redirect the user's browser here directly, no API key on
    the request."""
    pending = _pending_states.pop(state, None)
    if error or not pending:
        detail = error or "unknown or expired state"
        return _popup_close_html(ok=False, detail=detail)

    if provider != "google":
        return _popup_close_html(ok=False, detail=f"provider {provider!r} not supported")

    try:
        tokens = google_oauth.exchange_code_for_tokens(code)
    except Exception as e:
        return _popup_close_html(ok=False, detail=str(e))

    client_id = pending["client_id"]
    provider_scope = pending["provider_scope"]
    expires_at = (datetime.now(timezone.utc).timestamp() + tokens.get("expires_in", 3600))

    row = {
        "client_id": client_id,
        "provider": "google",
        "provider_scope": provider_scope,
        "status": "active",
        "access_token_encrypted": encrypt_token(tokens["access_token"]),
        "token_expires_at": datetime.fromtimestamp(expires_at, tz=timezone.utc).isoformat(),
        "last_verified_at": datetime.now(timezone.utc).isoformat(),
        "error_detail": None,
    }
    if tokens.get("refresh_token"):
        row["refresh_token_encrypted"] = encrypt_token(tokens["refresh_token"])

    supabase.schema("foundation").table("client_connections").upsert(
        row, on_conflict="client_id,provider,provider_scope,external_account_id"
    ).execute()

    return _popup_close_html(ok=True, detail=f"google/{provider_scope} connected")


def _popup_close_html(ok: bool, detail: str) -> str:
    # Posts a message to the opener and closes itself -- the hub page
    # listens for this and lights the checkmark without a page reload.
    return f"""<!doctype html><html><body>
<script>
  if (window.opener) {{
    window.opener.postMessage({{ type: 'connections_hub_result', ok: {str(ok).lower()}, detail: {detail!r} }}, '*');
  }}
  window.close();
</script>
<p>{"Connected." if ok else "Something went wrong: " + detail} You can close this window.</p>
</body></html>"""


@admin_router.post("/{connection_id}/disconnect")
def disconnect(connection_id: str):
    result = supabase.schema("foundation").table("client_connections").update({
        "status": "revoked", "access_token_encrypted": None, "refresh_token_encrypted": None,
    }).eq("id", connection_id).execute()
    if not result.data:
        raise HTTPException(404, f"connection {connection_id} not found")
    return result.data[0]


@admin_router.post("/{connection_id}/verify")
def verify(connection_id: str):
    """Live token health check -- used by the nightly cron, also callable
    on demand. For google connections, tries a refresh (the cheapest real
    signal a token is still good); other providers have no live check
    implemented yet, so they're left at their current status."""
    row = supabase.schema("foundation").table("client_connections").select("*").eq("id", connection_id).execute().data
    if not row:
        raise HTTPException(404, f"connection {connection_id} not found")
    row = row[0]

    if row["provider"] != "google" or not row.get("refresh_token_encrypted"):
        return {"connection_id": connection_id, "checked": False, "reason": "no live check implemented for this provider yet"}

    from app.services.connection_broker import decrypt_token
    try:
        fresh = google_oauth.refresh_access_token(decrypt_token(row["refresh_token_encrypted"]))
        supabase.schema("foundation").table("client_connections").update({
            "status": "active",
            "access_token_encrypted": encrypt_token(fresh["access_token"]),
            "last_verified_at": datetime.now(timezone.utc).isoformat(),
            "error_detail": None,
        }).eq("id", connection_id).execute()
        return {"connection_id": connection_id, "checked": True, "status": "active"}
    except Exception as e:
        supabase.schema("foundation").table("client_connections").update({
            "status": "expired", "error_detail": str(e),
        }).eq("id", connection_id).execute()
        return {"connection_id": connection_id, "checked": True, "status": "expired", "detail": str(e)}
