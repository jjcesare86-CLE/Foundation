# php_shield (code map)

Standalone service: `app.php_shield_main:app`. Imports nothing from `app.main` / `app.database`.

| Module | Responsibility |
|---|---|
| `config.py` | env vars, `REQUIRED_IN_PRODUCTION`, `validate_startup()` (refuse to boot in production) |
| `netsafe.py` | **all outbound fetches of user-supplied URLs**: URL policy, DNS check, IP pinning, per-hop redirect re-validation, size/time/content-type caps |
| `scanner.py` | passive PHP fingerprinting through `netsafe.fetch` |
| `php_version_db.py` | PHP end-of-life dates, risk levels, example CVEs |
| `ratelimit.py` | per-IP / per-domain / global / concurrency limits (backed by `scan_events`) |
| `turnstile.py` | optional Cloudflare Turnstile (`TURNSTILE_SECRET`) |
| `tiers.py`, `tiers.yaml`, `delivery_checklist.yaml` | prices, recommendation scoring/thresholds, delivery checklist — **edit the YAML, not code** |
| `billing.py` | Stripe Checkout + idempotent webhooks |
| `orders.py` | order state machine and the **fulfillment gate**, intake, signing, delivery |
| `agreement.py`, `pdf.py` | the authorization agreement (DRAFT) and its signed PDF |
| `verification.py` | domain ownership (DNS TXT or `/.well-known/phpshield-verify.txt`) |
| `maintenance.py` | monthly rescans (only for orders still authorized + verified) |
| `notify.py`, `emailer.py` | owner/customer email via Resend |
| `ops.py` | guarded writes (log + dead-letter + alert + 503), rate-limited alerts, self-test, health |
| `store.py` | `SupabaseStore` (production) / `MemoryStore` (tests, local dev) |
| `api.py` | HTTP routes: public, customer (order token), admin (`X-Admin-Key`), Stripe webhook |

Status flow: `pending_payment -> paid -> intake_complete -> authorized -> verified -> in_progress -> delivered -> closed`
(`canceled` from any pre-work state). The gate — a signed, unrevoked authorization for the same order **and** domain,
verified ownership, and payment before `in_progress` — is enforced in `orders.py` **and** again by triggers in
`supabase-php-shield/migrations/20261024000003_php_shield_guards.sql`.

Safety rule for contributors: never call `requests`/`httpx` on a user-supplied URL directly. Use `netsafe.fetch`.
