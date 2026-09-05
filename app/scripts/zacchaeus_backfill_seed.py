"""
SYNTHETIC 90-day transaction backfill for Delivered Fireworks and LUTS.

This is NOT real Stripe data — connection_broker has no live Stripe
connection for any client yet (see app/app/zacchaeus/stripe_client.py).
It stands in for the real backfill so the categorization pipeline has
something real to run against end-to-end until Connections Hub (item C)
ships. Every row this script writes is plausible-but-fabricated; delete
and re-run the real Stripe sync once that connection exists.

Idempotent: skips a client if it already has zb_transactions rows.
"""
import random
import sys
from datetime import date, timedelta

sys.path.insert(0, ".")

from app.database import supabase

random.seed(42)

EXPENSE_PATTERNS = [
    ("cost_of_goods_pyro", "Pyro supply order", 800, 12000),
    ("insurance_adjacent", "Event liability insurance", 300, 1500),
    ("permits_licensing", "State display permit fee", 150, 900),
    ("vehicle_fuel", "Fuel — show truck", 60, 240),
    ("labor_crew", "Crew payroll", 1200, 6000),
    ("marketing", "Facebook/Instagram ads", 100, 600),
    ("software_subscriptions", "Foundation / scheduling software", 49, 299),
    ("office_supplies", "Office supplies", 20, 150),
    ("equipment", "Mortar rack / equipment purchase", 500, 4000),
]
INCOME_PATTERNS = [
    ("other_income", "Show booking deposit", 2000, 15000),
    ("other_income", "Show booking final payment", 3000, 25000),
]


def _fake_transactions(days: int = 90) -> list[dict]:
    rows = []
    today = date.today()
    for i in range(days):
        d = today - timedelta(days=i)
        if random.random() < 0.35:
            category, desc, lo, hi = random.choice(EXPENSE_PATTERNS)
            rows.append({
                "occurred_at": d.isoformat(),
                "amount": round(random.uniform(lo, hi), 2),
                "direction": "expense",
                "source": "stripe",
                "raw_description": desc,
                "categorized_by": "uncategorized",
            })
        if random.random() < 0.15:
            category, desc, lo, hi = random.choice(INCOME_PATTERNS)
            rows.append({
                "occurred_at": d.isoformat(),
                "amount": round(random.uniform(lo, hi), 2),
                "direction": "income",
                "source": "stripe",
                "raw_description": desc,
                "categorized_by": "uncategorized",
            })
    return rows


def backfill_client(business_name: str) -> int:
    client = (
        supabase.schema("foundation").table("client_profiles")
        .select("id").eq("business_name", business_name).execute().data
    )
    if not client:
        print(f"SKIP {business_name}: no client_profiles row")
        return 0
    client_id = client[0]["id"]

    existing = (
        supabase.schema("foundation").table("zb_transactions")
        .select("id", count="exact").eq("client_id", client_id).execute()
    )
    if existing.count:
        print(f"SKIP {business_name}: already has {existing.count} zb_transactions rows")
        return 0

    rows = [{**r, "client_id": client_id} for r in _fake_transactions()]
    supabase.schema("foundation").table("zb_transactions").insert(rows).execute()
    print(f"backfilled {len(rows)} synthetic transactions for {business_name}")
    return len(rows)


if __name__ == "__main__":
    for name in ("Delivered Fireworks", "LUTS"):
        backfill_client(name)
