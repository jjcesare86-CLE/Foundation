# Claude Code Instructions — Foundation Layer

## What This Project Is
This is the **shared foundation layer** for all businesses owned/operated by John (Automation Nation, VoiceMIO, Jubilant Careers, and client deployments). It is a library of reusable skills, sub-agents, brand profiles, and templates — plus a FastAPI service that exposes them all via REST API.

## Tech Stack
- **Backend**: FastAPI (Python) deployed on Render
- **Database**: Supabase (PostgreSQL + pgvector for semantic search)
- **Auth**: Supabase Auth (JWT)
- **Storage**: Supabase Storage (`foundation-bucket`)
- **Version Control**: GitHub Organization
- **AI**: Anthropic Claude (claude-sonnet-4-20250514) for agent logic

## Key Rules for Claude Code
1. **Never hardcode API keys** — always use `.env` / environment variables
2. **Supabase schema** lives in `supabase/schema.sql` — always keep it updated
3. **Skills and agents** are stored in Supabase `foundation` schema AND as markdown files in `skills-library/` and `agents-library/` (dual storage for human readability + machine queryability)
4. **All routers** go in `foundation-api/routers/` — one file per domain
5. **Pydantic models** for all request/response schemas in `foundation-api/models/schemas.py`
6. **pgvector** is enabled — use it for semantic skill/agent search via `embedding` columns
7. Deployments use `render.yaml` — keep it current when adding services or env vars

## Business Context
- **Automation Nation**: AI agency automation platform — sells onboarding + automation services to SMBs
- **VoiceMIO**: AI voice agent SaaS — 142 industries, VAPI + ElevenLabs stack
- **Jubilant Careers**: (in development) — career/hiring AI platform
- **Clients**: Foundation layer gets instantiated per-client during onboarding

## Naming Conventions
- Skills: `category/skill-name.md` (e.g., `voice-agents/restaurant-reservations.md`)
- Agents: `category/agent-name.json` (e.g., `onboarding/closer-agent.json`)
- Brand kits: `brand-kits/{business-slug}/brand.json`
- Templates: `templates/{type}/{name}.md`

## Environment Variables Required
See `foundation-api/.env.example` for the full list.
