"""T-90/30/7 license/permit renewal reminders."""
from datetime import date, timedelta
from typing import Optional

from app.database import supabase

REMINDER_WINDOWS = (90, 30, 7)


def run_deadline_reminders(today: Optional[date] = None) -> dict:
    today = today or date.today()
    reminded = []
    for offset in REMINDER_WINDOWS:
        target = today + timedelta(days=offset)
        rows = (
            supabase.schema("foundation").table("am_licenses")
            .select("*").eq("expires_at", target.isoformat()).neq("status", "expired")
            .execute().data
        )
        for row in rows:
            supabase.schema("foundation").table("am_licenses").update({
                "status": "reminded", "reminders_sent": row["reminders_sent"] + 1,
            }).eq("id", row["id"]).execute()
            reminded.append({"license_id": row["id"], "client_id": row["client_id"], "days_out": offset, "license_type": row["license_type"]})
    return {"reminded": reminded}


def run_expiry_sweep(today: Optional[date] = None) -> dict:
    """Anything past its expires_at that isn't already marked expired gets flagged."""
    today = today or date.today()
    rows = (
        supabase.schema("foundation").table("am_licenses")
        .select("id").lt("expires_at", today.isoformat()).neq("status", "expired")
        .execute().data
    )
    for row in rows:
        supabase.schema("foundation").table("am_licenses").update({"status": "expired"}).eq("id", row["id"]).execute()
    return {"newly_expired": len(rows)}
