"""
Google OAuth2 (authorization-code flow, offline access) for the
Connections Hub. A separate OAuth client from Blast Video's (per the
spec's own open item #2) -- Blast Video's signInWithOAuth is a bare
Supabase Auth sign-in with no scopes and no callback route; nothing there
was reusable beyond "yes, Google OAuth against this project works."

GOOGLE_OAUTH_CLIENT_ID / GOOGLE_OAUTH_CLIENT_SECRET are not set anywhere
in this environment (checked). Every function below raises a clear
RuntimeError rather than silently proceeding -- matching stripe_client.py
and weather.py's pattern from Batch 1. Google's app verification for the
gmail.send scope (sensitive) also hasn't been submitted yet per the
spec's own open item #2 -- that's a 1-2 week clock that starts the day a
real client ID exists, separate from just having the credentials.
"""
import os
import secrets
from typing import Optional
from urllib.parse import urlencode

import httpx

AUTHORIZE_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
SCOPES = {
    "gmail": "https://www.googleapis.com/auth/gmail.send",
    "calendar": "https://www.googleapis.com/auth/calendar.events",
}


def _client_id() -> str:
    v = os.getenv("GOOGLE_OAUTH_CLIENT_ID")
    if not v:
        raise RuntimeError("GOOGLE_OAUTH_CLIENT_ID not set -- Connections Hub's Google OAuth client hasn't been provisioned yet")
    return v


def _client_secret() -> str:
    v = os.getenv("GOOGLE_OAUTH_CLIENT_SECRET")
    if not v:
        raise RuntimeError("GOOGLE_OAUTH_CLIENT_SECRET not set -- Connections Hub's Google OAuth client hasn't been provisioned yet")
    return v


def _redirect_uri() -> str:
    base = os.getenv("FOUNDATION_API_BASE_URL", "https://foundation-api-9gpl.onrender.com")
    return f"{base}/connections/callback/google"


def build_authorize_url(provider_scope: str, state: str) -> str:
    """provider_scope: 'gmail' | 'calendar'. state must carry client_id +
    a nonce -- the callback verifies it before ever touching a token."""
    scope = SCOPES.get(provider_scope)
    if not scope:
        raise ValueError(f"unknown provider_scope {provider_scope!r} for Google, expected one of {list(SCOPES)}")
    params = {
        "client_id": _client_id(),
        "redirect_uri": _redirect_uri(),
        "response_type": "code",
        "scope": scope,
        "access_type": "offline",   # required for a refresh_token
        "prompt": "consent",        # forces refresh_token on every connect, not just the first
        "state": state,
    }
    return f"{AUTHORIZE_URL}?{urlencode(params)}"


def new_state_nonce() -> str:
    return secrets.token_urlsafe(32)


def exchange_code_for_tokens(code: str) -> dict:
    """Returns {"access_token", "refresh_token", "expires_in", "scope", ...} from Google.
    Never call this with a client secret you haven't confirmed is real -- it will
    fail loudly (RuntimeError from _client_id/_client_secret) rather than send a
    request that's guaranteed to 401."""
    resp = httpx.post(TOKEN_URL, data={
        "code": code,
        "client_id": _client_id(),
        "client_secret": _client_secret(),
        "redirect_uri": _redirect_uri(),
        "grant_type": "authorization_code",
    }, timeout=30)
    resp.raise_for_status()
    return resp.json()


def refresh_access_token(refresh_token: str) -> dict:
    """Returns a fresh {"access_token", "expires_in", ...} -- Google doesn't
    reissue refresh_token on a refresh call, the original stays valid."""
    resp = httpx.post(TOKEN_URL, data={
        "refresh_token": refresh_token,
        "client_id": _client_id(),
        "client_secret": _client_secret(),
        "grant_type": "refresh_token",
    }, timeout=30)
    resp.raise_for_status()
    return resp.json()
