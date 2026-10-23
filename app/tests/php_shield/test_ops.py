"""Startup validation, /health, alerts, dead letters, self-test, PDF."""
import json

import pytest
from fastapi.testclient import TestClient

from app.php_shield import config
from app.php_shield.emailer import MailError, OutboxMailer
from app.php_shield.ops import Alerter, WriteFailed, dead_letter, guarded_write, startup_selftest
from app.php_shield.pdf import signed_agreement_pdf
from app.php_shield.store import MemoryStore, StoreError


# -- startup validation ---------------------------------------------------------

def test_production_refuses_to_boot_when_required_config_is_missing(monkeypatch):
    monkeypatch.setenv("PHP_SHIELD_ENV", "production")
    for name in config.REQUIRED_IN_PRODUCTION:
        monkeypatch.delenv(name, raising=False)
    with pytest.raises(RuntimeError) as e:
        config.validate_startup()
    msg = str(e.value)
    assert "refusing to start" in msg
    for must in ("PHP_SHIELD_SUPABASE_SERVICE_ROLE_KEY", "STRIPE_SECRET_KEY", "STRIPE_WEBHOOK_SECRET", "RESEND_API_KEY"):
        assert must in msg


def test_render_env_counts_as_production(monkeypatch):
    monkeypatch.delenv("PHP_SHIELD_ENV")
    monkeypatch.setenv("RENDER", "true")
    assert config.is_production()
    monkeypatch.delenv("PHP_SHIELD_SUPABASE_URL", raising=False)
    with pytest.raises(RuntimeError):
        config.validate_startup()


def test_development_boots_but_reports_what_is_missing(monkeypatch):
    monkeypatch.delenv("PHP_SHIELD_SUPABASE_SERVICE_ROLE_KEY", raising=False)
    rep = config.validate_startup()
    assert "PHP_SHIELD_SUPABASE_SERVICE_ROLE_KEY" in rep.missing and not rep.ok


def test_production_fully_configured_boots(monkeypatch):
    monkeypatch.setenv("PHP_SHIELD_ENV", "production")
    for name in config.REQUIRED_IN_PRODUCTION:
        monkeypatch.setenv(name, "x")
    assert config.validate_startup().ok


def test_cors_defaults_to_marketing_site_and_not_localhost_in_production(monkeypatch):
    monkeypatch.delenv("PHP_SHIELD_ALLOWED_ORIGINS", raising=False)
    monkeypatch.setenv("PHP_SHIELD_SITE_URL", "https://automaitionnation.com")
    assert "https://automaitionnation.com" in config.allowed_origins()
    monkeypatch.setenv("PHP_SHIELD_ENV", "production")
    assert not any("localhost" in o for o in config.allowed_origins())


# -- /health ----------------------------------------------------------------------

def test_health_ok_reports_config_and_db_without_secrets(client, svc, monkeypatch):
    for name in config.REQUIRED_IN_PRODUCTION:
        monkeypatch.setenv(name, "x")
    r = client.get("/health")
    body = r.json()
    assert r.status_code == 200 and body["ok"] and body["database"]["ok"]
    assert body["config"]["missing"] == [] and body["stripe"]["configured"]
    assert "sk_test_123" not in r.text and "x" * 3 not in json.dumps(body["config"])


def test_health_503_when_config_missing_or_db_down(client, svc, monkeypatch):
    r = client.get("/health")  # dev env: several required vars unset
    assert r.status_code == 503 and "PHP_SHIELD_SUPABASE_URL" in r.json()["config"]["missing"]
    for name in config.REQUIRED_IN_PRODUCTION:
        monkeypatch.setenv(name, "x")
    svc.store.select_since = lambda *a, **k: (_ for _ in ()).throw(StoreError("connection refused"))
    r = client.get("/health")
    assert r.status_code == 503 and r.json()["database"]["ok"] is False


def test_health_503_when_services_not_initialised(monkeypatch):
    from app.php_shield import services
    from app.php_shield_main import create_app

    services._services = None
    assert TestClient(create_app()).get("/health").status_code == 503


# -- alerts ---------------------------------------------------------------------------

def test_alerts_email_owner_and_ping_webhook(monkeypatch):
    monkeypatch.setenv("SLACK_WEBHOOK_URL", "https://hooks.example/abc")
    mailer, posted = OutboxMailer(), []
    a = Alerter(mailer, post=lambda url, **kw: posted.append((url, kw["json"])))
    assert a.alert("k1", "Something broke", "details <b>here</b>")
    assert mailer.sent[0]["to"] == ["owner@example.com"] and "&lt;b&gt;" in mailer.sent[0]["html"]  # escaped
    assert posted and posted[0][0] == "https://hooks.example/abc" and "Something broke" in posted[0][1]["text"]


def test_alerts_are_rate_limited_per_key_and_globally():
    mailer = OutboxMailer()
    a = Alerter(mailer, min_interval=600, max_per_hour=3)
    assert a.alert("same", "s", "b")
    assert not a.alert("same", "s", "b") and not a.alert("same", "s", "b")  # suppressed, no spam
    assert a.suppressed == 2 and len(mailer.sent) == 1
    assert a.alert("k2", "s", "b") and a.alert("k3", "s", "b")
    assert not a.alert("k4", "s", "b")  # hourly cap of 3
    assert len(mailer.sent) == 3


