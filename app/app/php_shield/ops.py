"""
PHP Shield -- operational safety net.

Nothing that matters is allowed to fail silently:
  * guarded_write()  - wraps every lead/order/authorization write. On failure it
    logs with context, persists the payload to a dead-letter file (and, best
    effort, a dead_letters row), alerts the owner, then raises WriteFailed so the
    caller returns a clear 503 instead of pretending it worked.
  * Alerter          - owner email (+ Slack/Discord-compatible webhook when
    SLACK_WEBHOOK_URL is set), rate-limited per alert key and globally so a
    broken dependency can't flood the inbox.
  * startup_selftest - writes then deletes a test row at boot.
  * health_report    - config + DB connectivity for /health (never returns secrets).
"""
import json
import logging
import threading
import time
from pathlib import Path
from typing import Callable, Optional

import requests

from app.php_shield import config
from app.php_shield.store import StoreError, iso

log = logging.getLogger("php_shield")


class WriteFailed(RuntimeError):
    def __init__(self, kind: str):
        self.kind = kind
        super().__init__(f"write failed: {kind}")


class Alerter:
    def __init__(self, mailer, *, min_interval: int = 600, max_per_hour: int = 20, post=requests.post):
        self.mailer, self.min_interval, self.max_per_hour, self._post = mailer, min_interval, max_per_hour, post
        self._last: dict[str, float] = {}
        self._sent: list[float] = []
        self._lock = threading.Lock()
        self.suppressed = 0

    def alert(self, key: str, subject: str, body: str) -> bool:
        """Never raises. Returns True if an alert was actually dispatched."""
        now = time.time()
        with self._lock:
            self._sent = [t for t in self._sent if t > now - 3600]
            if now - self._last.get(key, 0) < self.min_interval or len(self._sent) >= self.max_per_hour:
                self.suppressed += 1
                log.warning("alert suppressed (rate limit) key=%s subject=%s", key, subject)
                return False
            self._last[key] = now
            self._sent.append(now)
        log.error("ALERT [%s] %s :: %s", key, subject, body[:500])
        delivered = False
        owner = config.owner_email()
        if owner:
            try:
                self.mailer.send(owner, f"[PHP Shield ALERT] {subject}", f"<pre>{_esc(body)}</pre>")
                delivered = True
            except Exception:
                log.exception("alert email failed")
        hook = config.env("SLACK_WEBHOOK_URL")
        if hook:
            try:
                text = f"*PHP Shield alert:* {subject}\n{body[:1500]}"
                self._post(hook, json={"text": text, "content": text}, timeout=5)
                delivered = True
            except Exception:
                log.exception("alert webhook failed")
        return delivered


def _esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def dead_letter_path() -> Path:
    return Path(config.env("PHP_SHIELD_DEAD_LETTER_PATH", "dead_letters/php_shield.jsonl"))


def dead_letter(kind: str, payload: dict, error: str, store=None) -> None:
    """Persist a failed write so it can be replayed by hand. File first (works when the DB is
    the thing that's broken), table second (best effort)."""
    record = {"at": iso(), "kind": kind, "error": error, "payload": payload}
    try:
        path = dead_letter_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, default=str) + "\n")
    except Exception:
        log.exception("dead-letter file write failed; payload follows: %s", json.dumps(record, default=str))
    if store is not None:
        try:
            store.insert("dead_letters", {"kind": kind, "payload": payload, "error": error})
        except Exception:
            log.warning("dead_letters table write failed (file copy exists)")


def guarded_write(svc, kind: str, payload: dict, fn: Callable, context: Optional[dict] = None):
    try:
        return fn()
    except Exception as e:  # noqa: BLE001 -- we re-raise as WriteFailed after recording
        err = f"{type(e).__name__}: {e}"
        log.exception("write failed kind=%s context=%s", kind, context)
        dead_letter(kind, payload, err, store=svc.store)
        svc.alerter.alert(f"write:{kind}", f"{kind} write FAILED", f"{err}\ncontext={context}\npayload={json.dumps(payload, default=str)[:1200]}")
        raise WriteFailed(kind) from e


def startup_selftest(store) -> None:
    """Write + delete a probe row. Raises on failure; the caller decides whether that is fatal."""
    row = store.insert("health_checks", {})
    store.delete("health_checks", id=row["id"])


def health_report(svc) -> dict:
    cfg = config.check()
    db: dict = {"ok": True}
    try:
        svc.store.select_since("scan_events", iso())
    except StoreError as e:
        db = {"ok": False, "error": str(e)[:200]}
    key = config.env("STRIPE_SECRET_KEY")
    return {
        "ok": cfg.ok and db["ok"],
        "environment": "production" if config.is_production() else "development",
        "config": {"missing": cfg.missing, "warnings": cfg.warnings},
        "database": db,
        "stripe": {"configured": bool(key), "mode": "live" if key.startswith(("sk_live_", "rk_live_")) else "test" if key else None},
        "email": {"configured": bool(config.env("RESEND_API_KEY")), "owner_set": bool(config.owner_email())},
        "turnstile": {"enabled": bool(config.env("TURNSTILE_SECRET"))},
        "alerts": {"slack_webhook": bool(config.env("SLACK_WEBHOOK_URL")), "suppressed": svc.alerter.suppressed},
    }
