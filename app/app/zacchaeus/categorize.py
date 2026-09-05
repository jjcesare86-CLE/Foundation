"""
Sonnet categorization pipeline for foundation.zb_transactions. Confidence
below CONFIDENCE_THRESHOLD queues a one-question clarification via the
shared action library instead of guessing.
"""
import json
import logging

from app.database import supabase
from app.llm_router import llm_call, TaskTier

logger = logging.getLogger(__name__)

CONFIDENCE_THRESHOLD = 0.7

CATEGORIZE_SYSTEM = """You are Zacchaeus, categorizing one business transaction for
{business_name}, a {industry} business.

Assign it to exactly one category from this chart of accounts:
cost_of_goods, insurance, permits_licensing, vehicle_fuel, labor_crew,
marketing, software_subscriptions, office_supplies, travel, meals,
equipment, rent_utilities, professional_fees, bank_fees, other_income,
other_expense

Output ONLY valid JSON, no markdown fences:
{{
  "category": "<one of the categories above>",
  "confidence": 0.0-1.0,
  "anomaly": false,
  "note": "<one short plain-English note, or empty string>"
}}

Set anomaly=true only for something a business owner would want flagged —
an unusually large amount for its category, a description that doesn't
match its likely category, a duplicate-looking charge. Set confidence low
(<0.6) when the raw_description is too vague to categorize confidently
rather than guessing with false certainty."""


def categorize_transaction(tx: dict, business_name: str, industry: str) -> dict:
    user_msg = (
        f"Date: {tx['occurred_at']}\n"
        f"Amount: ${tx['amount']} ({tx['direction']})\n"
        f"Description: {tx.get('raw_description') or '(none)'}"
    )
    raw = llm_call(
        messages=[{"role": "user", "content": user_msg}],
        tier=TaskTier.STANDARD,
        system=CATEGORIZE_SYSTEM.format(business_name=business_name, industry=industry),
        max_tokens=300,
        project="foundation",
        agent_name="zacchaeus-books",
        task_type="zacchaeus:categorize_transaction",
    )
    cleaned = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    return json.loads(cleaned)


def run_categorization_batch(client_id: str, business_name: str, industry: str, limit: int = 100) -> dict:
    """Pulls uncategorized transactions for one client, categorizes each,
    writes the result. Sub-threshold confidence -> categorized_by='needs_clarification'
    instead of 'zacchaeus', category left as the model's best guess but flagged."""
    rows = (
        supabase.schema("foundation").table("zb_transactions")
        .select("*").eq("client_id", client_id).eq("categorized_by", "uncategorized")
        .limit(limit).execute().data
    )

    categorized = 0
    needs_clarification = 0
    anomalies = 0

    for tx in rows:
        try:
            result = categorize_transaction(tx, business_name, industry)
        except Exception as e:
            logger.exception(f"categorization failed for tx {tx['id']}: {e}")
            continue

        confidence = float(result.get("confidence", 0) or 0)
        low_confidence = confidence < CONFIDENCE_THRESHOLD

        supabase.schema("foundation").table("zb_transactions").update({
            "category": result.get("category"),
            "confidence": confidence,
            "anomaly_flag": bool(result.get("anomaly")),
            "notes": result.get("note") or None,
            "categorized_by": "needs_clarification" if low_confidence else "zacchaeus",
        }).eq("id", tx["id"]).execute()

        categorized += 1
        if low_confidence:
            needs_clarification += 1
        if result.get("anomaly"):
            anomalies += 1

    return {
        "processed": len(rows),
        "categorized": categorized,
        "needs_clarification": needs_clarification,
        "anomalies": anomalies,
    }
