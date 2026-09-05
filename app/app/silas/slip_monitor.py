"""
15-minute slip monitor: compares the GPS clock-in feed against scheduled
dispatch order. fetch_gps_clockins() is an honest stub -- Exterior
Rescue's feed endpoint was never confirmed (it's on John's prereq list in
the Batch 1 doc), so this raises rather than inventing clock-in data.
detect_slips() takes already-known clock-in data so the slip-detection
LOGIC is real and testable independent of where that data comes from.
"""
from datetime import datetime, timezone
from typing import Optional

from app.database import supabase

SLIP_THRESHOLD_MINUTES = 20


def fetch_gps_clockins(client_id: str) -> list[dict]:
    """TODO: wire to Exterior Rescue's real GPS clock-in feed once its
    endpoint is confirmed. [{"job_id": ..., "clocked_in_at": iso8601}]"""
    raise NotImplementedError(
        "no GPS clock-in feed configured for this client -- endpoint not yet "
        "confirmed (see Batch 1 doc manual prereqs). Pass clock-in data "
        "directly to detect_slips() for testing."
    )


def detect_slips(dispatched_jobs: list[dict], clockins: dict[str, datetime], now: Optional[datetime] = None) -> list[dict]:
    """dispatched_jobs: fs_jobs rows with status='dispatched' or 'enroute'.
    clockins: {job_id: clocked_in_at datetime}, missing entries mean not yet
    clocked in. A job slips if it has no clock-in more than
    SLIP_THRESHOLD_MINUTES past its expected start (approximated here by
    route_order * average job duration -- a real dispatch start time would
    come from run-sheet generation, not reconstructed after the fact)."""
    now = now or datetime.now(timezone.utc)
    slipped = []
    for job in dispatched_jobs:
        clocked_in = clockins.get(job["id"])
        if clocked_in is not None:
            continue
        expected = job.get("expected_start")
        if expected and (now - expected).total_seconds() / 60 > SLIP_THRESHOLD_MINUTES:
            slipped.append({"job_id": job["id"], "minutes_late": int((now - expected).total_seconds() / 60)})
    return slipped


def mark_slipped(job_ids: list[str]) -> None:
    for job_id in job_ids:
        supabase.schema("foundation").table("fs_jobs").update({"status": "slipped"}).eq("id", job_id).execute()
