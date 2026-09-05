"""Foundation API — Zacchaeus (Tax & Bookkeeping) Router. Cron-facing triggers."""
from fastapi import APIRouter, HTTPException

from app.database import supabase
from app.zacchaeus.categorize import run_categorization_batch
from app.zacchaeus.deadlines import run_deadline_reminders, run_1099_sweep, run_anomaly_digest

router = APIRouter(prefix="/zacchaeus", tags=["zacchaeus"])


def _client_context(client_id: str) -> dict:
    result = supabase.schema("foundation").table("client_profiles").select("*").eq("id", client_id).execute()
    if not result.data:
        raise HTTPException(404, f"client {client_id} not found")
    return result.data[0]


@router.post("/categorize/{client_id}")
def categorize(client_id: str):
    client = _client_context(client_id)
    return run_categorization_batch(client_id, client["business_name"], client.get("industry") or "general")


@router.post("/daily-sweep")
def daily_sweep():
    """Triggered by the daily Render cron: deadline reminders + 1099 sweep."""
    return {
        "deadlines": run_deadline_reminders(),
        "contractors": run_1099_sweep(),
    }


@router.get("/anomalies")
def anomalies(client_id: str = ""):
    return run_anomaly_digest(client_id or None)
