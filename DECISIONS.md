# PHP Shield launch — decisions

Judgement calls made while building `php-shield-launch` (nobody was available to ask).
Revisit any of these; each says what to change.

## Architecture
1. **PHP Shield is its own Render service**, `php-shield-api` (`uvicorn app.php_shield_main:app`), from this
   repo's `app/` directory. It imports nothing from `app.main` / `app.database`. Why: you asked for its own
   Supabase project and for "refuse to boot in production if config is missing" — inside `foundation-api` that
   would let a missing Stripe key take down Switchboard. The old mount in `app/main.py` and
   `routers/php_shield.py` are removed so there is exactly one (hardened) public scan surface.
2. **Its own Supabase project.** Env: `PHP_SHIELD_SUPABASE_URL`, `PHP_SHIELD_SUPABASE_SERVICE_ROLE_KEY`.
   Migrations live in `supabase-php-shield/migrations/` (NOT `supabase/migrations/`, which belongs to Foundation's
   project). The earlier `foundation.php_shield_leads` migration in `supabase/migrations/` is left untouched because
   it is already merged; **do not apply it** to the new project (or drop it from Foundation if it was applied).
3. **Scan limits** (per IP 5/h, per domain 3/day, global 500/day, 4 concurrent) are stored in a
   `scan_events` table so they survive restarts and multiple instances; if the DB is down the limiter falls
   back to in-memory counting rather than failing open. All tunable by env.
4. **Client IP** = right-most `X-Forwarded-For` entry (Render appends the real client address; the left-most
   entries are attacker-controlled).
5. **Expired/invalid TLS certificates do not stop a scan.** The request is retried without chain validation and
   the report notes it. Neglected sites are the target market; the connection is already pinned to a
   validated public IP so this cannot be used to reach internal hosts.
6. **IP-literal and numeric hostnames are rejected outright** (not just their resolved IPs), so decimal/hex/octal
   spellings never reach DNS.
7. **A scan ATTEMPT counts against limits even if it fails**, so failing scans can't be used to hammer a target.
