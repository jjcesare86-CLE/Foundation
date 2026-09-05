"""Render cron 'zacchaeus-daily' — deadline reminders (T-30/7/1) + 1099 sweep."""
import logging
import sys

sys.path.insert(0, ".")

from app.zacchaeus.deadlines import run_deadline_reminders, run_1099_sweep

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("zacchaeus_daily_cron")


def main() -> None:
    deadlines = run_deadline_reminders()
    log.info(f"deadline reminders sent: {len(deadlines['reminded'])}")
    contractors = run_1099_sweep()
    log.info(f"1099 threshold newly flagged: {contractors['newly_flagged']} ({contractors['contractors']})")


if __name__ == "__main__":
    main()
