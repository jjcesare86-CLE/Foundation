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
