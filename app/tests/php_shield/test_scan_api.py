"""/scan, /report, /tiers, /quote, /checkout and the abuse controls around them."""
import pytest

from app.php_shield import tiers
from tests.php_shield.conftest import make_lead

GOOD = {"url": "https://example.com", "email": "me@example.com", "consent": True, "company_website": ""}


def post_scan(client, **over):
    return client.post("/php-shield/scan", json={**GOOD, **over}, headers={"x-forwarded-for": "203.0.113.9"})


def test_successful_scan_stores_consenting_lead_and_returns_token(client, svc, fake_network):
    r = post_scan(client)
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["version"] == "7.4.33" and body["risk"]["risk_level"] == "critical" and body["report_token"]
    lead = svc.store.select("leads")[0]
    assert lead["consent_scan"] is True and "authorized to scan" in lead["consent_text"]
    assert lead["contact_email"] == "me@example.com" and lead["ip_hash"] and "203.0.113.9" not in lead["ip_hash"]
    # three probes, all pinned to the validated public IP
    assert [c[2] for c in fake_network["calls"]] == ["/", "/wp-login.php", "/readme.html"]
    assert {c[0] for c in fake_network["calls"]} == {"93.184.216.34"}


def test_honeypot_blocks_bots_without_scanning(client, svc, fake_network):
    assert post_scan(client, company_website="http://spam.example").status_code == 400
    assert not fake_network["calls"] and not svc.store.select("leads")


def test_consent_is_required(client, fake_network):
    assert post_scan(client, consent=False).status_code == 400
    assert client.post("/php-shield/scan", json={"url": "https://example.com", "email": "a@b.co"}).status_code == 422
    assert not fake_network["calls"]


@pytest.mark.parametrize("email", ["", "nope", "a@b", "a b@c.com"])
def test_email_validated(client, fake_network, email):
    assert post_scan(client, email=email).status_code == 400


@pytest.mark.parametrize("url", [
    "http://127.0.0.1/", "http://localhost/", "http://169.254.169.254/latest/meta-data/", "http://2130706433/",
    "http://0x7f000001/", "http://[::1]/", "http://[::ffff:127.0.0.1]/", "http://10.0.0.1:80/", "ftp://example.com/",
    "http://user:pw@example.com/", "https://example.com:8443/", "file:///etc/passwd", "http://metadata.google.internal/",
])
def test_ssrf_urls_rejected_before_any_network_or_rate_limit_use(client, svc, fake_network, url):
    r = post_scan(client, url=url)
    assert r.status_code == 400
    assert not fake_network["calls"]
    assert not svc.store.select("scan_events")  # rejected before consuming a rate-limit slot


def test_hostname_that_resolves_internal_is_blocked(client, svc, monkeypatch, fake_network):
    from app.php_shield import netsafe

    monkeypatch.setattr(netsafe, "default_resolver", lambda h, p: ["169.254.169.254"])
    r = post_scan(client, url="https://innocent-looking.example.com")
    assert r.status_code == 400 and not fake_network["calls"]


def test_rate_limit_per_ip_returns_429_with_retry_after(client, fake_network):
    for i in range(5):
        assert post_scan(client, url=f"https://site{i}.example.com").status_code == 200
    r = post_scan(client, url="https://site99.example.com")
    assert r.status_code == 429 and int(r.headers["Retry-After"]) > 0


def test_rate_limit_per_domain(client, fake_network):
    for i in range(3):
        r = client.post("/php-shield/scan", json=GOOD, headers={"x-forwarded-for": f"198.51.100.{i + 1}"})
        assert r.status_code == 200
    r = client.post("/php-shield/scan", json=GOOD, headers={"x-forwarded-for": "198.51.100.77"})
    assert r.status_code == 429 and "Retry-After" in r.headers
    # www. and the apex are the same domain
    r = client.post("/php-shield/scan", json={**GOOD, "url": "https://www.example.com"}, headers={"x-forwarded-for": "198.51.100.78"})
    assert r.status_code == 429


def test_spoofed_leftmost_forwarded_for_does_not_evade_limit(client, fake_network):
    for i in range(5):
        r = client.post("/php-shield/scan", json={**GOOD, "url": f"https://s{i}.example.com"},
                        headers={"x-forwarded-for": f"6.6.6.{i}, 203.0.113.50"})
        assert r.status_code == 200
    r = client.post("/php-shield/scan", json={**GOOD, "url": "https://another.example.com"},
                    headers={"x-forwarded-for": "6.6.6.200, 203.0.113.50"})
    assert r.status_code == 429


def test_turnstile_enforced_when_configured(client, fake_network, monkeypatch):
    monkeypatch.setenv("TURNSTILE_SECRET", "s")
    assert post_scan(client).status_code == 400  # no token
    from app.php_shield import turnstile

    monkeypatch.setattr(turnstile, "verify", lambda token, ip=None, **k: token == "good")
    assert post_scan(client, turnstile_token="bad").status_code == 400
    assert post_scan(client, turnstile_token="good").status_code == 200


def test_unreachable_site_is_a_clean_400(client, monkeypatch, fake_network):
    from app.php_shield import netsafe

    def boom(*a, **k):
        raise netsafe.FetchError("connection refused")

    monkeypatch.setattr(netsafe, "default_transport", boom)
    r = post_scan(client)
    assert r.status_code == 400 and "could not reach" in r.json()["detail"]


def test_lead_write_failure_is_loud_not_silent(client, svc, fake_network, tmp_path):
    from app.php_shield.store import StoreError

    real = svc.store.insert

    def failing(table, row):
        if table == "leads":
            raise StoreError("db down")
        return real(table, row)

    svc.store.insert = failing
    r = post_scan(client)
    assert r.status_code == 503  # not a fake success
    dead = (tmp_path / "dead.jsonl").read_text()
    assert '"kind": "lead"' in dead and "me@example.com" in dead  # payload preserved for follow-up
    alerts = [m for m in svc.mailer.sent if "ALERT" in m["subject"]]
    assert alerts and alerts[0]["to"] == ["owner@example.com"]


