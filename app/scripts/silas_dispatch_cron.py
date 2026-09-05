"""Render cron 'silas-dispatch-builder' — runs at 05:30. Builds today's
dispatch (crew assignment + nearest-neighbor route order) for every client
with active fs_crews rows."""
import logging
import sys
from datetime import date

sys.path.insert(0, ".")

from app.database import supabase
from app.silas.dispatch import build_dispatch
from app.ops.heartbeat import heartbeat

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("silas_dispatch_cron")

AGENT_SLUG, JOB_NAME = "silas-dispatch", "silas-dispatch-builder"


def main() -> None:
    try:
        crew_rows = supabase.schema("foundation").table("fs_crews").select("client_id").eq("active", True).execute().data
        client_ids = sorted(set(r["client_id"] for r in crew_rows))
        total_dispatched = 0
        for client_id in client_ids:
            result = build_dispatch(client_id, date.today())
            total_dispatched += result["jobs_dispatched"]
            log.info(f"client={client_id} dispatched={result['jobs_dispatched']} crews={result['crews_used']} unassigned={len(result['unassigned'])}")
        heartbeat(AGENT_SLUG, JOB_NAME, "success", f"clients={len(client_ids)} jobs_dispatched={total_dispatched}")
    except Exception as e:
        heartbeat(AGENT_SLUG, JOB_NAME, "failed", str(e))
        raise


if __name__ == "__main__":
    main()
