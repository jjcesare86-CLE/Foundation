"""Render cron 'ops-audit-weekly-smoke' — the L5 layer (one cheap canned
prompt per agent through the real router). Weekly, not nightly, because it
costs real tokens across the whole roster."""
import logging
import sys

sys.path.insert(0, ".")

from app.ops.ops_audit import run_full_audit

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("ops_audit_weekly_smoke_cron")


def main() -> None:
    board = run_full_audit(run_l5=True)
    l5_fail = [row["agent_id"] for row in board if row["layers"]["L5"]["pass"] is False]
    log.info(f"L5 smoke complete: {len(board) - len(l5_fail)}/{len(board)} passed")
    if l5_fail:
        log.warning(f"L5 failures: {l5_fail}")


if __name__ == "__main__":
    main()
