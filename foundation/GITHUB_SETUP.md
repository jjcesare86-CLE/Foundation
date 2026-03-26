# GitHub Organization Setup Guide

## Step 1 — Create the Organization

1. Go to https://github.com/organizations/new
2. Name it: `jjcesare-foundation` (or `automation-nation-foundation`)
3. Set to **Private** (you can make specific repos public later)

---

## Step 2 — Create These Repos

| Repo Name | Contents | Who Uses It |
|-----------|----------|-------------|
| `foundation-api` | This FastAPI service | All platforms via REST |
| `foundation-skills` | `skills-library/` folder | Claude Code, agents |
| `foundation-brand-kits` | `brand-kits/` folder | All platforms |
| `foundation-templates` | `templates/` folder | AN, VoiceMIO, Jubilant |
| `foundation-agents` | `agents-library/` folder | All agent builders |

---

## Step 3 — Push This Folder

```powershell
# From your "Claude Foundation" folder in VS Code terminal:

cd "C:\Users\John\Desktop\Claude Foundation"

git init
git remote add origin https://github.com/jjcesare-foundation/foundation-api.git
git add .
git commit -m "Initial foundation scaffold"
git branch -M main
git push -u origin main
```

---

## Step 4 — Connect to Render

1. Go to https://render.com → New Web Service
2. Connect your `foundation-api` GitHub repo
3. Set build: `pip install -r requirements.txt`
4. Set start: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add env vars from `.env.example`
6. Deploy → your Foundation API URL will be something like `foundation-api.onrender.com`

---

## Step 5 — Update Platform Repos to Call Foundation API

In each platform (Automation Nation, VoiceMIO, etc.), add to your `.env`:

```
FOUNDATION_API_URL=https://foundation-api.onrender.com
```

Then call it anywhere you need skills/agents/brand/templates:

```python
# Example: Get all voice agent skills for restaurant industry
import httpx

async def get_skills(category: str, industry: str):
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{settings.FOUNDATION_API_URL}/skills",
            params={"category": category, "industry": industry}
        )
        return resp.json()
```

---

## Step 6 — Seed Your Data

1. Run `supabase/schema.sql` in Supabase SQL editor
2. Run `supabase/seed_skills.sql` for starter skills
3. Import your Perplexity-built skills/agents using the `POST /skills` and `POST /agents` endpoints

---

## Recommended .gitignore

```
.env
__pycache__/
*.pyc
.venv/
node_modules/
.DS_Store
```
