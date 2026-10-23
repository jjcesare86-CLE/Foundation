"""scripts/php_shield_verify_deploy.py against an in-process app (healthy and broken configs)."""
import importlib.util
import pathlib

import pytest
from fastapi.testclient import TestClient

from app.php_shield import config

SCRIPT = pathlib.Path(__file__).parents[3] / "scripts" / "php_shield_verify_deploy.py"
spec = importlib.util.spec_from_file_location("php_shield_verify_deploy", SCRIPT)
verify = importlib.util.module_from_spec(spec)
spec.loader.exec_module(verify)

SITE = "https://site.test"


@pytest.fixture
def prod_client(svc, monkeypatch):
    from app.php_shield_main import create_app

    monkeypatch.setenv("PHP_SHIELD_ENV", "production")
    monkeypatch.setenv("RESEND_API_KEY", "re_test")
    for name in config.REQUIRED_IN_PRODUCTION:
        monkeypatch.setenv(name, config.env(name) or "x")
    return TestClient(create_app())


def run(client, **kw):
    return verify.run("http://testserver", site=SITE, get=client.get, post=client.post, options=client.options, **kw)


def test_healthy_production_deployment_passes_every_check(prod_client):
    results = run(prod_client)
    failed = [(n, d) for ok, n, d in results if not ok]
    assert not failed, failed
    names = " ".join(n for _, n, _ in results)
    for must in ("/health", "SSRF blocked: http://169.254.169.254", "honeypot", "consent", "webhook rejects", "admin API", "CORS"):
        assert must in names


def test_missing_config_is_reported(prod_client, monkeypatch):
    monkeypatch.delenv("STRIPE_WEBHOOK_SECRET")
    results = run(prod_client)
    bad = {n: d for ok, n, d in results if not ok}
    assert any("/health is 200" in n for n in bad) and "STRIPE_WEBHOOK_SECRET" in str(bad)
    assert any("webhook rejects" in n for n in bad)  # 503 instead of 400: secret not configured


def test_wrong_cors_origin_is_caught(prod_client):
    results = verify.run("http://testserver", site="https://not-the-site.example", get=prod_client.get,
                         post=prod_client.post, options=prod_client.options)
    assert any(not ok and "CORS allows" in n for ok, n, _ in results)


def test_unreachable_service_fails_cleanly():
    def boom(*a, **k):
        raise ConnectionError("refused")

    results = verify.run("http://nowhere.invalid", get=boom, post=boom, options=boom)
    assert results[0][0] is False and "refused" in results[0][2]
    assert verify.main(["http://127.0.0.1:9"]) == 1  # real connection refused -> exit 1
