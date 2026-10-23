"""Shared fixtures: in-memory services, signed-webhook helper, canned network."""
import hashlib
import hmac
import json
import time
import uuid

import pytest
from fastapi.testclient import TestClient

from app.php_shield import billing, netsafe, services
from app.php_shield.emailer import OutboxMailer
from app.php_shield.ops import Alerter
from app.php_shield.ratelimit import RateLimiter, SimpleLimiter
from app.php_shield.store import MemoryStore

WEBHOOK_SECRET = "whsec_test_secret"
ADMIN_KEY = "admin-test-key"
PUBLIC_IP = "93.184.216.34"

ENV = {
    "PHP_SHIELD_ENV": "development",
    "PHP_SHIELD_OWNER_EMAIL": "owner@example.com",
    "PHP_SHIELD_ADMIN_API_KEY": ADMIN_KEY,
    "PHP_SHIELD_IP_HASH_SALT": "test-salt",
    "PHP_SHIELD_SITE_URL": "https://site.test",
    "STRIPE_SECRET_KEY": "sk_test_123",
    "STRIPE_WEBHOOK_SECRET": WEBHOOK_SECRET,
    "STRIPE_PRICE_PHPSHIELD_BASIC": "price_basic",
    "STRIPE_PRICE_PHPSHIELD_STANDARD": "price_standard",
    "STRIPE_PRICE_PHPSHIELD_COMPLEX": "price_complex",
    "STRIPE_PRICE_PHPSHIELD_MAINTENANCE": "price_maint",
}


class FakeStripe:
    """Session creation is faked; signature verification is the REAL stripe library."""

    def __init__(self):
        self.sessions = []
        self._real = billing.StripeGateway()

    fail = False

    def create_session(self, **params):
        if self.fail:
            raise RuntimeError("stripe is down")
        self.sessions.append(params)
        return {"id": f"cs_test_{len(self.sessions)}", "url": f"https://checkout.stripe.test/c/{len(self.sessions)}"}

    def construct_event(self, payload, sig, secret):
        return self._real.construct_event(payload, sig, secret)


@pytest.fixture(autouse=True)
def _env(monkeypatch, tmp_path):
    for k, v in ENV.items():
        monkeypatch.setenv(k, v)
    for k in ("TURNSTILE_SECRET", "SLACK_WEBHOOK_URL", "RENDER", "RESEND_API_KEY"):
        monkeypatch.delenv(k, raising=False)
    monkeypatch.setenv("PHP_SHIELD_DEAD_LETTER_PATH", str(tmp_path / "dead.jsonl"))


@pytest.fixture
def svc():
    store, mailer = MemoryStore(), OutboxMailer()
    s = services.Services(store=store, mailer=mailer, alerter=Alerter(mailer), limiter=RateLimiter(store),
                          simple_limiter=SimpleLimiter(), stripe=FakeStripe())
    services.init_services(s)
    yield s
    services._services = None


@pytest.fixture
def client(svc):
    from app.php_shield_main import create_app

    return TestClient(create_app(), raise_server_exceptions=False)


@pytest.fixture
def fake_network(monkeypatch):
    """Canned DNS + HTTP so scans exercise the REAL scanner/netsafe pipeline without a network."""
    state = {"headers": {"x-powered-by": "PHP/7.4.33", "content-type": "text/html"}, "calls": []}
    monkeypatch.setattr(netsafe, "default_resolver", lambda host, port: [PUBLIC_IP])

    def transport(ip, target, headers, deadline, max_bytes):
        state["calls"].append((ip, target.host, target.path))
        return netsafe.Response(status=200, headers=dict(state["headers"]), body="<html></html>")

    monkeypatch.setattr(netsafe, "default_transport", transport)
    return state


def sign_webhook(event: dict, secret: str = WEBHOOK_SECRET, ts: int | None = None):
    payload = json.dumps(event).encode()
    t = ts or int(time.time())
    sig = hmac.new(secret.encode(), f"{t}.".encode() + payload, hashlib.sha256).hexdigest()
    return payload, {"Stripe-Signature": f"t={t},v1={sig}", "Content-Type": "application/json"}


def make_lead(svc, domain="example.com", version="7.4.33", wordpress=False, email="cust@example.com"):
    from app.php_shield.scanner import ScanResult
    from app.php_shield.php_version_db import risk_report

    scan = ScanResult(url=f"https://{domain}", domain=domain, php_detected=True, version=version, confidence="high",
                      evidence=["/: X-Powered-By: PHP/" + version], risk=risk_report(version), wordpress=wordpress,
                      scanned_at="2026-10-24T00:00:00+00:00").to_dict()
    return svc.store.insert("leads", {"report_token": f"rt_{domain}_{uuid.uuid4().hex[:8]}", "url": scan["url"], "domain": domain,
                                      "contact_email": email, "consent_scan": True, "consent_text": "x",
                                      "php_version": version, "risk_level": scan["risk"]["risk_level"],
                                      "confidence": "high", "scan": scan, "status": "new"})


def paid_order(svc, domain="example.com", tier="standard", maintenance=False):
    """An order that has been through checkout + the real webhook."""
    from app.php_shield import orders

    lead = make_lead(svc, domain)
    order = orders.create_order(svc, lead, tier, maintenance)
    return orders.mark_paid(svc, order, customer_id="cus_1", subscription_id="sub_1" if maintenance else None,
                            session_id="cs_1", amount_total=order["amount_cents"])


INTAKE = {"site_url": "https://example.com", "hosting_provider": "Bluehost", "access_method": "sftp",
          "has_staging_or_backup": "backup exists", "preferred_timing": "this week", "contact_name": "Pat Owner",
          "contact_email": "pat@example.com"}
