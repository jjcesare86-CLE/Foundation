"""Daily deadline reminders (T-30/7/1), 1099 threshold sweep, anomaly digest."""
import logging
from datetime import date, timedelta

from app.database import supabase

logger = logging.getLogger(__name__)

REMINDER_WINDOWS = (30, 7, 1)


def run_deadline_reminders(today: date | None = None) -> dict:
    """Finds upcoming zb_tax_deadlines rows landing exactly 30/7/1 days out and
    marks them reminded. Actual SMS/email delivery is a TODO on the same
    connection_broker/GHL gap noted in stripe_client.py — this always does the
    bookkeeping (status/reminders_sent) so nothing depends on delivery to stay correct."""
    today = today or date.today()
    reminded = []
    for offset in REMINDER_WINDOWS:
        target = today + timedelta(days=offset)
        rows = (
            supabase.schema("foundation").table("zb_tax_deadlines")
            .select("*").eq("due_date", target.isoformat()).neq("status", "done")
            .execute().data
        )
        for row in rows:
            supabase.schema("foundation").table("zb_tax_deadlines").update({
                "status": "reminded", "reminders_sent": row["reminders_sent"] + 1,
            }).eq("id", row["id"]).execute()
            reminded.append({"deadline_id": row["id"], "client_id": row["client_id"], "days_out": offset})
    return {"reminded": reminded}


def run_1099_sweep(tax_year: int | None = None) -> dict:
    """Flags any contractor whose ytd_paid crosses the $600 IRS threshold and
    isn't already flagged."""
    tax_year = tax_year or date.today().year
    rows = (
        supabase.schema("foundation").table("zb_contractors")
        .select("*").eq("tax_year", tax_year).gte("ytd_paid", 600).eq("threshold_flagged", False)
        .execute().data
    )
    for row in rows:
        supabase.schema("foundation").table("zb_contractors").update({
            "threshold_flagged": True,
        }).eq("id", row["id"]).execute()
    return {"newly_flagged": len(rows), "contractors": [r["contractor_name"] for r in rows]}


def run_anomaly_digest(client_id: str | None = None) -> list[dict]:
    query = (
        supabase.schema("foundation").table("zb_transactions")
        .select("id,client_id,occurred_at,amount,category,notes")
        .eq("anomaly_flag", True)
    )
    if client_id:
        query = query.eq("client_id", client_id)
    return query.execute().data
