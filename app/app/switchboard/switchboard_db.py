"""
Second database client: the dedicated Switchboard Supabase project
(docs/specs/SWITCHBOARD_ADDENDUM_F_SEPARATE_DATABASE.md, F.3/F.5/F.6).

Foundation's own client (app.database.supabase) is never reused for
Switchboard data in `switchboard` mode, and no value from the Foundation
project (URL, service key, anon key) may equal its Switchboard counterpart.
validate_config() runs at import time from app.main and refuses to boot on
any violation. Nothing here ever logs or returns a key.
"""
import os
import time
from typing import Optional

import jwt
from supabase import Client, create_client

FOUNDATION_REF = "rhtwtoinmiekttvunlzs"
AN_REF = "rzsryxvlaezfvftqpvbx"
VALID_MODES = ("foundation", "switchboard")
SWITCHBOARD_DB_JWT_TTL_SECONDS = 60 * 60


class SwitchboardConfigError(RuntimeError):
    pass


def _norm_url(u: Optional[str]) -> str:
    return (u or "").strip().rstrip("/").lower()


def db_mode() -> str:
    mode = os.getenv("SWITCHBOARD_DB_MODE", "foundation").strip().lower() or "foundation"
    if mode not in VALID_MODES:
        raise SwitchboardConfigError(f"SWITCHBOARD_DB_MODE must be one of {VALID_MODES}")
    return mode


def is_configured() -> bool:
    return bool(os.getenv("SWITCHBOARD_SUPABASE_URL") and os.getenv("SWITCHBOARD_SUPABASE_SERVICE_ROLE_KEY"))


def validate_config() -> None:
    """Startup guard. Raises SwitchboardConfigError (so the API refuses to boot)
    if the two Supabase configurations are mixed up. Unset SWITCHBOARD_* vars are
    fine in `foundation` mode (the default) so a deploy without them still boots."""
    mode = db_mode()
    sb_url = _norm_url(os.getenv("SWITCHBOARD_SUPABASE_URL"))
    sb_service = os.getenv("SWITCHBOARD_SUPABASE_SERVICE_ROLE_KEY")
    sb_anon = os.getenv("SWITCHBOARD_SUPABASE_ANON_KEY")
    sb_jwt = os.getenv("SWITCHBOARD_SUPABASE_JWT_SECRET")
    ref = os.getenv("SWITCHBOARD_PROJECT_REF")

    if mode == "switchboard":
        missing = [n for n, v in (
            ("SWITCHBOARD_SUPABASE_URL", sb_url),
            ("SWITCHBOARD_SUPABASE_SERVICE_ROLE_KEY", sb_service),
            ("SWITCHBOARD_SUPABASE_JWT_SECRET", sb_jwt),
        ) if not v]
        if missing:
            raise SwitchboardConfigError(f"SWITCHBOARD_DB_MODE=switchboard but missing: {', '.join(missing)}")

    if not sb_url and not sb_service:
        return  # foundation mode, nothing configured

    if sb_url and sb_url == _norm_url(os.getenv("SUPABASE_URL")):
        raise SwitchboardConfigError("SWITCHBOARD_SUPABASE_URL equals SUPABASE_URL: refusing to start")
    for forbidden in (FOUNDATION_REF, AN_REF):
        if sb_url and forbidden in sb_url:
            raise SwitchboardConfigError("SWITCHBOARD_SUPABASE_URL points at a non-Switchboard project: refusing to start")
    if ref and sb_url and ref.lower() not in sb_url:
        raise SwitchboardConfigError("SWITCHBOARD_PROJECT_REF does not match SWITCHBOARD_SUPABASE_URL: refusing to start")
    if sb_service and sb_service == os.getenv("SUPABASE_SERVICE_ROLE_KEY"):
        raise SwitchboardConfigError("Switchboard service key equals Foundation service key: refusing to start")
    if sb_anon and sb_anon == os.getenv("SUPABASE_ANON_KEY"):
        raise SwitchboardConfigError("Switchboard anon key equals Foundation anon key: refusing to start")
    if sb_jwt and sb_jwt in (os.getenv("SWITCHBOARD_JWT_SECRET"), os.getenv("SUPABASE_JWT_SECRET")):
        raise SwitchboardConfigError("SWITCHBOARD_SUPABASE_JWT_SECRET must not reuse another JWT secret (F.9.7): refusing to start")


_client: Optional[Client] = None


def client() -> Client:
    """Service-role client for the Switchboard project (server-side only)."""
    global _client
    if not is_configured():
        raise SwitchboardConfigError("Switchboard database is not configured on the server")
    if _client is None:
        _client = create_client(
            os.environ["SWITCHBOARD_SUPABASE_URL"], os.environ["SWITCHBOARD_SUPABASE_SERVICE_ROLE_KEY"]
        )
    return _client


def mint_workspace_jwt(user_id: str, workspace_id: str, sb_role: str) -> str:
    """Short-lived token the widget uses against the Switchboard project directly
    (Realtime reads under RLS). Signed with the Switchboard project's secret.
    `role` must be 'authenticated' (PostgREST maps it to the DB role); the
    membership role travels in `sb_role`. Never accepted by the Foundation API."""
    secret = os.getenv("SWITCHBOARD_SUPABASE_JWT_SECRET")
    if not secret:
        raise SwitchboardConfigError("Switchboard JWT signing is not configured on the server")
    now = int(time.time())
    return jwt.encode(
        {
            "aud": "authenticated", "role": "authenticated", "sub": user_id,
            "user_id": user_id, "workspace_id": workspace_id, "sb_role": sb_role,
            "iat": now, "exp": now + SWITCHBOARD_DB_JWT_TTL_SECONDS,
        },
        secret, algorithm="HS256",
    )
