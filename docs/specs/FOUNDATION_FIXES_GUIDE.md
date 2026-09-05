> **STATUS (Sep 2, 2026):** The three Render env vars in this guide (`FOUNDATION_API_KEY`, `CONNECTION_BROKER_ENCRYPTION_KEY`, `ALLOWED_ORIGINS`) are **set and deployed**. The code that reads them is **not yet written** — that is what this item builds. Run only after Phase 0 (`03_PHASE0_RESTORE_API.md`) is green. The API entrypoint is `app/app/main.py`; the employees router is `app/app/routers/employees.py`.

# FOUNDATION FIXES — STEP-BY-STEP EXECUTION GUIDE
**For John to run in Claude Code or manually · Covers the CORS patch, API key gate, and Fernet encryption setup**

---

## STEP 1: CORS + FOUNDATION_API_KEY GATE

### What's wrong
`app/main.py` (or `app/app/main.py` — the audit will confirm the actual path) either:
- Has no CORS middleware (Switchboard embed from other domains gets blocked), or
- Has `allow_origins=["*"]` (works but is a security hole for authenticated endpoints), or
- Has no API key gate (anyone who finds the URL can call internal endpoints)

### What to do

**Option A — Paste into Claude Code (recommended):**
```
Open the Foundation API repo (jjcesare86-CLE/Foundation). Find the FastAPI
app entrypoint (likely app/main.py or app/app/main.py — ls to confirm).

Make these changes:

1. CORS MIDDLEWARE — replace any existing CORSMiddleware block (or add one)
   with this:

   from fastapi.middleware.cors import CORSMiddleware
   import os

   ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "").split(",")
   # Fallback for dev: if empty, allow localhost
   if not ALLOWED_ORIGINS or ALLOWED_ORIGINS == [""]:
       ALLOWED_ORIGINS = ["http://localhost:3000", "http://localhost:8080"]

   app.add_middleware(
       CORSMiddleware,
       allow_origins=ALLOWED_ORIGINS,
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )

2. API KEY GATE — add a dependency that protects internal/admin endpoints
   while leaving public endpoints open:

   from fastapi import Security, HTTPException, Depends
   from fastapi.security import APIKeyHeader

   API_KEY_HEADER = APIKeyHeader(name="X-Foundation-API-Key", auto_error=False)
   FOUNDATION_API_KEY = os.getenv("FOUNDATION_API_KEY")

   async def require_api_key(api_key: str = Security(API_KEY_HEADER)):
       if not FOUNDATION_API_KEY:
           # Key not configured = fail closed, not open
           raise HTTPException(503, "API key not configured on server")
       if api_key != FOUNDATION_API_KEY:
           raise HTTPException(403, "Invalid API key")
       return api_key

   # USAGE: add `dependencies=[Depends(require_api_key)]` to any router
   # or individual endpoint that should be protected. Public endpoints
   # (like /public/agents, /switchboard/bootstrap with its own JWT auth) stay open.
   # Example:
   #   app.include_router(admin_router, dependencies=[Depends(require_api_key)])
   #   app.include_router(ops_router, prefix="/ops", dependencies=[Depends(require_api_key)])

3. Apply the require_api_key dependency to:
   - /ops/* (agent health audit)
   - /admin/* (playbook generation, reviews)
   - /connections/callback/* stays open (OAuth callbacks need to reach it)
   - /switchboard/* uses its own JWT auth (sb_settings JWT, not the API key)
   - /public/* stays open
   - /agents stays open (read-only roster)

4. Commit: "fix: CORS whitelist + API key gate on internal endpoints"

Do NOT push yet — we'll set the env vars first.
```

**Option B — do it manually:** open `app/main.py` in your editor and make the three changes above yourself. It's ~30 lines total.

### Render env vars to set (do this in the Render dashboard or via CLI)

Go to **Render → foundation-api-9gpl → Environment**:

