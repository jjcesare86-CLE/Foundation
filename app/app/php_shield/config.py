"""
PHP Shield -- environment configuration and startup validation.

PHP Shield runs as its OWN service (app.php_shield_main) with its OWN Supabase
project. Nothing here imports the rest of Foundation (app.database / app.main),
so a missing PHP Shield var can never take Foundation down, and vice versa.
"""
import os
from dataclasses import dataclass

SITE_URL_DEFAULT = "https://automaitionnation.com"

# name -> why it is required in production
REQUIRED_IN_PRODUCTION = {
    "PHP_SHIELD_SUPABASE_URL": "PHP Shield's own Supabase project URL",
    "PHP_SHIELD_SUPABASE_SERVICE_ROLE_KEY": "service-role key for that project (leads, orders, authorizations)",
    "STRIPE_SECRET_KEY": "Stripe API key (checkout)",
    "STRIPE_WEBHOOK_SECRET": "Stripe webhook signing secret (payment confirmation)",
    "STRIPE_PRICE_PHPSHIELD_BASIC": "Stripe price id, Basic Fix $300",
    "STRIPE_PRICE_PHPSHIELD_STANDARD": "Stripe price id, Standard Fix $750",
    "STRIPE_PRICE_PHPSHIELD_COMPLEX": "Stripe price id, Complex Fix $1,500",
    "STRIPE_PRICE_PHPSHIELD_MAINTENANCE": "Stripe price id, Maintenance $99/mo",
    "RESEND_API_KEY": "Resend key (customer + owner emails)",
    "PHP_SHIELD_OWNER_EMAIL": "where owner notifications and alerts go",
    "PHP_SHIELD_ADMIN_API_KEY": "gates the admin endpoints/page",
    "PHP_SHIELD_IP_HASH_SALT": "salt for hashing client IPs in rate-limit and lead records",
}

# The monthly rescan cron only reads the database and sends email.
CRON_REQUIRED = ("PHP_SHIELD_SUPABASE_URL", "PHP_SHIELD_SUPABASE_SERVICE_ROLE_KEY", "RESEND_API_KEY", "PHP_SHIELD_OWNER_EMAIL")

OPTIONAL = {
    "PHP_SHIELD_SITE_URL": f"public marketing site (default {SITE_URL_DEFAULT})",
    "PHP_SHIELD_FROM_EMAIL": "From address, must be on a Resend-verified domain",
    "PHP_SHIELD_ALLOWED_ORIGINS": "comma-separated CORS origins (default: the marketing site)",
    "TURNSTILE_SECRET": "enables Cloudflare Turnstile on /scan when set",
    "SLACK_WEBHOOK_URL": "extra alert channel (Slack or Discord-compatible webhook)",
    "PHP_SHIELD_DEAD_LETTER_PATH": "local fallback file for failed writes",
}


def env(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


def is_production() -> bool:
    return (
        env("PHP_SHIELD_ENV").lower() == "production"
        or bool(env("RENDER"))  # Render sets RENDER=true on every service
    )


def site_url() -> str:
    return env("PHP_SHIELD_SITE_URL", SITE_URL_DEFAULT).rstrip("/")


def owner_email() -> str:
    return env("PHP_SHIELD_OWNER_EMAIL")


def from_email() -> str:
    return env("PHP_SHIELD_FROM_EMAIL", "PHP Shield <shield@automaitionnation.com>")


def allowed_origins() -> list[str]:
    raw = env("PHP_SHIELD_ALLOWED_ORIGINS")
    if raw:
        return [o.strip() for o in raw.split(",") if o.strip()]
    origins = [site_url(), "https://www.automaitionnation.com"]
    if not is_production():
        origins += ["http://localhost:5173", "http://localhost:8080", "http://127.0.0.1:5173"]
    return sorted(set(origins))


def stripe_price_ids() -> dict[str, str]:
    return {
        "basic": env("STRIPE_PRICE_PHPSHIELD_BASIC"),
        "standard": env("STRIPE_PRICE_PHPSHIELD_STANDARD"),
        "complex": env("STRIPE_PRICE_PHPSHIELD_COMPLEX"),
        "maintenance": env("STRIPE_PRICE_PHPSHIELD_MAINTENANCE"),
    }


@dataclass
class ConfigReport:
    missing: list[str]
    warnings: list[str]

    @property
    def ok(self) -> bool:
        return not self.missing


def check(names=None) -> ConfigReport:
    missing = [n for n in (names or REQUIRED_IN_PRODUCTION) if not env(n)]
    warnings = []
    key = env("STRIPE_SECRET_KEY")
    if key and not key.startswith(("sk_", "rk_")):
        warnings.append("STRIPE_SECRET_KEY does not look like a Stripe key")
    if is_production() and key.startswith(("sk_test_", "rk_test_")):
        warnings.append("production is running with a Stripe TEST key")
    if not env("TURNSTILE_SECRET"):
        warnings.append("TURNSTILE_SECRET unset: bot challenge disabled (honeypot + rate limits still active)")
    return ConfigReport(missing=missing, warnings=warnings)


def validate_startup(names=None) -> ConfigReport:
    """Fail loudly. In production a missing required var refuses to boot."""
    report = check(names)
    if report.missing and is_production():
        lines = "\n".join(f"  - {n}: {REQUIRED_IN_PRODUCTION[n]}" for n in report.missing)
        raise RuntimeError(f"PHP Shield refusing to start: missing required environment variables:\n{lines}")
    return report