def test_alerter_never_raises_even_if_everything_is_down(monkeypatch):
    monkeypatch.setenv("SLACK_WEBHOOK_URL", "https://hooks.example/abc")

    class Down:
        def send(self, *a, **k):
            raise MailError("resend down")

    def boom(*a, **k):
        raise RuntimeError("slack down")

    assert Alerter(Down(), post=boom).alert("k", "s", "b") is False


# -- guarded writes / dead letters ----------------------------------------------------

def test_guarded_write_logs_persists_alerts_and_raises(svc, tmp_path):
    def failing():
        raise StoreError("insert failed: relation does not exist")

    with pytest.raises(WriteFailed) as e:
        guarded_write(svc, "order", {"email": "c@example.com", "tier": "basic"}, failing, {"lead": "L1"})
    assert e.value.kind == "order"
    line = json.loads((tmp_path / "dead.jsonl").read_text().splitlines()[-1])
    assert line["kind"] == "order" and line["payload"]["email"] == "c@example.com" and "relation does not exist" in line["error"]
    assert svc.store.select("dead_letters")[0]["kind"] == "order"  # table copy too (DB was up)
    assert [m for m in svc.mailer.sent if "ALERT" in m["subject"] and "order write FAILED" in m["subject"]]


def test_dead_letter_still_works_when_the_database_is_the_thing_that_broke(tmp_path):
    class Dead(MemoryStore):
        def insert(self, *a, **k):
            raise StoreError("db down")

    dead_letter("lead", {"email": "x@y.com"}, "db down", store=Dead())  # must not raise
    assert "x@y.com" in (tmp_path / "dead.jsonl").read_text()


def test_successful_write_passes_through(svc):
    assert guarded_write(svc, "x", {}, lambda: 42) == 42 and not svc.mailer.sent


def test_failed_customer_email_is_recorded_not_swallowed(svc, tmp_path):
    from app.php_shield import notify

    class Down:
        def send(self, *a, **k):
            raise MailError("resend 500")

    svc.mailer = Down()
    svc.alerter.mailer = OutboxMailer()
    assert notify.safe_send(svc, "c@example.com", "hi", "<p>x</p>", kind="t") is False
    assert "resend 500" in (tmp_path / "dead.jsonl").read_text()
    assert svc.alerter.mailer.sent  # owner alerted via the (working) alert path


# -- self-test ---------------------------------------------------------------------------

def test_startup_selftest_writes_then_deletes():
    store = MemoryStore()
    startup_selftest(store)
    assert store.select("health_checks") == []


def test_startup_selftest_fails_loudly():
    class Dead(MemoryStore):
        def insert(self, *a, **k):
            raise StoreError("permission denied for table health_checks")

    with pytest.raises(StoreError):
        startup_selftest(Dead())


def test_lifespan_refuses_boot_in_production_when_selftest_fails(monkeypatch):
    from app.php_shield import services
    from app.php_shield_main import create_app

    monkeypatch.setenv("PHP_SHIELD_ENV", "production")
    for name in config.REQUIRED_IN_PRODUCTION:
        monkeypatch.setenv(name, "x")

    class Dead(MemoryStore):
        def insert(self, *a, **k):
            raise StoreError("db unreachable")

    store, mailer = Dead(), OutboxMailer()
    monkeypatch.setattr(services, "build_default", lambda: services.Services(
        store=store, mailer=mailer, alerter=Alerter(mailer), limiter=None, simple_limiter=None))
    with pytest.raises(RuntimeError, match="self-test failed"):
        with TestClient(create_app()):
            pass


# -- PDF -------------------------------------------------------------------------------------

def test_pdf_is_a_valid_pdf_and_regenerates_identically(client, svc):
    from tests.php_shield.test_fulfillment import through_authorization

    o = through_authorization(client, svc)
    auth = svc.store.select("authorizations", order_id=o["id"])[0]
    a, b = signed_agreement_pdf(auth, o), signed_agreement_pdf(auth, o)
    assert a.startswith(b"%PDF") and a.rstrip().endswith(b"%%EOF") and len(a) > 2000
    assert a == b  # deterministic: the stored row fully determines the document


def test_cron_has_a_smaller_required_set(monkeypatch):
    monkeypatch.setenv("PHP_SHIELD_ENV", "production")
    for name in config.REQUIRED_IN_PRODUCTION:
        monkeypatch.delenv(name, raising=False)
    for name in config.CRON_REQUIRED:
        monkeypatch.setenv(name, "x")
    assert config.validate_startup(config.CRON_REQUIRED).ok  # no Stripe/admin/salt needed
    with pytest.raises(RuntimeError):
        config.validate_startup()  # but the API itself still demands everything


def test_render_blueprint_declares_every_required_var_for_the_api():
    import pathlib
    import yaml

    d = yaml.safe_load((pathlib.Path(__file__).parents[2] / "render.yaml").read_text(encoding="utf-8"))
    svc = {s["name"]: s for s in d["services"]}
    api_vars = {v["key"] for v in svc["php-shield-api"]["envVars"]}
    cron_vars = {v["key"] for v in svc["php-shield-monthly-rescan"]["envVars"]}
    assert set(config.REQUIRED_IN_PRODUCTION) <= api_vars, set(config.REQUIRED_IN_PRODUCTION) - api_vars
    assert set(config.CRON_REQUIRED) <= cron_vars
    assert svc["php-shield-api"]["healthCheckPath"] == "/health"
    assert "app.php_shield_main:app" in svc["php-shield-api"]["startCommand"]
