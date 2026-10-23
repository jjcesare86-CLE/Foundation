"""scripts/create_stripe_products.py with a fake Stripe module (no network, no keys)."""
import importlib.util
import pathlib

import pytest

from app.php_shield import tiers

SCRIPT = pathlib.Path(__file__).parents[3] / "scripts" / "create_stripe_products.py"
spec = importlib.util.spec_from_file_location("create_stripe_products", SCRIPT)
script = importlib.util.module_from_spec(spec)
spec.loader.exec_module(script)


class _List:
    def __init__(self, data):
        self.data = data


class FakeStripe:
    def __init__(self, existing=None):
        self.api_key = None
        self.created_prices, self.created_products = [], []
        self._existing = existing or {}
        outer = self

        class Price:
            @staticmethod
            def list(lookup_keys, active, limit):
                return _List([outer._existing[k] for k in lookup_keys if k in outer._existing])

            @staticmethod
            def create(**p):
                outer.created_prices.append(p)
                return {"id": f"price_new_{len(outer.created_prices)}"}

        class Product:
            @staticmethod
            def create(**p):
                outer.created_products.append(p)
                return {"id": f"prod_new_{len(outer.created_products)}"}

        self.Price, self.Product = Price, Product


def test_amounts_come_from_tiers_yaml_not_hardcoded():
    amounts = script.load_amounts()
    assert [a["amount"] for a in amounts.values()] == [tiers.tier_price_cents(k) for k in ("basic", "standard", "complex")] + [9900]
    assert [a["amount"] for a in amounts.values()] == [30000, 75000, 150000, 9900]
    assert [a["recurring"] for a in amounts.values()] == [False, False, False, True]


def test_test_mode_creates_products_and_prints_env_vars(monkeypatch, capsys):
    monkeypatch.setenv("STRIPE_SECRET_KEY", "sk_test_abc")
    fake = FakeStripe()
    assert script.main([], stripe_module=fake) == 0
    out = capsys.readouterr().out
    assert fake.api_key == "sk_test_abc" and len(fake.created_products) == 4 and len(fake.created_prices) == 4
    assert [p["unit_amount"] for p in fake.created_prices] == [30000, 75000, 150000, 9900]
    assert fake.created_prices[3]["recurring"] == {"interval": "month"} and "recurring" not in fake.created_prices[0]
    assert all(p["currency"] == "usd" and p["lookup_key"].startswith("phpshield_") for p in fake.created_prices)
    for name in ("BASIC", "STANDARD", "COMPLEX", "MAINTENANCE"):
        assert f"STRIPE_PRICE_PHPSHIELD_{name}=price_new_" in out
    assert "$env:STRIPE_PRICE_PHPSHIELD_BASIC" in out  # PowerShell form


def test_rerun_reuses_matching_prices(monkeypatch):
    monkeypatch.setenv("STRIPE_SECRET_KEY", "sk_test_abc")
    existing = {s["lookup_key"]: {"id": f"price_{k}", "product": f"prod_{k}", "unit_amount": s["amount"],
                                   "recurring": {"interval": "month"} if s["recurring"] else None}
                for k, s in script.load_amounts().items()}
    fake = FakeStripe(existing)
    assert script.main([], stripe_module=fake) == 0
    assert not fake.created_prices and not fake.created_products


def test_changed_amount_creates_new_price_on_same_product(monkeypatch):
    monkeypatch.setenv("STRIPE_SECRET_KEY", "sk_test_abc")
    s = script.load_amounts()["STRIPE_PRICE_PHPSHIELD_BASIC"]
    fake = FakeStripe({s["lookup_key"]: {"id": "price_old", "product": "prod_basic", "unit_amount": 25000, "recurring": None}})
    script.main([], stripe_module=fake)
    basic = fake.created_prices[0]
    assert basic["product"] == "prod_basic" and basic["unit_amount"] == 30000 and basic["transfer_lookup_key"] is True


@pytest.mark.parametrize("argv,key", [([], "sk_live_abc"), (["--live"], "sk_test_abc"), ([], ""), (["--live"], "")])
def test_refuses_wrong_mode_or_missing_key(monkeypatch, argv, key):
    monkeypatch.setenv("STRIPE_SECRET_KEY", key)
    fake = FakeStripe()
    assert script.main(argv, stripe_module=fake) == 2
    assert not fake.created_prices


def test_live_flag_with_live_key_works(monkeypatch):
    monkeypatch.setenv("STRIPE_SECRET_KEY", "sk_live_abc")
    fake = FakeStripe()
    assert script.main(["--live"], stripe_module=fake) == 0 and len(fake.created_prices) == 4


def test_dry_run_needs_no_key_and_makes_no_calls(monkeypatch, capsys):
    monkeypatch.delenv("STRIPE_SECRET_KEY", raising=False)
    assert script.main(["--dry-run"]) == 0
    out = capsys.readouterr().out
    assert "$300.00" in out and "$750.00" in out and "$1,500.00" in out and "$99.00" in out and "/month" in out


# -- webhook endpoint creation ---------------------------------------------------

WEBHOOK = "https://php-shield-api.onrender.com/php-shield/stripe/webhook"


def _with_webhooks(fake, existing=()):
    class WebhookEndpoint:
        created = []

        @staticmethod
        def list(limit):
            return _List(list(existing))

        @staticmethod
        def create(**p):
            WebhookEndpoint.created.append(p)
            return {"id": "we_new", "secret": "whsec_new_secret"}

    fake.WebhookEndpoint = WebhookEndpoint
    return WebhookEndpoint


def test_webhook_endpoint_created_with_the_three_events_and_secret_printed(monkeypatch, capsys):
    monkeypatch.setenv("STRIPE_SECRET_KEY", "sk_test_abc")
    fake = FakeStripe()
    we = _with_webhooks(fake)
    assert script.main(["--webhook-url", WEBHOOK], stripe_module=fake) == 0
    assert we.created == [{"url": WEBHOOK, "enabled_events": ["checkout.session.completed", "invoice.paid", "customer.subscription.deleted"],
                           "description": "PHP Shield"}]
    out = capsys.readouterr().out
    assert "STRIPE_WEBHOOK_SECRET=whsec_new_secret" in out and '$env:STRIPE_WEBHOOK_SECRET = "whsec_new_secret"' in out


def test_existing_webhook_endpoint_is_not_duplicated_and_user_is_told_how_to_get_the_secret(monkeypatch, capsys):
    monkeypatch.setenv("STRIPE_SECRET_KEY", "sk_test_abc")
    fake = FakeStripe()
    we = _with_webhooks(fake, existing=[{"id": "we_old", "url": WEBHOOK}])
    assert script.main(["--webhook-url", WEBHOOK], stripe_module=fake) == 0
    out = capsys.readouterr().out
    assert not we.created and "STRIPE_WEBHOOK_SECRET=" not in out and "Reveal" in out


def test_webhook_url_must_be_https(monkeypatch):
    monkeypatch.setenv("STRIPE_SECRET_KEY", "sk_test_abc")
    fake = FakeStripe()
    assert script.main(["--webhook-url", "http://insecure.example/hook"], stripe_module=fake) == 2
    assert not fake.created_prices


def test_dry_run_mentions_webhook_without_calling_stripe(monkeypatch, capsys):
    monkeypatch.delenv("STRIPE_SECRET_KEY", raising=False)
    assert script.main(["--dry-run", "--webhook-url", WEBHOOK]) == 0
    assert "would create webhook endpoint" in capsys.readouterr().out
