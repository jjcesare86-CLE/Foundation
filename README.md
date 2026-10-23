# Foundation

Central repository for the Foundation platform — shared infrastructure for Automation Nation, VoiceMIO, and Jubilant Careers.

## Structure

```
foundation-org/
├── foundation-skills/          # All skill definitions (markdown/JSON)
├── foundation-agents/          # Sub-agent prompt libraries
├── foundation-brand-kit/       # Brand assets, copy, tone guides per business
├── foundation-templates/       # Website, doc, social templates
├── foundation-sops/            # SOPs, legal docs, onboarding flows
├── foundation-api/             # FastAPI microservice (deploy to Render)
├── sql/migrations/             # Supabase database migrations
└── supabase/storage/           # Storage bucket setup
```

## Database (Supabase + pgvector)

| Table | Purpose |
|-------|---------|
| `foundation.skills` | Skill name, description, prompt, category, version |
| `foundation.agents` | Agent configs, system prompts, tools list |
| `foundation.brand_profiles` | Per business: colors, tone, taglines, logos |
| `foundation.templates` | Document/web/social templates |
| `foundation.client_profiles` | Reusable client data from onboarding |

All tables have `VECTOR(1536)` embedding columns for semantic search via pgvector.

## API Endpoints

```
GET  /skills?category=social_media&industry=restaurant
GET  /agents?type=onboarding&platform=voicemio
GET  /brand/{business_slug}
POST /client-profile
GET  /templates?type=website&industry=dental
GET  /health
```

## Setup

1. Run SQL migrations in order in the Supabase SQL Editor (`sql/migrations/001_*` through `008_*`)
2. Run `supabase/storage/setup_buckets.sql` to create storage buckets
3. Copy `.env.example` to `.env` and fill in your keys
4. Deploy `foundation-api/` to Render (or run locally with `uvicorn app.main:app --reload`)

---

## PHP Shield

Consent-based PHP vulnerability funnel: **free passive scan -> report -> paid fix (Basic $300 / Standard $750 /
Complex $1,500) -> optional $99/mo maintenance**. It runs as its **own Render service** (`php-shield-api`) with
its **own Supabase project**; it shares nothing with `foundation-api` or Switchboard. The marketing-site pages
(scan box, report, checkout, order flow) live in the `automaition-nation` repo.

| What | Where |
|---|---|
| Service entrypoint | `app/app/php_shield_main.py` (`uvicorn app.php_shield_main:app`) |
| Code | `app/app/php_shield/` (see its `README.md` for architecture) |
| Database | `supabase-php-shield/migrations/*.sql` (tables, RLS, guards) |
| Render blueprint | `render.php-shield.yaml` (web service + monthly rescan cron) |
| Env vars | `.env.php-shield.example` (every variable, commented) |
| Prices / tier thresholds | `app/app/php_shield/tiers.yaml` |
| Hand-run launch steps | `MANUAL_STEPS.md` |
| Design decisions | `DECISIONS.md` |

### Local setup (PowerShell)

```powershell
cd app
pip install -r requirements.txt
$env:PHP_SHIELD_OWNER_EMAIL = "you@example.com"
$env:PHP_SHIELD_ADMIN_API_KEY = "dev-admin-key"
$env:PHP_SHIELD_IP_HASH_SALT = "dev-salt"
python -m uvicorn app.php_shield_main:app --port 8000
```

With no Supabase/Resend variables set, development mode uses an in-memory store and an outbox that only logs
emails, so everything works locally; production mode refuses to start without the real configuration.
`GET http://localhost:8000/health` shows exactly what is still missing.

### Tests and lint

```powershell
cd app
python -m pytest tests/php_shield -q
python -m ruff check app/php_shield tests/php_shield
```

To also run the database-guard tests against a real PostgreSQL (any scratch server):

```powershell
pip install pg8000
$env:PHP_SHIELD_TEST_PG_DSN = "postgresql://postgres@localhost:5432/postgres"
python -m pytest tests/php_shield/test_sql_guards.py -q
```

### Deploy to Render

1. Apply `supabase-php-shield/migrations/*.sql`, in filename order, to the PHP Shield Supabase project.
2. Create the Stripe products/prices and the webhook endpoint:
   `python scripts/create_stripe_products.py --webhook-url https://php-shield-api.onrender.com/php-shield/stripe/webhook`
   (test mode by default; `--live` with an `sk_live_` key for production). It prints every env var to set.
3. Render -> **New -> Blueprint** -> this repo -> Blueprint file path `render.php-shield.yaml`; paste the values
   it asks for (names in `.env.php-shield.example`).
4. Verify the deployment: `python scripts/php_shield_verify_deploy.py https://php-shield-api.onrender.com`

### Stripe webhook

Endpoint `https://<service>/php-shield/stripe/webhook`, events `checkout.session.completed`, `invoice.paid`,
`customer.subscription.deleted`. Signatures are verified; each event id is recorded once, so redeliveries are
harmless. `create_stripe_products.py --webhook-url ...` creates it for you and prints `STRIPE_WEBHOOK_SECRET`
(Stripe only shows the secret at creation).

### Launch checklist

- [ ] Migrations applied to the PHP Shield Supabase project; `GET /health` is 200
- [ ] Stripe **test** purchase end to end (card `4242 4242 4242 4242`): paid -> intake -> sign -> verify -> admin start/deliver
- [ ] Owner email received for the paid order and the signed authorization; customer received the signed PDF
- [ ] **Attorney has reviewed and approved the authorization agreement** (`app/app/php_shield/agreement.py`, currently marked DRAFT), governing law filled in
- [ ] Switched to Stripe **live** keys/price ids/webhook secret; `php_shield_verify_deploy.py` passes in live mode
- [ ] Resend sending domain verified; `PHP_SHIELD_OWNER_EMAIL` is a mailbox you watch
- [ ] (Optional) Turnstile: `TURNSTILE_SECRET` on the API + `VITE_TURNSTILE_SITE_KEY` on the site
- [ ] Marketing site deployed with the PHP Shield pages; scan -> report -> checkout works from automaitionnation.com
