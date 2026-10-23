"""
Create PHP Shield's Stripe products and prices, then print the env vars to set.

    python scripts/create_stripe_products.py            # TEST mode (default; needs an sk_test_ key)
    python scripts/create_stripe_products.py --live     # LIVE mode (needs an sk_live_ key)
    python scripts/create_stripe_products.py --dry-run  # show what would be created, call nothing

Amounts come from app/app/php_shield/tiers.yaml (the same file the site shows prices from), so
the two cannot drift. The key is read from the STRIPE_SECRET_KEY environment variable only.

Safe to re-run: prices are looked up by `lookup_key` first. If a price already exists with the
same amount it is reused; if you changed the amount in tiers.yaml a new price is created and the
lookup key moves to it (old subscribers keep the old price).
"""
import argparse
import os
import sys
from pathlib import Path

import yaml

TIERS_YAML = Path(__file__).resolve().parents[1] / "app" / "app" / "php_shield" / "tiers.yaml"
LOOKUP_VERSION = "v1"

# env var -> (tiers.yaml section, key, product name, recurring?)
PLAN = [
    ("STRIPE_PRICE_PHPSHIELD_BASIC", "tiers", "basic", "PHP Shield - Basic Fix", False),
    ("STRIPE_PRICE_PHPSHIELD_STANDARD", "tiers", "standard", "PHP Shield - Standard Fix", False),
    ("STRIPE_PRICE_PHPSHIELD_COMPLEX", "tiers", "complex", "PHP Shield - Complex Fix", False),
    ("STRIPE_PRICE_PHPSHIELD_MAINTENANCE", "maintenance", None, "PHP Shield - Maintenance Plan", True),
]


def money(cents: int) -> str:
    return f"${cents / 100:,.2f}"


def load_amounts(path: Path = TIERS_YAML) -> dict:
    cfg = yaml.safe_load(path.read_text(encoding="utf-8"))
    out = {}
    for env_name, section, key, name, recurring in PLAN:
        item = cfg[section][key] if key else cfg[section]
        out[env_name] = {"name": name, "description": item["description"], "amount": int(item["price_cents"]),
                         "recurring": recurring, "lookup_key": f"phpshield_{key or 'maintenance'}_{LOOKUP_VERSION}",
                         "meta_key": key or "maintenance"}
    return out


def ensure_price(stripe, spec: dict) -> tuple[str, str]:
    """Returns (price_id, 'reused'|'created')."""
    existing = stripe.Price.list(lookup_keys=[spec["lookup_key"]], active=True, limit=1).data
    if existing and existing[0]["unit_amount"] == spec["amount"] and bool(existing[0].get("recurring")) == spec["recurring"]:
        return existing[0]["id"], "reused"
    product_id = existing[0]["product"] if existing else None
    if product_id is None:
        product_id = stripe.Product.create(name=spec["name"], description=spec["description"],
                                           metadata={"phpshield_key": spec["meta_key"]})["id"]
    params = {"product": product_id, "unit_amount": spec["amount"], "currency": "usd", "lookup_key": spec["lookup_key"],
              "transfer_lookup_key": True, "metadata": {"phpshield_key": spec["meta_key"]}}
    if spec["recurring"]:
        params["recurring"] = {"interval": "month"}
    return stripe.Price.create(**params)["id"], "created"


def main(argv=None, stripe_module=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--live", action="store_true", help="use LIVE mode (default is test mode)")
    ap.add_argument("--dry-run", action="store_true", help="print the plan; make no Stripe calls")
    args = ap.parse_args(argv)
    specs = load_amounts()

    if args.dry_run:
        print(f"# DRY RUN ({'live' if args.live else 'test'} mode) - nothing will be created\n")
        for s in specs.values():
            print(f"{s['name']:<34} {money(s['amount']):>9}{' /month' if s['recurring'] else ' one-time'}   lookup_key={s['lookup_key']}")
        return 0

    key = os.getenv("STRIPE_SECRET_KEY", "").strip()
    want = "sk_live_" if args.live else "sk_test_"
    if not key:
        print("STRIPE_SECRET_KEY is not set.", file=sys.stderr)
        return 2
    if not key.startswith((want, want.replace("sk_", "rk_"))):
        print(f"Refusing: --live={args.live} needs a {want}... key, but STRIPE_SECRET_KEY looks like "
              f"{'a live' if 'live' in key[:8] else 'a test'} key.", file=sys.stderr)
        return 2

    if stripe_module is None:
        import stripe as stripe_module
    stripe_module.api_key = key

    print(f"Stripe {'LIVE' if args.live else 'TEST'} mode\n")
    results = {}
    for env_name, spec in specs.items():
        price_id, action = ensure_price(stripe_module, spec)
        results[env_name] = price_id
        print(f"  {action:<8} {spec['name']:<32} {money(spec['amount']):>9}  {price_id}")

    print("\nSet these environment variables (Render -> php-shield-api -> Environment):\n")
    for env_name, price_id in results.items():
        print(f"{env_name}={price_id}")
    print("\nPowerShell (local):")
    for env_name, price_id in results.items():
        print(f'  $env:{env_name} = "{price_id}"')
    return 0


if __name__ == "__main__":
    sys.exit(main())
