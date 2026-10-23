"""
PHP Shield -- optional Cloudflare Turnstile check, feature-flagged by TURNSTILE_SECRET.

Unset secret => skipped gracefully (honeypot + rate limits still apply).
Set secret    => /scan requires a valid `turnstile_token`; a Cloudflare outage
                 fails CLOSED (the request is rejected) because the secret being
                 set means the operator wants the challenge enforced.
"""
import os

import requests

VERIFY_URL = "https://challenges.cloudflare.com/turnstile/v0/siteverify"


def enabled() -> bool:
    return bool(os.getenv("TURNSTILE_SECRET", "").strip())


def verify(token: str | None, remote_ip: str | None = None, *, post=requests.post) -> bool:
    secret = os.getenv("TURNSTILE_SECRET", "").strip()
    if not secret:
        return True
    if not token:
        return False
    try:
        resp = post(VERIFY_URL, data={"secret": secret, "response": token, "remoteip": remote_ip or ""}, timeout=5)
        return bool(resp.json().get("success"))
    except Exception:
        return False