```
FOUNDATION_API_KEY=<generate one: python3 -c "import secrets; print(secrets.token_urlsafe(48))">
ALLOWED_ORIGINS=https://automaitionnation.com,https://www.automaitionnation.com,https://voicemio.com,https://blastvideo.ai,https://studio.blastvideo.ai,https://jubilantcareers.com,https://lightuptheskypyro.com,https://deliveredfireworks.com,https://exteriorrescuewny.com,http://localhost:3000,http://localhost:8080
```

**How to generate the key** (run locally or in any terminal):
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(48))"
```
Copy the output → paste as the value for `FOUNDATION_API_KEY` in Render.

Then set the SAME key value in every service that calls Foundation internally:
- `an-sales-pipeline` → env var `FOUNDATION_API_KEY=<same value>`
- `luts-api` → env var `FOUNDATION_API_KEY=<same value>`
- `delivered-web` (if it calls Foundation directly) → same
- Any future service that hits Foundation's internal endpoints

**Why this matters:** without this, anyone who guesses your Render URL can call
`/ops/agent-health`, `/admin/generate-playbooks`, or any internal endpoint.
The gate is a single header check — zero performance cost, massive security gain.

---

## STEP 2: FERNET ENCRYPTION FOR CONNECTION_BROKER

### Decision: Fernet (app-level) ✅
- Key lives in Render env var only — never in Postgres, never in query logs
- Python's `cryptography` library (already a FastAPI ecosystem standard)
- Encrypt on write, decrypt on read, key rotation built into Fernet spec

### Setup

**A. Generate the encryption key** (run once, locally):
```bash
python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```
Copy the output.

**B. Set the Render env var:**
```
CONNECTION_BROKER_ENCRYPTION_KEY=<paste the key from step A>
```
Set this on `foundation-api-9gpl` ONLY — no other service needs it because
no other service touches tokens directly (that's the whole point of the broker).

**C. The code (paste into Claude Code or build manually):**
```
In the Foundation repo, create or update app/services/connection_broker.py:

from cryptography.fernet import Fernet
import os

_ENCRYPTION_KEY = os.getenv("CONNECTION_BROKER_ENCRYPTION_KEY")
if not _ENCRYPTION_KEY:
    raise RuntimeError("CONNECTION_BROKER_ENCRYPTION_KEY not set — refusing to start")

_fernet = Fernet(_ENCRYPTION_KEY.encode())


def encrypt_token(plaintext: str) -> str:
    """Encrypt a token for storage. Returns a URL-safe base64 string."""
    return _fernet.encrypt(plaintext.encode()).decode()


def decrypt_token(ciphertext: str) -> str:
    """Decrypt a stored token. Raises InvalidToken on bad key/data."""
    return _fernet.decrypt(ciphertext.encode()).decode()


# --- Usage in the OAuth callback endpoint ---
# After exchanging the auth code for tokens:
#
#   from app.services.connection_broker import encrypt_token
#
#   encrypted_access = encrypt_token(access_token)
#   encrypted_refresh = encrypt_token(refresh_token)
#
#   # Store in client_connections:
#   await supabase.table("client_connections").upsert({
#       "client_id": client_id,
#       "provider": provider,
#       "access_token_encrypted": encrypted_access,
#       "refresh_token_encrypted": encrypted_refresh,
#       ...
#   })
#
# --- Usage when an agent needs to act ---
#
#   from app.services.connection_broker import decrypt_token
#
#   row = await supabase.table("client_connections") \
#       .select("access_token_encrypted") \
#       .eq("client_id", client_id) \
#       .eq("provider", "google") \
#       .single()
#
#   access_token = decrypt_token(row["access_token_encrypted"])
#   # Use access_token for the API call — never log it, never return it
```

**D. Update the migration (if not already done):**
The `client_connections` table columns `access_token_encrypted` and
`refresh_token_encrypted` are just TEXT columns — Fernet ciphertext is a
regular string. No Postgres extensions needed. If you already created the
table with these column names, you're set. If the columns are named
`access_token` / `refresh_token` without the `_encrypted` suffix, rename
them in a migration to make intent obvious:
```sql
ALTER TABLE client_connections RENAME COLUMN access_token TO access_token_encrypted;
ALTER TABLE client_connections RENAME COLUMN refresh_token TO refresh_token_encrypted;
```

**E. Key rotation (future, not urgent):**
Fernet supports `MultiFernet` — you add a new key, decrypt with any valid key,
re-encrypt with the newest. When you eventually rotate, add the new key as
`CONNECTION_BROKER_ENCRYPTION_KEY_NEW`, update the code to use MultiFernet
with [new, old], run a one-time re-encrypt migration, then remove the old key.
Don't build this now — just know it's a 30-minute job when the time comes.

---

## STEP 3: VERIFY BOTH

### Quick verification after deploy:
```bash
# 1. CORS — should get proper headers back
curl -I -X OPTIONS https://foundation-api-9gpl.onrender.com/agents \
  -H "Origin: https://automaitionnation.com" \
  -H "Access-Control-Request-Method: GET"
