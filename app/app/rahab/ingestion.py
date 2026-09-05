"""
Review ingestion + draft pipeline. Called by the Render cron
'rahab-review-ingestion' (every 2h business hours, see render.yaml);
also callable directly for tests/dry-runs — that's the shape the fake-
review VERIFY step exercises.
"""
import logging
from typing import Optional

from app.database import supabase
from app.action_library.executor import create_action
from app.rahab.draft import draft_review_response
from app.rahab import ghl_client

logger = logging.getLogger(__name__)

_LEGAL_FLAGS = ("lawsuit", "sue ", "sued", "discrimina", "racist", "assault", "unsafe", "injur", "lawyer", "attorney")


def ingest_client_reviews(
    client_id: str, location_id: str, business_name: str, owner_first: str, business_phone: str,
) -> dict:
    """Pulls reviews from GHL for one client, upserts new ones, drafts + queues an
    approval-inbox action for each. Real GHL call only happens if GHL_API_KEY is set."""
    raw_reviews = ghl_client.fetch_reviews(location_id)
    drafted = 0
    for raw in raw_reviews:
        row = _upsert_review(client_id, raw)
        if row is not None:
            process_new_review(row, business_name, owner_first, business_phone, location_id)
            drafted += 1
    return {"fetched": len(raw_reviews), "drafted": drafted}


def process_new_review(
    review_row: dict, business_name: str, owner_first: str, business_phone: str, location_id: str,
) -> dict:
    """Drafts a response for one rr_reviews row already in status='new' and queues
    it as a pending agent_actions row (or escalates it, for legal-flavored text)."""
    review_text = review_row.get("review_text") or ""

    if _is_legal_flavored(review_text):
        updated = supabase.schema("foundation").table("rr_reviews").update({
            "status": "escalated",
            "escalation_reason": "legal/discrimination/safety language detected — routed to owner + Peter, no public draft",
        }).eq("id", review_row["id"]).execute()
        return updated.data[0]

    rating = review_row.get("rating") or 0
    response_text = draft_review_response(
        review_text=review_text, rating=rating, reviewer_name=review_row.get("reviewer_name"),
        business_name=business_name, owner_first=owner_first, business_phone=business_phone,
    )

    action = create_action(
        action_type="post_review_response",
        draft={"response_text": response_text, "rating": rating, "review_text": review_text},
        payload={
            "review_id": review_row["id"],
            "location_id": location_id,
            "platform": review_row["platform"],
            "external_review_id": review_row.get("external_review_id"),
        },
        agent_id="rahab-reputation",
        client_id=review_row["client_id"],
        requested_by="cron",
    )

    updated = supabase.schema("foundation").table("rr_reviews").update({
        "status": "draft_ready", "draft_response": response_text, "action_id": action["id"],
    }).eq("id", review_row["id"]).execute()
    return updated.data[0]


def _upsert_review(client_id: str, raw: dict) -> Optional[dict]:
    """Inserts the review if not already ingested. Returns the new row, or None if
    it already exists (idempotent re-ingestion — the 2h cron will see the same
    reviews repeatedly until they age out of the GHL API's recent-reviews window)."""
    existing = (
        supabase.schema("foundation").table("rr_reviews")
        .select("id").eq("client_id", client_id)
        .eq("platform", "google").eq("external_review_id", raw.get("id"))
        .execute()
    )
    if existing.data:
        return None
    inserted = supabase.schema("foundation").table("rr_reviews").insert({
        "client_id": client_id, "platform": "google",
        "external_review_id": raw.get("id"), "reviewer_name": raw.get("reviewerName"),
        "rating": raw.get("rating"), "review_text": raw.get("text"),
        "reviewed_at": raw.get("createDate"), "status": "new",
    }).execute()
    return inserted.data[0]


def _is_legal_flavored(text: str) -> bool:
    t = (text or "").lower()
    return any(flag in t for flag in _LEGAL_FLAGS)


def detect_spikes(negative_threshold: int = 3, window_hours: int = 72) -> list[dict]:
    """Nightly spike detection: clients with >= negative_threshold reviews rated
    <=2 stars, detected within the last window_hours. Returns one summary dict
    per client with a spike — caller (cron) is responsible for alerting the owner."""
    from datetime import datetime, timedelta, timezone

    cutoff = (datetime.now(timezone.utc) - timedelta(hours=window_hours)).isoformat()
    rows = (
        supabase.schema("foundation").table("rr_reviews")
        .select("client_id,rating,detected_at,reviewer_name")
        .lte("rating", 2).gte("detected_at", cutoff)
        .execute().data
    )
    by_client: dict[str, list[dict]] = {}
    for r in rows:
        by_client.setdefault(r["client_id"], []).append(r)

    spikes = []
    for client_id, reviews in by_client.items():
        if len(reviews) >= negative_threshold:
            spikes.append({
                "client_id": client_id,
                "count": len(reviews),
                "window_hours": window_hours,
                "reviewers": [r.get("reviewer_name") for r in reviews],
            })
    return spikes
