"""
Render cron 'rahab-review-ingestion' — runs every 2h during business hours.
Iterates every client_profiles row with a GHL location id configured
(metadata->>'ghl_location_id') and runs the ingest pipeline for it.
No-ops cleanly (0 fetched) for any client without a location id configured
or without GHL_API_KEY set — never a silent crash, always a clear log line.
"""
import logging
import sys

sys.path.insert(0, ".")

from app.database import supabase
from app.rahab.ingestion import ingest_client_reviews
from app.ops.heartbeat import heartbeat

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("rahab_ingest_cron")

AGENT_SLUG, JOB_NAME = "rahab-reputation", "rahab-review-ingestion"


def main() -> None:
    try:
        clients = supabase.schema("foundation").table("client_profiles").select("*").execute().data
        total_fetched = total_drafted = 0
        for client in clients:
            location_id = (client.get("metadata") or {}).get("ghl_location_id")
            if not location_id:
                continue
            result = ingest_client_reviews(
                client_id=client["id"],
                location_id=location_id,
                business_name=client["business_name"],
                owner_first=(client.get("contact_name") or client["business_name"]).split()[0],
                business_phone=client.get("contact_phone") or "",
            )
            total_fetched += result["fetched"]
            total_drafted += result["drafted"]
            log.info(f"client={client['business_name']} fetched={result['fetched']} drafted={result['drafted']}")
        heartbeat(AGENT_SLUG, JOB_NAME, "success", f"fetched={total_fetched} drafted={total_drafted}")
    except Exception as e:
        heartbeat(AGENT_SLUG, JOB_NAME, "failed", str(e))
        raise


if __name__ == "__main__":
    main()
