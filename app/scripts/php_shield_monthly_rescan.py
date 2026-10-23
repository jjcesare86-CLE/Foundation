"""
Render cron `php-shield-monthly-rescan` -- runs daily; rescans every active Maintenance Plan
subscription whose next_scan_at has passed (about once every 30 days each).

Only domains with a valid signed authorization AND verified ownership are scanned. Customers get
their report by email; the owner is alerted on any NEW critical finding or failure. Exits non-zero
if any subscription errored, so Render marks the run failed.
"""
import json
import logging
import sys

sys.path.insert(0, ".")

from app.php_shield import config, maintenance, services  # noqa: E402

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("php_shield_monthly_rescan")


def main() -> int:
    config.validate_startup(config.CRON_REQUIRED)
    svc = services.init_services()
    summary = maintenance.run_monthly(svc)
    log.info("monthly rescan summary: %s", json.dumps(summary))
    return 1 if summary["errors"] else 0


if __name__ == "__main__":
    sys.exit(main())
