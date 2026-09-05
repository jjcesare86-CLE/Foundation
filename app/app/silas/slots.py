"""Python wrapper around the atomic foundation.claim_slot() Postgres function."""
from app.database import supabase


def claim_slot(offer_id: str, contact_id: str) -> dict:
    result = supabase.schema("foundation").rpc(
        "claim_slot", {"p_offer_id": offer_id, "p_contact_id": contact_id}
    ).execute()
    row = result.data[0] if result.data else {"claimed": False, "offer_id": offer_id}
    return row
