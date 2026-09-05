"""Render cron 'connections-health-nightly' — verifies every 'active'
connection, flips broken ones to 'expired'. Owner alerting ("reconnect
your Facebook") via GHL SMS/email is a TODO on the same generic-GHL-
messaging gap noted throughout this build (rahab/ghl_client.py,
silas/action_types.py) — this does the verification + status bookkeeping
for real; the notification send is not implemented yet."""
import logging
import sys

sys.path.insert(0, ".")

from app.database import supabase
from app.routers.connections import verify

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("connections_health_cron")


def main() -> None:
    rows = supabase.schema("foundation").table("client_connections").select("id,provider,client_id").eq("status", "active").execute().data
    flipped = 0
    for row in rows:
        result = verify(row["id"])
        if result.get("status") == "expired":
            flipped += 1
            log.warning(f"EXPIRED client={row['client_id']} provider={row['provider']} connection={row['id']} — reconnect needed")
    log.info(f"checked {len(rows)} active connections, {flipped} flipped to expired")


if __name__ == "__main__":
    main()
