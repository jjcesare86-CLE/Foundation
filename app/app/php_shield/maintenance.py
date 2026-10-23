"""
PHP Shield -- monthly maintenance rescans.

Run daily by the Render cron job `php-shield-monthly-rescan` (app/scripts/php_shield_monthly_rescan.py).
Only subscriptions that are active AND whose order still has a valid signed authorization
and verified domain ownership are rescanned -- consent is re-checked on every run.
"""
import logging
from datetime import timedelta
from typing import Callable, Optional

from app.php_shield import notify, orders, report_generator
from app.php_shield import scanner as scanner_mod
from app.php_shield.ops import guarded_write
from app.php_shield.store import iso, parse_iso, utcnow

log = logging.getLogger("php_shield")
INTERVAL_DAYS = 30


def _level(scan: Optional[dict]) -> str:
    return ((scan or {}).get("risk") or {}).get("risk_level", "unknown")


def run_monthly(svc, *, now=None, scanner: Optional[Callable] = None) -> dict:
    now = now or utcnow()
    scan = scanner or scanner_mod.scan
    summary = {"due": 0, "scanned": 0, "skipped_no_consent": 0, "critical_alerts": 0, "errors": 0}

    for sub in svc.store.select("subscriptions", status="active"):
        if not sub.get("next_scan_at") or parse_iso(sub["next_scan_at"]) > now:
            continue
        summary["due"] += 1
        try:
            order = orders.get_order(svc, sub["order_id"])
            if not orders.valid_authorization(svc, order) or not orders.domain_verified(svc, order):
                summary["skipped_no_consent"] += 1
                svc.alerter.alert(f"maint:noconsent:{sub['id']}", f"Rescan skipped: {sub['domain']}",
                                  "Active Maintenance Plan but no valid authorization / verified ownership. Not scanning.")
                continue

            result = scan(f"https://{sub['domain']}").to_dict()
            prev_rows = sorted(svc.store.select("scan_reports", order_id=order["id"]), key=lambda r: r["created_at"])
            previous = prev_rows[-1]["result"] if prev_rows else None
            if previous is None and order.get("lead_id"):
                lead = (svc.store.select("leads", id=order["lead_id"]) or [{}])[0]
                previous = lead.get("scan")

            rep = {"order_id": order["id"], "domain": sub["domain"], "kind": "monthly", "version": result.get("version"),
                   "risk_level": _level(result), "result": result}
            guarded_write(svc, "scan_report", rep, lambda rep=rep: svc.store.insert("scan_reports", rep), {"sub": sub["id"]})

            if result.get("error"):
                svc.alerter.alert(f"maint:error:{sub['id']}", f"Monthly rescan could not reach {sub['domain']}", result["error"])
            else:
                html = ("<p>Here is this month's security rescan.</p>"
                        + report_generator.render_comparison(previous or {}, result, sub["domain"]))
                notify.safe_send(svc, sub["customer_email"], f"PHP Shield monthly report: {sub['domain']}",
                                 notify._wrap("Your monthly PHP Shield report", html), kind="customer_monthly")
            if _level(result) == "critical" and _level(previous) != "critical":
                summary["critical_alerts"] += 1
                svc.alerter.alert(f"maint:critical:{sub['id']}:{result.get('version')}", f"NEW CRITICAL finding: {sub['domain']}",
                                  f"PHP {result.get('version')} - {(result.get('risk') or {}).get('headline', '')}")

            svc.store.update("subscriptions", {"last_scan_at": iso(now), "next_scan_at": iso(now + timedelta(days=INTERVAL_DAYS))},
                             id=sub["id"])
            summary["scanned"] += 1
        except Exception as e:  # noqa: BLE001 - one bad subscription must not stop the rest
            summary["errors"] += 1
            log.exception("monthly rescan failed sub=%s", sub.get("id"))
            svc.alerter.alert(f"maint:fail:{sub.get('id')}", f"Monthly rescan failed: {sub.get('domain')}", f"{type(e).__name__}: {e}")
    return summary
