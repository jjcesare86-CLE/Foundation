"""Render cron 'amos-daily' — T-90/30/7 license reminders + expiry sweep."""
import logging
import sys

sys.path.insert(0, ".")

from app.amos.deadlines import run_deadline_reminders, run_expiry_sweep
from app.ops.heartbeat import heartbeat

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("amos_daily_cron")

AGENT_SLUG, JOB_NAME = "amos-compliance", "amos-daily"


def main() -> None:
    try:
        deadlines = run_deadline_reminders()
        log.info(f"license reminders sent: {len(deadlines['reminded'])}")
        expiry = run_expiry_sweep()
        log.info(f"newly expired: {expiry['newly_expired']}")
        heartbeat(AGENT_SLUG, JOB_NAME, "success", f"reminded={len(deadlines['reminded'])} expired={expiry['newly_expired']}")
    except Exception as e:
        heartbeat(AGENT_SLUG, JOB_NAME, "failed", str(e))
        raise


if __name__ == "__main__":
    main()
