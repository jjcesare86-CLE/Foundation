"""
PHP Shield -- service container.

One place that wires store / mailer / alerter / limiters together so the API, the cron
job and the tests all build the same graph. Tests call init_services() with in-memory
doubles; production calls build_default() at startup.
"""
from dataclasses import dataclass
from typing import Any, Optional

from app.php_shield import config
from app.php_shield.emailer import build_mailer
from app.php_shield.ops import Alerter
from app.php_shield.ratelimit import RateLimiter, SimpleLimiter
from app.php_shield.store import MemoryStore, SupabaseStore


@dataclass
class Services:
    store: Any
    mailer: Any
    alerter: Alerter
    limiter: RateLimiter
    simple_limiter: SimpleLimiter
    stripe: Any = None


_services: Optional[Services] = None


def build_default() -> Services:
    url, key = config.env("PHP_SHIELD_SUPABASE_URL"), config.env("PHP_SHIELD_SUPABASE_SERVICE_ROLE_KEY")
    if url and key:
        store = SupabaseStore(url, key)
    elif config.is_production():
        raise RuntimeError("PHP Shield refusing to start: Supabase is not configured")
    else:
        store = MemoryStore()  # local dev only; data is lost on restart
    mailer = build_mailer()
    from app.php_shield.billing import StripeGateway

    return Services(store=store, mailer=mailer, alerter=Alerter(mailer), limiter=RateLimiter(store),
                    simple_limiter=SimpleLimiter(), stripe=StripeGateway())


def init_services(svc: Optional[Services] = None, **overrides) -> Services:
    global _services
    _services = svc or build_default()
    for k, v in overrides.items():
        setattr(_services, k, v)
    return _services


def get() -> Services:
    if _services is None:
        raise RuntimeError("PHP Shield services not initialised")
    return _services
