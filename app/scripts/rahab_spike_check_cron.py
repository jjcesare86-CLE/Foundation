"""Render cron 'rahab-spike-check' — runs nightly. Logs any client with 3+
negative (<=2 star) reviews in the last 72h. Owner alerting (SMS/email via
GHL) is a TODO wired once Connections Hub (item C) ships a per-client
notification target; for now this makes the spike visible in cron logs and
in the return value for anything that wants to poll it via /rahab/spike-check.
"""
import logging
import sys

sys.path.insert(0, ".")

from app.rahab.ingestion import detect_spikes
from app.ops.heartbeat import heartbeat

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("rahab_spike_check_cron")

AGENT_SLUG, JOB_NAME = "rahab-reputation", "rahab-spike-check"


def main() -> None:
    try:
        spikes = detect_spikes()
        if not spikes:
            log.info("no spikes detected")
        for spike in spikes:
            log.warning(f"SPIKE client={spike['client_id']} count={spike['count']} window={spike['window_hours']}h")
        heartbeat(AGENT_SLUG, JOB_NAME, "success", f"spikes={len(spikes)}")
    except Exception as e:
        heartbeat(AGENT_SLUG, JOB_NAME, "failed", str(e))
        raise


if __name__ == "__main__":
    main()
