"""
agent_task_receipts helper — for multi-target tasks (campaigns, batches)
where a single agent_actions row can't express per-item outcomes well.
Any agent doing a "send to N recipients" / "categorize N rows" style task
should call record_task_receipt() with the real intended/completed/failed
counts, never a rounded-up summary.
"""
from typing import Optional

from app.database import supabase


def record_task_receipt(
    client_id: str,
    agent_slug: str,
    task_ref: str,
    intended_count: int,
    completed_count: int,
    failed_count: int = 0,
    partial_reason: Optional[str] = None,
    evidence: Optional[dict] = None,
) -> dict:
    row = {
        "client_id": client_id,
        "agent_slug": agent_slug,
        "task_ref": task_ref,
        "intended_count": intended_count,
        "completed_count": completed_count,
        "failed_count": failed_count,
        "partial_reason": partial_reason,
        "evidence": evidence,
    }
    result = supabase.schema("foundation").table("agent_task_receipts").insert(row).execute()
    return result.data[0]


def format_client_report(receipt: dict) -> str:
    """The client-facing line Rule 2 (§2.3) requires: always completed-of-
    intended, never a bare 'done'."""
    intended = receipt["intended_count"]
    completed = receipt["completed_count"]
    line = f"Sent {completed} of {intended}"
    if receipt.get("failed_count"):
        line += f" — {receipt['failed_count']} failed"
        if receipt.get("partial_reason"):
            line += f" ({receipt['partial_reason']})"
    return line
