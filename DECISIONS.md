# PHP Shield launch — decisions

Judgement calls made while building branch `php-shield-launch` (nobody was available to ask).
Each says what to change if you disagree.

## Architecture
1. **PHP Shield is its own Render service**, `php-shield-api` (`uvicorn app.php_shield_main:app`), built from this
   repo's `app/` directory, plus a cron `php-shield-monthly-rescan`. It imports nothing from `app.main` /
   `app.database`. Why: you asked for its own Supabase project and for "refuse to boot in production if config is
   missing"; inside `foundation-api` a missing Stripe key would have taken down Switchboard. The old mount in
   `app/main.py` and `routers/php_shield.py` are removed so there is exactly one (hardened) public scan surface.
2. **Its own Supabase project.** Env: `PHP_SHIELD_SUPABASE_URL`, `PHP_SHIELD_SUPABASE_SERVICE_ROLE_KEY`. Migrations
   are in `supabase-php-shield/migrations/` (NOT `supabase/migrations/`, which belongs to Foundation's project).
   The earlier `foundation.php_shield_leads` migration in `supabase/migrations/` is left untouched because it is
   already merged; **do not apply it**, or drop that table from Foundation if it was applied.
3. **Render blueprint is `render.php-shield.yaml` at the repo root** with `rootDir: app` (a blueprint nested in
   `app/` can't build). `app/render.yaml` is unchanged. Optional vars (`TURNSTILE_SECRET`, `SLACK_WEBHOOK_URL`) are
   left out of it so Render doesn't demand a value; add them in the dashboard if wanted.
4. **Production detection** = `PHP_SHIELD_ENV=production` **or** Render's automatic `RENDER` variable. The cron
   has a smaller required set (database + email only), so you set fewer variables on it.

## Abuse and SSRF
5. **Limits** (per IP 5/h, per domain 3/day, global 500/day, 4 concurrent; env-tunable) live in a `scan_events`
   table so they survive restarts and multiple instances. If the DB is down the limiter falls back to in-memory
   counting rather than failing open.
6. **Client IP = right-most `X-Forwarded-For` entry.** Render appends the real client address; the left-most
   entries are attacker-controlled. A test proves a spoofed left-most value can't evade the limit.
7. **A scan attempt counts against limits even if it fails**, so failing scans can't be used to hammer a target.
   Requests rejected by URL validation (blocked/internal URLs) happen before the limiter and cost no slot.
8. **IP literals and numeric hostnames (decimal/hex/octal) are rejected outright**, not just their resolved IPs.
9. **Expired/invalid TLS certificates do not stop a scan.** It retries without chain validation and the report
   notes it. Neglected sites are the target market, and the connection is already pinned to a validated public IP,
   so this can't be used to reach internal hosts.
10. **Turnstile fails closed** when `TURNSTILE_SECRET` is set (a Cloudflare outage rejects the request); unset =
    skipped, with honeypot + rate limits still active.
11. **The scan does not email the visitor.** Emailing whatever address someone types would make the form a spam
    cannon. The report is shown on screen via its unguessable link; only paying customers and you receive email.

## Money
12. **One Stripe Checkout.** With maintenance it uses subscription mode with a one-time line + a recurring line,
    so the first invoice is `tier + $99` (the order records that total) and monthly billing continues. Maintenance
    can also be bought alone (`tier` = none); it still needs intake, authorization and ownership verification.
13. **Env names are the ones you specified** (`STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`) plus
    `STRIPE_PRICE_PHPSHIELD_{BASIC,STANDARD,COMPLEX,MAINTENANCE}`. Because PHP Shield is its own service these
    don't collide with Foundation's Switchboard-billing variables of the same name.
14. **Webhook idempotency**: each Stripe event id is inserted into `webhook_events` first (unique); a redelivery is a
    no-op. If processing fails the row is deleted and a non-2xx is returned so Stripe retries.
15. **`pending_payment` and `canceled` statuses were added** to your list (an order exists before payment). If Stripe
    session creation fails, the pending order is canceled so no orphan remains.
16. **Tier recommendation** is a points score (risk level, PHP versions behind latest, example-CVE count,
    WordPress detected) compared with two thresholds, all in `app/app/php_shield/tiers.yaml`. Unknown version =>
    no tier, "request a custom quote". The quote request flags the existing lead (status `quote_requested`) and
    emails you.

## Consent, authorization, fulfillment
17. **Authorization agreement is an AI-written DRAFT** (`agreement.py`, header + text + DB all say so). It needs
    an attorney: legal entity name (currently "PHP Shield, a service of Automaition Nation"), governing law (a
    bracketed placeholder), and the liability limits. After review, change `AGREEMENT_VERSION` (drop `-DRAFT`).
18. **The agreement text is rendered server-side and is deterministic per order** (no date inside it), so what the
    customer reads is byte-identical to what is hashed; the client can't supply text. The signing time is stored
    separately. Stored per signature: typed name, timestamp, IP, user agent, SHA-256, the exact text, domain, order.
19. **The order's domain is fixed** to the scanned domain and can't change. Intake's site URL must be on that
    domain (`www.` tolerated) — otherwise a customer could authorize one site and have another worked on.
20. **The gate**: no `authorized`/`verified`/`in_progress` without a signed, unrevoked authorization for the same
    order AND domain; `verified`/`in_progress` also need verified ownership; `in_progress` needs payment. Enforced
    in `orders.py` and again by Postgres triggers (tested on a real database).
21. **Authorizations and revocations are append-only** at the database level (triggers block UPDATE/DELETE/TRUNCATE
    even for roles that bypass RLS). Customers can revoke on their order page; you're emailed and the gate then blocks work.
22. **Customers have no accounts.** The unguessable order token in the link is the credential. The admin API/page
    uses `X-Admin-Key` (`PHP_SHIELD_ADMIN_API_KEY`); the admin page is a static shell that holds the key only in
    `sessionStorage`.
23. **Credentials are never collected in a form.** Intake records `credentials_handoff_status = link_pending`.
    **The one-time secure link itself is NOT built** — per the brief it is a placeholder note + status field.
    Today you send access details to the customer by a channel you control; build a real secure-link tool before volume.
24. **Domain verification**: DNS TXT `_phpshield-verify.<domain>` = `phpshield-verify=<token>`, or the file
    `/.well-known/phpshield-verify.txt` containing the token. Per-order random token; checks are rate-limited.
25. **Delivery** requires every checklist item ticked, runs the post-fix rescan (allowed: authorized + verified) and
    emails before/after. Maintenance-only orders "deliver" a baseline rescan the same way.
26. **Monthly rescans** run from a daily cron, due-based, re-checking consent each time; an active subscription
    without valid authorization/verification is skipped and you're alerted.

## Reliability
27. **Writes never fail silently**: log with context -> dead-letter file **and** `dead_letters` table -> alert
    (owner email + optional Slack) -> caller gets a clear 503. A failed lead insert therefore returns 503 instead of
    a fake success. Alerts are rate-limited (per key 10 min, 20/hour overall). Render's disk is ephemeral, so the
    table copy and the alert email are the durable records.
28. **Startup**: validate config (production refuses to boot, exit non-zero, lists every missing name), connect, run a
    write+delete self-test (fatal in production). `/health` returns 503 until config and DB are good and never prints secrets.

## Testing / tooling
29. **Postgres tests use `pg8000`** (pure Python) because `psycopg-binary` has no wheel for this machine's 32-bit
    Python. They run only when `PHP_SHIELD_TEST_PG_DSN` is set; otherwise 27 tests skip.
30. **Frontend** was built in the `automaition-nation` repo by a delegated agent and then reviewed by me. Landing
    pricing was placeholder copy; it now mirrors `tiers.yaml` and loads live from the API. Report/order pages are `noindex`.

## Known gaps (not done)
- No real Stripe/Supabase/Resend was available, so those integrations were tested only with fakes (signature
  verification uses the real Stripe library). Run `scripts/php_shield_verify_deploy.py` after deploy.
- Secure credential hand-off link (see 23). No refund/dispute handling. No customer-facing order list.
- Migrations were validated on PostgreSQL 18; Supabase currently runs 15/17 (only standard features are used).
- The Supabase personal access token hardcoded in `sql/run_migrations.py` (found in an earlier audit) is not
  touched here; revoke it in Supabase.
