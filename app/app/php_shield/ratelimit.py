"""
PHP Shield -- abuse limits for the public scan endpoint.

Backed by the `scan_events` table (survives restarts and works across
instances) with the same store used everywhere else. Limits (all env-tunable):

  per IP            5 scans / hour        PHP_SHIELD_LIMIT_IP_PER_HOUR
  per target domain 3 scans / day         PHP_SHIELD_LIMIT_DOMAIN_PER_DAY
  global            500 scans / day       PHP_SHIELD_LIMIT_GLOBAL_PER_DAY
  concurrency       4 scans at once       PHP_SHIELD_MAX_CONCURRENT_SCANS

A scan ATTEMPT counts whether or not it succeeds -- otherwise failing scans
would be a free way to hammer a target.
"""
import hashlib
import hmac
import os
import threading
import time
from contextlib import contextmanager
from datetime import timedelta
from typing import Optional

from app.php_shield.store import StoreError, iso, parse_iso, utcnow

HOUR, DAY = 3600, 86400


class RateLimited(Exception):
    def __init__(self, scope: str, retry_after: int):
        self.scope, self.retry_after = scope, max(1, int(retry_after))
        super().__init__(f"rate limit exceeded ({scope})")


class Busy(Exception):
    """Global concurrency cap reached."""
    retry_after = 15


def _int_env(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, default))
    except ValueError:
        return default


def hash_ip(ip: str) -> str:
    salt = os.getenv("PHP_SHIELD_IP_HASH_SALT", "dev-salt")
    return hmac.new(salt.encode(), ip.encode(), hashlib.sha256).hexdigest()[:32]


class RateLimiter:
    def __init__(self, store, *, ip_per_hour=None, domain_per_day=None, global_per_day=None, max_concurrent=None):
        self.store = store
        self.ip_per_hour = ip_per_hour if ip_per_hour is not None else _int_env("PHP_SHIELD_LIMIT_IP_PER_HOUR", 5)
        self.domain_per_day = domain_per_day if domain_per_day is not None else _int_env("PHP_SHIELD_LIMIT_DOMAIN_PER_DAY", 3)
        self.global_per_day = global_per_day if global_per_day is not None else _int_env("PHP_SHIELD_LIMIT_GLOBAL_PER_DAY", 500)
        self._sem = threading.BoundedSemaphore(max_concurrent if max_concurrent is not None else _int_env("PHP_SHIELD_MAX_CONCURRENT_SCANS", 4))
        self._lock = threading.Lock()
        self._fallback: list[dict] = []  # used only if the store is down, so limits never fail open

    # -- event bookkeeping -------------------------------------------------
    def _times(self, since_seconds: int, **eq) -> list:
        since = iso(utcnow() - timedelta(seconds=since_seconds))
        try:
            rows = self.store.select_since("scan_events", since, **eq)
        except StoreError:
            cutoff = time.time() - since_seconds
            rows = [r for r in self._fallback if r["_t"] >= cutoff and all(r.get(k) == v for k, v in eq.items())]
            return sorted(r["_t"] for r in rows)
        return sorted(parse_iso(r["created_at"]).timestamp() for r in rows)

    def _record(self, ip_hash: str, domain: str):
        try:
            self.store.insert("scan_events", {"ip_hash": ip_hash, "domain": domain})
        except StoreError:
            self._fallback.append({"ip_hash": ip_hash, "domain": domain, "_t": time.time()})

    @staticmethod
    def _retry_after(times: list, window: int, limit: int) -> int:
        # the (len-limit+1)-th oldest event must age out before another is allowed
        idx = len(times) - limit
        return window - (time.time() - times[max(idx, 0)])

    def check_and_record(self, ip: str, domain: str) -> None:
        ip_hash = hash_ip(ip)
        checks = (
            ("ip", HOUR, self.ip_per_hour, {"ip_hash": ip_hash}),
            ("domain", DAY, self.domain_per_day, {"domain": domain}),
            ("global", DAY, self.global_per_day, {}),
        )
        with self._lock:
            for scope, window, limit, eq in checks:
                times = self._times(window, **eq)
                if len(times) >= limit:
                    raise RateLimited(scope, self._retry_after(times, window, limit))
            self._record(ip_hash, domain)

    @contextmanager
    def slot(self):
        if not self._sem.acquire(blocking=False):
            raise Busy()
        try:
            yield
        finally:
            self._sem.release()


class SimpleLimiter:
    """In-process sliding window for the cheap endpoints (checkout, quote, intake...)."""

    def __init__(self):
        self._hits: dict[str, list[float]] = {}
        self._lock = threading.Lock()

    def check(self, key: str, limit: int, window: int = HOUR) -> None:
        now = time.time()
        with self._lock:
            hits = [t for t in self._hits.get(key, []) if t > now - window]
            if len(hits) >= limit:
                self._hits[key] = hits
                raise RateLimited(key.split(":")[0], window - (now - hits[0]))
            hits.append(now)
            self._hits[key] = hits


def client_ip(request) -> str:
    """Render's proxy APPENDS the real client address to X-Forwarded-For, so the
    right-most entry is the only one a caller cannot forge."""
    xff: Optional[str] = request.headers.get("x-forwarded-for")
    if xff:
        parts = [p.strip() for p in xff.split(",") if p.strip()]
        if parts:
            return parts[-1]
    return request.client.host if request.client else "unknown"