# -- report / tiers / quote / checkout -------------------------------------------

def test_report_has_recommendation_tiers_and_maintenance(client, svc):
    lead = make_lead(svc)
    r = client.get(f"/php-shield/report/{lead['report_token']}")
    body = r.json()
    assert r.status_code == 200 and body["recommendation"]["tier"] in ("basic", "standard", "complex")
    assert [t["key"] for t in body["tiers"]] == ["basic", "standard", "complex"]
    assert [t["price_cents"] for t in body["tiers"]] == [30000, 75000, 150000]
    assert body["maintenance"]["price_cents"] == 9900
    assert client.get("/php-shield/report/nope").status_code == 404


def test_tier_recommendation_is_driven_by_config():
    base = {"php_detected": True, "version": "x"}
    from app.php_shield.php_version_db import risk_report

    def rec(v, wp=False):
        return tiers.recommend({**base, "wordpress": wp, "risk": risk_report(v)})

    assert rec("8.3.1")["tier"] == "basic"           # supported-ish, one branch behind
    assert rec("7.4.33")["tier"] == "standard"       # critical + 5 behind
    assert rec("5.6.40")["tier"] == "complex"        # critical + 10 behind
    assert rec("8.1.2")["tier"] in ("basic", "standard")
    assert rec("7.4.33", wp=True)["score"] == rec("7.4.33")["score"] + 1
    unknown = tiers.recommend({"php_detected": False, "version": None, "risk": None})
    assert unknown["tier"] is None and unknown["custom_quote"] is True


def test_thresholds_live_in_yaml_not_code(monkeypatch):
    cfg = tiers._cfg()
    monkeypatch.setitem(cfg["thresholds"], "basic_max_score", 99)
    from app.php_shield.php_version_db import risk_report

    assert tiers.recommend({"php_detected": True, "version": "5.6.40", "wordpress": True, "risk": risk_report("5.6.40")})["tier"] == "basic"


def test_quote_request_creates_flagged_lead_and_emails_owner(client, svc):
    lead = make_lead(svc)
    r = client.post("/php-shield/quote", json={"report_token": lead["report_token"], "notes": "custom theme"})
    assert r.status_code == 200
    stored = svc.store.select("leads", id=lead["id"])[0]
    assert stored["quote_requested"] is True and stored["quote_notes"] == "custom theme"
    assert any("quote" in m["subject"].lower() for m in svc.mailer.sent)


def test_checkout_tier_only_is_one_time_payment(client, svc):
    lead = make_lead(svc)
    r = client.post("/php-shield/checkout", json={"report_token": lead["report_token"], "tier": "standard", "maintenance": False})
    assert r.status_code == 200 and r.json()["checkout_url"].startswith("https://checkout.stripe.test/")
    p = svc.stripe.sessions[0]
    assert p["mode"] == "payment" and p["line_items"] == [{"price": "price_standard", "quantity": 1}]
    order = svc.store.select("orders")[0]
    assert order["status"] == "pending_payment" and order["amount_cents"] == 75000
    assert p["client_reference_id"] == order["id"] and p["metadata"]["order_id"] == order["id"]
    assert p["success_url"] == f"https://site.test/php-shield/order/{order['public_token']}?paid=1"


def test_checkout_with_maintenance_is_subscription_mode(client, svc):
    lead = make_lead(svc)
    client.post("/php-shield/checkout", json={"report_token": lead["report_token"], "tier": "basic", "maintenance": True})
    p = svc.stripe.sessions[0]
    assert p["mode"] == "subscription"
    assert [i["price"] for i in p["line_items"]] == ["price_basic", "price_maint"]
    assert p["subscription_data"]["metadata"]["order_id"]
    assert svc.store.select("orders")[0]["amount_cents"] == 39900


def test_checkout_maintenance_standalone(client, svc):
    lead = make_lead(svc)
    r = client.post("/php-shield/checkout", json={"report_token": lead["report_token"], "tier": None, "maintenance": True})
    assert r.status_code == 200 and svc.store.select("orders")[0]["tier"] is None


def test_checkout_validation(client, svc, monkeypatch):
    lead = make_lead(svc)
    t = lead["report_token"]
    assert client.post("/php-shield/checkout", json={"report_token": t, "tier": None, "maintenance": False}).status_code == 400
    assert client.post("/php-shield/checkout", json={"report_token": "bad", "tier": "basic"}).status_code == 404
    monkeypatch.delenv("STRIPE_PRICE_PHPSHIELD_BASIC")
    assert client.post("/php-shield/checkout", json={"report_token": t, "tier": "basic"}).status_code == 503


def test_unknown_tier_rejected(client, svc):
    lead = make_lead(svc)
    r = client.post("/php-shield/checkout", json={"report_token": lead["report_token"], "tier": "platinum", "maintenance": False})
    assert r.status_code == 400 and not svc.stripe.sessions and not svc.store.select("orders")


def test_stripe_failure_is_a_clean_502_alerts_owner_and_leaves_no_orphan_order(client, svc):
    lead = make_lead(svc)
    svc.stripe.fail = True
    r = client.post("/php-shield/checkout", json={"report_token": lead["report_token"], "tier": "basic", "maintenance": False})
    assert r.status_code == 502 and "stripe is down" not in r.text
    assert [o["status"] for o in svc.store.select("orders")] == ["canceled"]
    assert any("Stripe checkout creation failed" in m["subject"] for m in svc.mailer.sent)
