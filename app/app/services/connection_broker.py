"""
connection_broker — agent-facing access layer (Connections Hub Part 4).

Agents never read tokens directly. This module resolves a client's
connection, refreshes it if the access token is near expiry, executes the
call, and returns a result. If a required connection is missing or
revoked, callers get back the exact scripted line the spec wants agents
to say verbatim -- callers don't have to invent their own copy.
"""
from datetime import datetime, timedelta, timezone
from typing import Optional

from cryptography.fernet import Fernet
import os

_ENCRYPTION_KEY = os.getenv("CONNECTION_BROKER_ENCRYPTION_KEY")
if not _ENCRYPTION_KEY:
    raise RuntimeError("CONNECTION_BROKER_ENCRYPTION_KEY not set — refusing to start")

_fernet = Fernet(_ENCRYPTION_KEY.encode())


def encrypt_token(plaintext: str) -> str:
    """Encrypt a token for storage. Returns a URL-safe base64 string."""
    return _fernet.encrypt(plaintext.encode()).decode()


def decrypt_token(ciphertext: str) -> str:
    """Decrypt a stored token. Raises InvalidToken on bad key/data."""
    return _fernet.decrypt(ciphertext.encode()).decode()


class ConnectionNotFoundError(Exception):
    pass


class ConnectionRevokedError(Exception):
    pass


def _missing_connection_message(service_label: str) -> str:
    return f"I need access to your {service_label} first — tap Connect Your Accounts in your dashboard and I'm ready in 3 minutes."


def get_valid_token(client_id: str, provider: str, provider_scope: Optional[str] = None) -> str:
    """Returns a decrypted, refreshed-if-needed access token.
    Raises ConnectionNotFoundError / ConnectionRevokedError -- callers
    (send_email, create_event, post_social below) catch these and return
    the scripted missing-connection line rather than letting an agent
    fail with a raw exception."""
    from app.database import supabase

    query = (
        supabase.schema("foundation").table("client_connections")
        .select("*").eq("client_id", client_id).eq("provider", provider)
    )
    if provider_scope:
        query = query.eq("provider_scope", provider_scope)
    result = query.execute()
    if not result.data:
        raise ConnectionNotFoundError(f"no {provider}/{provider_scope} connection for client {client_id}")

    row = result.data[0]
    if row["status"] in ("revoked", "error"):
        raise ConnectionRevokedError(f"{provider}/{provider_scope} connection for client {client_id} is {row['status']}")

    access_token = decrypt_token(row["access_token_encrypted"]) if row.get("access_token_encrypted") else None

    expires_at = row.get("token_expires_at")
    needs_refresh = expires_at and datetime.fromisoformat(expires_at.replace("Z", "+00:00")) < datetime.now(timezone.utc) + timedelta(minutes=5)
    if needs_refresh and row.get("refresh_token_encrypted") and provider == "google":
        from app.connections.google_oauth import refresh_access_token
        refresh_token = decrypt_token(row["refresh_token_encrypted"])
        fresh = refresh_access_token(refresh_token)
        access_token = fresh["access_token"]
        new_expiry = (datetime.now(timezone.utc) + timedelta(seconds=fresh.get("expires_in", 3600))).isoformat()
        supabase.schema("foundation").table("client_connections").update({
            "access_token_encrypted": encrypt_token(access_token),
            "token_expires_at": new_expiry,
            "last_refreshed_at": datetime.now(timezone.utc).isoformat(),
        }).eq("id", row["id"]).execute()

    if not access_token:
        raise ConnectionNotFoundError(f"{provider}/{provider_scope} connection for client {client_id} has no usable token")
    return access_token


def send_email(client_id: str, to: str, subject: str, body: str) -> dict:
    try:
        token = get_valid_token(client_id, "google", "gmail")
    except (ConnectionNotFoundError, ConnectionRevokedError):
        return {"ok": False, "missing_connection": "gmail", "message": _missing_connection_message("Gmail")}
    # TODO: real Gmail API send (gmail.users.messages.send) once a real
    # GOOGLE_OAUTH_CLIENT_ID/SECRET exists to actually mint `token` from —
    # the token-resolution path above is real, this call is not yet.
    return {"ok": False, "detail": "Gmail send not implemented yet — token resolution works, the send call is a TODO"}


def create_event(client_id: str, summary: str, start: str, end: str, attendees: Optional[list] = None) -> dict:
    try:
        token = get_valid_token(client_id, "google", "calendar")
    except (ConnectionNotFoundError, ConnectionRevokedError):
        return {"ok": False, "missing_connection": "calendar", "message": _missing_connection_message("Calendar")}
    # TODO: real Calendar API insert, same caveat as send_email above.
    return {"ok": False, "detail": "Calendar event creation not implemented yet — token resolution works, the call is a TODO"}


def post_social(client_id: str, platform: str, content: str) -> dict:
    """Social goes through GHL (architecture decision: Option A), not a
    direct per-platform OAuth token -- so this checks for a ghl_social
    connection row (proves the client's GHL subaccount is linked) rather
    than resolving a Meta/TikTok/LinkedIn token directly."""
    try:
        get_valid_token(client_id, "ghl_social")
    except (ConnectionNotFoundError, ConnectionRevokedError):
        return {"ok": False, "missing_connection": platform, "message": _missing_connection_message(platform.title())}
    return {"ok": False, "detail": "social post via GHL not implemented yet — connection check works, the call is a TODO"}
