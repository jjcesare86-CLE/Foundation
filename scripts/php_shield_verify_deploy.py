"""
Verify a deployed php-shield-api in about 10 seconds.

    python scripts/php_shield_verify_deploy.py https://php-shield-api.onrender.com

Makes only harmless requests: it never scans a real site, never creates an order, and every
"attack" request it sends is one the service must REJECT. Exit code 0 = all checks passed.
"""
import argparse
import sys

import requests

SITE = "https://automaitionnation.com"


def run(base: str, site: str = SITE, get=requests.get, post=requests.post, options=requests.options) -> list[tuple[bool, str, str]]:
    base = base.rstrip("/")
    out = []

    def check(name, ok, detail=""):
        out.append((bool(ok), name, detail))

    try:
        r = get(f"{base}/health", timeout=20)
        body = r.json()
        miss = body.get("config", {}).get("missing", [])
        check("/health is 200 (config complete, database reachable)", r.status_code == 200 and body.get("ok"),
              f"HTTP {r.status_code}; missing={miss}; db={body.get('database')}")
        check("running in production mode", body.get("environment") == "production", f"environment={body.get('environment')}")
        check("Stripe is in the mode you expect", body.get("stripe", {}).get("configured"), f"mode={body.get('stripe', {}).get('mode')}")
        check("email (Resend) configured", body.get("email", {}).get("configured") and body.get("email", {}).get("owner_set"))
        for w in body.get("config", {}).get("warnings", []):
            check(f"warning: {w}", True)
    except Exception as e:  # noqa: BLE001
        check("/health reachable", False, f"{type(e).__name__}: {e}")
        return out

    t = get(f"{base}/php-shield/tiers", timeout=20).json()
    check("tiers are $300 / $750 / $1,500 + $99/mo",
          [x["price_cents"] for x in t["tiers"]] == [30000, 75000, 150000] and t["maintenance"]["price_cents"] == 9900)

    pre = options(f"{base}/php-shield/scan", headers={"Origin": site, "Access-Control-Request-Method": "POST",
                                                       "Access-Control-Request-Headers": "content-type"}, timeout=20)
    check(f"CORS allows {site}", pre.headers.get("access-control-allow-origin") == site, str(pre.headers.get("access-control-allow-origin")))
    bad = options(f"{base}/php-shield/scan", headers={"Origin": "https://evil.example", "Access-Control-Request-Method": "POST"}, timeout=20)
    check("CORS rejects other origins", "access-control-allow-origin" not in bad.headers)

    body = {"email": "verify@example.com", "consent": True, "company_website": ""}
    for url in ("http://169.254.169.254/latest/meta-data/", "http://127.0.0.1/", "http://2130706433/", "http://[::1]/"):
        r = post(f"{base}/php-shield/scan", json={**body, "url": url}, timeout=20)
        check(f"SSRF blocked: {url}", r.status_code == 400, f"HTTP {r.status_code}")
    r = post(f"{base}/php-shield/scan", json={**body, "url": "https://example.com", "company_website": "bot"}, timeout=20)
    check("honeypot rejects bots", r.status_code == 400)
    r = post(f"{base}/php-shield/scan", json={**body, "url": "https://example.com", "consent": False}, timeout=20)
    check("scan requires the consent checkbox", r.status_code == 400)

    r = post(f"{base}/php-shield/stripe/webhook", data=b"{}", headers={"Stripe-Signature": "t=1,v1=bad"}, timeout=20)
    check("webhook rejects an unsigned/forged call (400, not 503 = secret is configured)", r.status_code == 400, f"HTTP {r.status_code}")

    r = get(f"{base}/php-shield/admin/orders", timeout=20)
    check("admin API requires the key", r.status_code == 403, f"HTTP {r.status_code}")
    r = get(f"{base}/php-shield/order/not-a-real-token", timeout=20)
    check("unknown order token is 404", r.status_code == 404)
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("base_url")
    ap.add_argument("--site", default=SITE, help=f"marketing site origin to test CORS against (default {SITE})")
    args = ap.parse_args(argv)
    results = run(args.base_url, args.site)
    for ok, name, detail in results:
        print(("PASS  " if ok else "FAIL  ") + name + (f"   [{detail}]" if detail and not ok else ""))
    failed = [r for r in results if not r[0]]
    print(f"\n{len(results) - len(failed)}/{len(results)} checks passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
