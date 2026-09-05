"""
Foundation API — Rahab (Reputation & Review Manager) Router
Cron-facing trigger endpoints + manual review-request kickoff.
"""
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.database import supabase
from app.rahab.ingestion import ingest_client_reviews, detect_spikes
from app.rahab import ghl_client

router = APIRouter(prefix="/rahab", tags=["rahab"])


def _client_context(client_id: str) -> dict:
    result = supabase.schema("foundation").table("client_profiles").select("*").eq("id", client_id).execute()
    if not result.data:
        raise HTTPException(404, f"client {client_id} not found")
    return result.data[0]


@router.post("/ingest/{client_id}")
def ingest(client_id: str, location_id: str = "", owner_first: str = "", business_phone: str = ""):
    """Triggered by the 2h Render cron, one call per client with reputation enabled."""
    client = _client_context(client_id)
    resolved_location = location_id or (client.get("metadata") or {}).get("ghl_location_id", "")
    return ingest_client_reviews(
        client_id=client_id,
        location_id=resolved_location,
        business_name=client["business_name"],
        owner_first=owner_first or client["business_name"].split()[0],
        business_phone=business_phone or client.get("contact_phone") or "",
    )


@router.post("/spike-check")
def spike_check():
    """Triggered by the nightly Render cron."""
    return {"spikes": detect_spikes()}


class ReviewRequestBody(BaseModel):
    client_id: str
    location_id: str
    contact_id: str
    workflow_id: str
    job_ref: Optional[str] = None


@router.post("/review-request")
def request_review(body: ReviewRequestBody):
    """Fires the GHL review-request workflow (SMS then email at +24h, per Rahab's
    prompt) and logs it. FTC-clean: called for every completed job, never filtered
    to happy customers only."""
    result = ghl_client.trigger_review_request(body.location_id, body.contact_id, body.workflow_id)
    row = supabase.schema("foundation").table("rr_review_requests").insert({
        "client_id": body.client_id,
        "customer_contact_id": body.contact_id,
        "job_ref": body.job_ref,
        "sms_sent_at": datetime.now(timezone.utc).isoformat() if result.get("ok") else None,
    }).execute()
    return {"ghl_result": result, "row": row.data[0] if row.data else None}
