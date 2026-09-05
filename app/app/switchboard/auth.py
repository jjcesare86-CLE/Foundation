"""
Switchboard auth bridge.

Switchboard's host pages (AN dashboard, client staff dashboards) each have
their OWN Supabase Auth session, on THEIR OWN Supabase project — never
Foundation's. Foundation can't verify a token it didn't sign, and doesn't
hold the other project's JWT signing secret. Real, secure path with zero new
secrets required for the AN leg: forward the host's access token to that
project's own `GET /auth/v1/user` endpoint (the standard way to ask a
Supabase Auth server "is this token real, and whose is it" without holding
its signing key). If that project says the token is valid, we trust the
user_id and email it hands back — Supabase itself did the cryptographic
verification.

Once we know who the caller really is, we mint our OWN short-lived JWT
(HS256, SWITCHBOARD_JWT_SECRET) scoped to {user_id, workspace_id, role}.
That's the only token Switchboard's own endpoints accept — never the host
product's token directly, so Foundation never has to understand every host
product's auth internals at every call site, just once, here.
"""
import os
import time
from typing import Optional

import httpx
import jwt
from fastapi import Header, HTTPException

from app.database import supabase

SWITCHBOARD_JWT_SECRET = os.getenv("SWITCHBOARD_JWT_SECRET")
SWITCHBOARD_JWT_TTL_SECONDS = 60 * 60  # "short-lived" per spec §3.1

# Not secrets — Supabase anon/publishable keys are meant to be public
# (they're committed in AN-repo's own client-side source). Configurable via
# env for when a second host product (a different Supabase project) needs
# the same bridge; defaults are AN-repo's real, already-public values.
AN_SUPABASE_URL = os.getenv("AN_SUPABASE_URL", "https://rzsryxvlaezfvftqpvbx.supabase.co")
AN_SUPABASE_ANON_KEY = os.getenv(
    "AN_SUPABASE_ANON_KEY",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ6c3J5eHZsYWV6ZnZmdHFwdmJ4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTgzMjYzNjMsImV4cCI6MjA3MzkwMjM2M30.d5tNcaAgQctciR9c2xJxgs5gWgSQGC-7EK5Q5a19FaA",
)


class SwitchboardAuthError(Exception):
    def __init__(self, status: int, detail: str):
        self.status = status
        self.detail = detail


async def verify_host_token(access_token: str, host: str = "an") -> dict:
    """Ask the host product's OWN Supabase Auth server whose token this is.
    Never decodes/trusts the token locally — we don't hold that project's
    signing key, so the only honest verification is asking its issuer."""
    if host != "an":
        raise SwitchboardAuthError(400, f"unknown host product '{host}'")
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            resp = await client.get(
                f"{AN_SUPABASE_URL}/auth/v1/user",
                headers={"Authorization": f"Bearer {access_token}", "apikey": AN_SUPABASE_ANON_KEY},
            )
        except httpx.HTTPError as e:
            raise SwitchboardAuthError(502, f"could not reach host auth server: {e}")
    if resp.status_code != 200:
        raise SwitchboardAuthError(401, "host session token is invalid or expired")
    data = resp.json()
    if not data.get("id"):
        raise SwitchboardAuthError(401, "host auth server returned no user id")
    return {"user_id": data["id"], "email": data.get("email")}


def resolve_workspace(user_id: str, email: Optional[str]) -> dict:
    """Find (or, for a genuine first-time owner login, create) this user's
    workspace membership. No open self-serve discovery (Addendum C.3): the
    only auto-bootstrap path is an EXACT match between the verified email
    and an existing client_profiles.contact_email — the real business
    owner logging into their own already-provisioned account, not an open
    "find my company" flow. If no membership exists and no exact email
    match exists either, this is a real gap (most seeded client_profiles
    rows have no contact_email at all — flagged in DECISIONS.md, not
    silently papered over), and we say so rather than fabricate access."""
    existing = (
        supabase.schema("foundation").table("sb_memberships")
        .select("*").eq("user_id", user_id).is_("revoked_at", "null")
        .order("joined_at", desc=True).limit(1).execute().data
    )
    if existing:
        return existing[0]

    if email:
        match = (
            supabase.schema("foundation").table("client_profiles")
            .select("id").eq("contact_email", email).execute().data
        )
        if len(match) == 1:
            row = {"workspace_id": match[0]["id"], "user_id": user_id, "role": "owner"}
            supabase.schema("foundation").table("sb_memberships").insert(row).execute()
            return row

    raise SwitchboardAuthError(
        403,
        "no workspace membership found for this account, and no exact "
        "contact-email match to auto-provision one — ask a Foundation admin "
        "to add you to your workspace",
    )


def mint_switchboard_jwt(user_id: str, workspace_id: str, role: str) -> str:
    if not SWITCHBOARD_JWT_SECRET:
        raise SwitchboardAuthError(503, "Switchboard auth is not configured on the server")
    now = int(time.time())
    claims = {
        "user_id": user_id,
        "workspace_id": workspace_id,
        "role": role,
        "iat": now,
        "exp": now + SWITCHBOARD_JWT_TTL_SECONDS,
    }
    return jwt.encode(claims, SWITCHBOARD_JWT_SECRET, algorithm="HS256")


def verify_switchboard_jwt(token: str) -> dict:
    if not SWITCHBOARD_JWT_SECRET:
        raise SwitchboardAuthError(503, "Switchboard auth is not configured on the server")
    try:
        return jwt.decode(token, SWITCHBOARD_JWT_SECRET, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise SwitchboardAuthError(401, "Switchboard session expired — reconnect")
    except jwt.InvalidTokenError:
        raise SwitchboardAuthError(401, "invalid Switchboard session token")


async def require_switchboard_auth(authorization: Optional[str] = Header(None)) -> dict:
    """FastAPI dependency: every real Switchboard endpoint depends on this.
    Returns {user_id, workspace_id, role} — callers MUST filter every query
    by these, never by a client-supplied parameter (Addendum C.7: 'the
    parameter must not exist at all')."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(401, "missing Switchboard session token")
    token = authorization[len("Bearer "):]
    try:
        claims = verify_switchboard_jwt(token)
    except SwitchboardAuthError as e:
        raise HTTPException(e.status, e.detail)
    return claims
