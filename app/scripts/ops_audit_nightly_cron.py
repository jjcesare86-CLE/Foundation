"""Render cron 'ops-audit-nightly' — full L1-L4 audit every night (L5 smoke
calls are weekly per spec, see ops_audit_weekly_smoke_cron.py, since they
cost real money). Writes docs/state/OPS_AUDIT.md-style output to the logs;
red statuses paging John via GHL SMS is a TODO on the same generic-GHL-
messaging gap noted in silas/action_types.py."""
import logging
import sys

sys.path.insert(0, ".")

from app.ops.ops_audit import run_full_audit

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("ops_audit_nightly_cron")


def main() -> None:
    board = run_full_audit(run_l5=False)
    counts = {"green": 0, "amber": 0, "red": 0}
    for row in board:
        counts[row["status"]] += 1
        if row["status"] != "green":
            failing = [f"{k}:{v['reason']}" for k, v in row["layers"].items() if v["pass"] is False]
            log.warning(f"{row['status'].upper()} {row['agent_id']} — {'; '.join(failing)}")
    log.info(f"audit complete: {counts}")


if __name__ == "__main__":
    main()
