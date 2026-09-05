"""
Minimal GHL (GoHighLevel) client for Rahab's reviews/reputation surface.

NOTE: endpoint paths below follow GHL's v2 REST conventions
(services.leadconnectorhq.com, Version header, Bearer auth) but haven't
been exercised against a real GHL account in this build — no GHL_API_KEY
was available. Verify against current GHL API docs before the first real
client connection; the shapes here are best-effort, not confirmed.

Every function is safe to call with no key configured: fetch_reviews()
returns [] and the *_response()/trigger_*() calls fail soft with
{"ok": False}. Callers that need to distinguish "not configured" from "a
credential-only cred exists" should check GHL_API_KEY themselves — the
action library's demo-mode gate already does this before a handler ever
gets here in the live-call path.
"""
import os
import httpx

GHL_API_KEY = os.getenv("GHL_API_KEY", "")
GHL_BASE = "https://services.leadconnectorhq.com"


def _headers() -> dict:
    return {"Authorization": f"Bearer {GHL_API_KEY}", "Version": "2021-07-28"}


def fetch_reviews(location_id: str) -> list[dict]:
    """Pull reviews for a GHL sub-account. Returns [] if not configured or on any error."""
    if not GHL_API_KEY or not location_id:
        return []
    try:
        resp = httpx.get(f"{GHL_BASE}/locations/{location_id}/reviews", headers=_headers(), timeout=30)
        resp.raise_for_status()
        return resp.json().get("reviews", [])
    except Exception:
        return []


def publish_review_response(location_id: str, external_review_id: str, response_text: str) -> dict:
    """Post a reply to a live review. Fail-soft: never raises."""
    try:
        resp = httpx.post(
            f"{GHL_BASE}/locations/{location_id}/reviews/{external_review_id}/reply",
            headers=_headers(), json={"reply": response_text}, timeout=30,
        )
        resp.raise_for_status()
        return {"ok": True, "external_id": external_review_id}
    except Exception as e:
        return {"ok": False, "detail": str(e)}


def trigger_review_request(location_id: str, contact_id: str, workflow_id: str) -> dict:
    """Fires the GHL workflow that sends the review-request SMS/email sequence."""
    try:
        resp = httpx.post(
            f"{GHL_BASE}/contacts/{contact_id}/workflow/{workflow_id}",
            headers=_headers(), json={"locationId": location_id}, timeout=30,
        )
        resp.raise_for_status()
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "detail": str(e)}