# Look for: access-control-allow-origin: https://automaitionnation.com

# 2. API key gate — internal endpoint WITHOUT key should 403
curl https://foundation-api-9gpl.onrender.com/ops/agent-health
# Expected: 403 Invalid API key

# 3. API key gate — WITH key should work
curl https://foundation-api-9gpl.onrender.com/ops/agent-health \
  -H "X-Foundation-API-Key: <your key>"
# Expected: 200 + health data

# 4. Public endpoint — should work without key
curl https://foundation-api-9gpl.onrender.com/agents
# Expected: 200 + roster

# 5. Fernet — start the service; if KEY is missing, it refuses to boot
# (the RuntimeError in step C guarantees this — fail closed)
```

---

## COMBINED CLAUDE CODE PROMPT (if you want Claude Code to do all of it)
```
Foundation repo, branch security-foundations. Tasks:

1. Find the FastAPI app entrypoint (ls app/ to confirm path). Add CORS
   middleware with ALLOWED_ORIGINS from env (fallback to localhost for dev)
   per docs/specs/FOUNDATION_FIXES_GUIDE.md Step 1. Add the API key gate
   (X-Foundation-API-Key header, require_api_key dependency) and apply it
   to /ops/* and /admin/* routers. Leave /public/*, /agents, /switchboard/*,
   and /connections/callback/* unprotected (they have their own auth or
   are intentionally public).

2. Install cryptography if not in requirements.txt. Create
   app/services/connection_broker.py with Fernet encrypt/decrypt per
   Step 2. Fail-closed: RuntimeError on missing env var. Wire encrypt
   into the /connections/callback/{provider} token-exchange endpoint.
   Wire decrypt into every broker action method (send_email, post_social,
   create_event, etc.).

3. If client_connections columns are named access_token / refresh_token
   without _encrypted suffix, migration to rename them.

4. Commit, verify CORS + 403 + Fernet boot-check per Step 3.
   Do NOT push until John confirms env vars are set in Render.
```

---

## ENV VAR CHECKLIST (John does these in Render dashboard)

| Service | Var | Value |
|---|---|---|
| foundation-api-9gpl | `FOUNDATION_API_KEY` | `python3 -c "import secrets; print(secrets.token_urlsafe(48))"` |
| foundation-api-9gpl | `ALLOWED_ORIGINS` | comma-separated list of all product domains (see Step 1) |
| foundation-api-9gpl | `CONNECTION_BROKER_ENCRYPTION_KEY` | `python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"` |
| an-sales-pipeline | `FOUNDATION_API_KEY` | same value as above |
| luts-api | `FOUNDATION_API_KEY` | same value as above |
| delivered-web | `FOUNDATION_API_KEY` | same value (if it calls Foundation) |

**Run order:** set all env vars in Render FIRST → then push the code branch →
Render redeploys with everything in place.
