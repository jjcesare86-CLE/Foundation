# 🏗️ Claude Foundation — Core Infrastructure

This is the **shared foundation layer** powering all businesses:
- Automation Nation (automaition-nation.onrender.com)
- VoiceMIO (voicemio.com)
- Jubilant Careers (coming soon)
- ...and all future ventures + client deployments

---

## Folder Structure

```
claude-foundation/
├── README.md                   ← You are here
├── CLAUDE.md                   ← Claude Code instructions (AI reads this)
│
├── supabase/
│   ├── schema.sql              ← Full foundation schema (run this first)
│   ├── seed_skills.sql         ← Sample skill seeds
│   └── seed_agents.sql         ← Sample agent seeds
│
├── foundation-api/             ← FastAPI microservice (deploy to Render)
│   ├── main.py
│   ├── routers/
│   │   ├── skills.py
│   │   ├── agents.py
│   │   ├── brands.py
│   │   ├── templates.py
│   │   └── clients.py
│   ├── models/
│   │   └── schemas.py
│   ├── db/
│   │   └── client.py
│   ├── requirements.txt
│   ├── render.yaml
│   └── .env.example
│
├── skills-library/             ← All skill definitions (markdown + JSON)
│   ├── voice-agents/
│   ├── social-media/
│   ├── website-build/
│   ├── legal-docs/
│   ├── sops/
│   └── onboarding/
│
├── agents-library/             ← Sub-agent prompt configs
│   ├── sales/
│   ├── onboarding/
│   ├── content/
│   └── operations/
│
├── brand-kits/                 ← Per-business brand profiles
│   ├── automation-nation/
│   ├── voicemio/
│   └── jubilant-careers/
│
└── templates/                  ← Reusable output templates
    ├── websites/
    ├── social/
    ├── legal/
    └── sops/
```

---

## Quick Start

1. **Supabase**: Run `supabase/schema.sql` in your Supabase SQL editor
2. **API**: `cd foundation-api && pip install -r requirements.txt && uvicorn main:app --reload`
3. **Env**: Copy `foundation-api/.env.example` → `.env` and fill in your keys
4. **Deploy**: Push to GitHub → connect to Render using `render.yaml`

---

## GitHub Repos (Recommended)

| Repo | Purpose |
|------|---------|
| `foundation-api` | This FastAPI service |
| `foundation-skills` | Skills + agents library |
| `foundation-brand-kits` | Brand profiles per business |
| `foundation-templates` | Output templates |

All platform repos (AN, VoiceMIO, etc.) call `foundation-api` via REST.
