"""Registers Rahab's action types with the shared action library."""
from app.action_library.registry import register_action_type
from app.database import supabase
from app.rahab import ghl_client


def _execute_post_review_response(draft: dict, payload: dict, demo: bool) -> dict:
    location_id = payload.get("location_id")
    external_review_id = payload.get("external_review_id")
    review_id = payload.get("review_id")
    response_text = draft.get("response_text", "")

    if demo:
        result = {"ok": True, "would_have": f"post a GHL review reply: {response_text[:120]!r}"}
    else:
        result = ghl_client.publish_review_response(location_id, external_review_id, response_text)

    if result.get("ok") and review_id:
        supabase.schema("foundation").table("rr_reviews").update({
            "status": "posted", "posted_response": response_text,
        }).eq("id", review_id).execute()

    return result


def register_rahab_actions() -> None:
    register_action_type("post_review_response", _execute_post_review_response, required_env=["GHL_API_KEY"])
