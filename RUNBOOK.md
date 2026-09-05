# RUNBOOK — PHASE 0 TO LAUNCH, COPY-PASTE ORDER
**One document. Top to bottom. Each phase: what you do by hand, what you paste, what "done" looks like.**
Tick the matching box in `CHECKLIST.md` as each gate turns green. Never start the next phase on a red gate.

Every Claude Code session opens the same way — paste this header first:

```
GROUND TRUTH FOR THIS SESSION — read before any work:

Working repo:   C:\Users\jjces\OneDrive\Desktop\Foundation  (jjcesare86-CLE/Foundation, branch main)
Supabase:       project ref rhtwtoinmiekttvunlzs  (named "Foundation")
Agent catalog:  schema `foundation`, table `foundation.ai_employees` (26 active rows) —
                NOT `public.ai_employees`, and NOT the Automation Nation database.
API:            https://foundation-api-9gpl.onrender.com  (Render service foundation-api-9gpl)
Docker:         NOT installed on this machine. Do not use `supabase db dump` / `db pull`
                / `db reset`; introspect via SQL against the live database instead.

Do NOT touch:   rzsryxvlaezfvftqpvbx (that is Automation Nation's database),
                the AN-repo folder, public.ai_employees anywhere,
                eden_sessions isolation, tier gating (lives in platforms),
                GABRIEL (paused), the LYDIA Shopify agent.

Before any migration: run `supabase projects list` and confirm the LINKED marker
is on rhtwtoinmiekttvunlzs. If not: `supabase link --project-ref rhtwtoinmiekttvunlzs`.

Read docs/specs/00_STATE_OF_THE_BUILD.md before writing code. Where any other
spec disagrees with it, 00_STATE wins. Where 00_STATE disagrees with the live
database, the live database wins — and update 00_STATE.

Full project map (reference only):
  rhtwtoinmiekttvunlzs = Foundation          ← all agent / Switchboard / playbook work goes HERE
  rzsryxvlaezfvftqpvbx = Automation Nation   ← AN sales pipeline + homepage only
  xgaqgqkycckolwfcrmop = VoiceMIO
  qstcxqytmaqkygdiacfd = Blast Video
  lrlspiokmtetbzgdvzep = MRLIN
  nrqhiprzwmgdbsvyzbws = Delivered Fireworks
  dhkspkspelieaesvflvc = Bakerellas
  ohhzkmvekopnheazxbjf = Broker Broker
  mtgionuehdipyhpkiget = Exterior Rescue
  zltppbyjuivsqeolnony = MRLIN NetSuite Wizard
```

Naming: "Phase 0" is the API restore. After that the phases are lettered A–N to match `02_BUILD_ORDER.md`. If you'd rather say "Phase 1, 2, 3…" out loud, A=1, B=2, and so on. Same thing.


---

## PHASE 0 — RESTORE THE API  (`03_PHASE0_RESTORE_API.md`)

**You do first**
1. Supabase → project `rhtwtoinmiekttvunlzs` → Project Settings → API → Exposed schemas → tick **foundation** → Save.
2. SQL Editor, same project:
```sql
grant usage on schema foundation to anon, authenticated, service_role;
grant select on all tables in schema foundation to anon, authenticated, service_role;
grant select on all sequences in schema foundation to anon, authenticated, service_role;
alter default privileges in schema foundation grant select on tables to anon, authenticated, service_role;
```
3. PowerShell: `try { (Invoke-WebRequest "https://foundation-api-9gpl.onrender.com/agents").StatusCode } catch { $_.Exception.Response.StatusCode }` → expect 200. If still 500, run `select platform_slug, count(*) from foundation.employee_platform_subscriptions where is_active group by 1;` — an empty table is the other cause; seed it per §0.1.
4. `Get-Content "C:\Users\jjces\OneDrive\Desktop\AN-repo\supabase\.temp\project-ref"` → if it says `rhtwtoinmiekttvunlzs`, `cd` into AN-repo and `supabase link --project-ref rzsryxvlaezfvftqpvbx`.
5. `Rename-Item "C:\Users\jjces\OneDrive\Desktop\Foundation_Scaffold" "ZZ_old_scaffold"`
6. Render → foundation-api-9gpl → Environment: `MODEL_ORCH_MAX=claude-fable-5-1`, `MODEL_COMPLEX=claude-opus-4-8`, `MODEL_STANDARD=claude-sonnet-5`, `MODEL_COMPLEX_ENTERPRISE=claude-fable-5-1`.
7. Open Claude Code in `C:\Users\jjces\OneDrive\Desktop\Foundation`.

**Paste into Claude Code** (session header first, then this)

```
Foundation repo. Supabase project rhtwtoinmiekttvunlzs is linked. Docker is NOT
available on this machine, so `supabase db dump` and `db pull` cannot run —
work through the Supabase dashboard SQL or the Postgres connection string
instead.

1. Introspect the live schema without Docker: query information_schema for all
   tables and columns in schemas `public` and `foundation`, plus all functions,
   RLS policies, and the contents of supabase_migrations.schema_migrations.
   Save the result to docs/state/LIVE_SCHEMA_2026-09.md.

2. Read supabase/migrations/. Report which remote migration versions
   (20260818193841, 20260818193842, 20260818195000) have no local file, and
   from the live schema infer what each one created. Write the inference to
   docs/state/MIGRATION_DRIFT.md — do not guess silently.

3. Reconcile: create a baseline migration file
   supabase/migrations/20260818195000_baseline_captured.sql containing the
   CREATE statements for every table/function/policy that exists remotely but
   has no local migration (generated from step 1, idempotent with IF NOT
   EXISTS). Then run the three `supabase migration repair --status applied`
   commands (applied, NOT reverted) so the history table matches the files.
   Verify with `supabase migration list` — Local and Remote columns must
   agree with nothing pending.

4. Commit: "chore: capture live schema baseline, reconcile migration history"
Do not push any schema changes in this session. This is bookkeeping only.

--- then, same session ---

In app/app/routers/employees.py, _resolve_model() maps only
'orchestrator' | 'standard' | 'fast'. The database uses 'complex' and
'orchestrator_max'; both currently fall through to STANDARD, so all five
C-suite agents are running on Sonnet.

1. In app/llm_router.py add TaskTier.ORCHESTRATOR_MAX resolving from env
   MODEL_ORCH_MAX (default "claude-fable-5-1"). Set the COMPLEX default to
   "claude-opus-4-8" and STANDARD default to "claude-sonnet-5".
2. In employees.py, make the tier map:
     "orchestrator_max": TaskTier.ORCHESTRATOR_MAX,
     "complex":          TaskTier.COMPLEX,
     "orchestrator":     TaskTier.COMPLEX,   # legacy alias, keep
     "standard":         TaskTier.STANDARD,
     "fast":             TaskTier.FAST,
3. Add the comment block at the top of llm_router.py:
   "# ENTERPRISE FLIP: set MODEL_COMPLEX=claude-fable-5-1 in Render to move
    the full C-suite to Fable 5.1. See docs/specs/FOUNDATION_BATCH1... Part 0.1."
4. Unit test: for each model_tier value present in foundation.ai_employees,
   assert _resolve_model returns the expected model string from env.
5. Do NOT change the cost table or add Fallback API config yet — that is
   Batch 1 Phase 0. This is the minimum to stop Solomon running on Sonnet.
Commit: "fix(router): map complex + orchestrator_max tiers; Sonnet 5 default"
```

**Then, same session — roster change (Caleb → CISO, Nehemiah → COO)**

```
Foundation repo, branch roster-caleb-security. Same GLOBAL RULES (project
rhtwtoinmiekttvunlzs, schema foundation, CLI migrations, live-schema
introspection, no secrets). Read docs/specs/04_ROSTER_CHANGE_CALEB_SECURITY.md.

1. Introspect foundation.ai_employees for the Caleb row and one other C-suite
   row (Miriam) to see the exact slug, handoff, and org-chart conventions.
2. Migration:
   - UPDATE Caleb: role='Chief Information Security Officer',
     department stays 'csuite', model_tier stays 'complex'; rewrite
     system_prompt for the CISO role per the spec (hard lines included);
     handoff_to → ezra, peter, abigail, nehemiah, solomon; supervises → ezra;
     helps / outside_scope updated to match. Keep the same id and slug so
     nothing referencing Caleb's id breaks; if the slug embeds "coo", add a
     legacy_slug column (if absent) and keep the old value there.
   - INSERT Nehemiah: biblical_name='Nehemiah', product_name='Nehemiah',
     role='Chief Operating Officer', department='csuite', is_csuite=true,
     model_tier='complex', system_prompt = the former COO prompt adapted to
     Nehemiah's voice (organizer, builder, "everyone on their section of the
     wall"), handoff_to → miriam, caleb, solomon, joseph; reports_to →
     solomon; supervises → joseph, naomi, martha, silas (when he exists).
   - employee_platform_subscriptions rows for Nehemiah matching Caleb's.
   - Ezra: reports_to → caleb. Nothing else changes.
   All idempotent; seeds via ON CONFLICT.
3. Repo sweep: every place that hard-codes Caleb as COO or as the default AN
   concierge — system prompts, handoff text, Switchboard default_agent for the
   AN property, frontend copy in this repo. Change COO references to
   Nehemiah. Leave the AN homepage "Ask Caleb" button's target as a TODO with
   both options noted (Nehemiah recommended) — that lives in the AN repo and
   John decides.
4. Update docs/specs/00_STATE_OF_THE_BUILD.md §2 (roster table) and
   docs/state/DECISIONS.md in the same commit.
VERIFY: /agents returns 27; Caleb's row shows the CISO role and a
security-specific system_prompt; Nehemiah resolves to claude-opus-4-8 in a
dry run; Ezra's reports_to is Caleb; the ops-audit L1 check (once D exists)
shows both rows complete.
```

**Done when**
- `/agents` returns 200 with 26 rows, then **27** after the roster change below
- `supabase migration list` shows Local and Remote in agreement
- Unit test passes; a dry-run Solomon call logs `claude-fable-5-1` in `llm_usage`
- AN-repo's project-ref reads `rzsryxvlaezfvftqpvbx`


---

## A — SECURITY FOUNDATIONS  (`FOUNDATION_FIXES_GUIDE.md`)

**You do first**
- Env vars are already set on foundation-api-9gpl. Also set the same `FOUNDATION_API_KEY` value on `an-sales-pipeline`, `luts-api`, and `delivered-web` in Render.

**Paste into Claude Code** (session header first, then this)

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

**Done when**
- CORS preflight from automaitionnation.com returns the allow-origin header
- `/ops/agent-health` without the key → 403; with it → 200; `/agents` open → 200
- Service refuses to boot if `CONNECTION_BROKER_ENCRYPTION_KEY` is missing (test by unsetting locally)


---

## B — BATCH 1: RAHAB, ZACCHAEUS, SILAS  (`CLAUDE_CODE_MASTER_PROMPT_BATCH1.md`)

**You do first**
- Enable PostGIS is handled by the migration, but confirm the Supabase plan allows extensions.
- Create a Google Maps API key (Distance Matrix + Geocoding) → Render `GOOGLE_MAPS_API_KEY`.
- Confirm the Exterior Rescue GPS clock-in feed endpoint (Silas needs it).

**Paste into Claude Code** (session header first, then this)

```
You are working in the Foundation repo (C:\Users\jjces\OneDrive\Desktop\Foundation, jjcesare86-CLE/Foundation), Supabase project rhtwtoinmiekttvunlzs (CLI linked), deployed at foundation-api-9gpl.onrender.com. Docker is not available; introspect the live database with SQL, never with `db dump` or `db pull`.

Read in full before writing any code:
- docs/specs/00_STATE_OF_THE_BUILD.md   (verified facts — wins over every other doc)
- docs/specs/FOUNDATION_ROSTER_FABLE_EXPANSION.md
- docs/specs/FOUNDATION_BATCH1_ZACCHAEUS_RAHAB_SILAS.md  (including the SCHEMA ADDENDUM at the end)

GLOBAL RULES
1. All database changes go through Supabase CLI migration files
   (supabase migration new <name> → SQL → supabase db push). Never ad-hoc SQL
   against production. Every migration idempotent (IF NOT EXISTS; seeds via
   ON CONFLICT).
2. Before touching any table, introspect its LIVE columns via
   information_schema. The agent catalog is foundation.ai_employees with the
   exact column set in 00_STATE §4. Specs describe intent; the live schema is
   truth. Where they conflict, adapt to live and note it in
   docs/state/CURRENT.md.
3. After each phase, run its VERIFY step. If it fails, stop, fix, re-verify.
   Never begin the next phase on a red gate.
4. Every LLM-calling pipeline goes through llm_router.py and logs an llm_usage
   row (project='Foundation', agent_name per agent).
5. Commit at every green gate: "batch1: phase N — <summary>". Work on branch
   batch1-expansion; do not push to main until Phase 6 passes.
6. Never print, log, or commit secrets.
7. Do NOT touch: eden_sessions isolation, tier gating (lives in platforms),
   GABRIEL (paused), the LYDIA Shopify agent, public.ai_employees anywhere,
   the AN database (rzsryxvlaezfvftqpvbx).
8. New agent rows populate the full 00_STATE §4 column set, use lowercase
   department slugs (finance | marketing | operations …), and get
   employee_platform_subscriptions rows for every platform slug that the
   existing 26 agents have — copy the existing convention exactly.

PHASE 0 — OPTION A/B ROUTER WIRING (extends the Phase-0 tier-map fix)
- llm_router.py: MODEL_MAP with FAST → claude-haiku-4-5-20251001,
  STANDARD → claude-sonnet-5, COMPLEX → claude-opus-4-8,
  ORCHESTRATOR_MAX → claude-fable-5-1, VOICE → gemini-3.1-flash-live,
  LONGCTX → claude-fable-5-1 — every one overridable by env.
- Enforce prompt caching on COMPLEX and ORCHESTRATOR_MAX calls (reject
  uncached).
- Anthropic Fallback API configuration applied to whatever model string
  resolves to claude-fable-5-1 (safeguard reroutes bill at Opus rates; log
  task_type='fable_fallback').
- Cost table: fable-5-1 10/50 with cache-read at 0.25; opus-4-8 5/25;
  sonnet-5 2/10; haiku per current pricing; cache-read for non-Fable models
  at 10% of input.
- Migration: confirm solomon-ceo model_tier='orchestrator_max' (already
  true), and nehemiah (COO), caleb (CISO), miriam-cfo, isaiah-cso, abigail-clo
  model_tier='complex' (true after Phase 0.6). This phase is a no-op on data if 00_STATE holds;
  verify rather than assume.
VERIFY: unit test resolves each tier to the expected model string; a dry-run
Solomon call logs claude-fable-5-1 with cached input to llm_usage; a dry-run
Nehemiah call logs claude-opus-4-8.

PHASE 1 — JOANNA (VERIFY ONLY — already done in the database)
- Confirm the finance row has biblical_name='Joanna' and product_name='Lydia'.
  Do NOT rename anything.
- Repo sweep: any system prompt, handoff array, redirect line, or frontend
  card in this repo that refers to the invoicing agent as "Lydia" in a
  finance context should read "Joanna" (biblical_name). product_name stays
  'Lydia' wherever product_name is what's displayed. The Shopify LYDIA agent
  is a different product — leave it alone.
VERIFY: grep shows no finance-context "Lydia" where biblical_name is meant;
/agents returns Joanna in finance.

PHASE 2 — AGENT 28: RAHAB (build FIRST — creates the shared action library)
- Execute Sprint R from the Batch 1 doc: ai_employees row (00_STATE §4
  columns; department 'marketing'; model_tier 'standard'; handoff_to
  → anna, nathan, peter), rr_reviews + rr_review_requests migrations with
  RLS, system prompt into the system_prompt column, the typed action library
  (agent_actions table, approve/reject endpoints, dashboard approval inbox,
  first action type post_review_response — designed per the GABRIEL
  action-library spec for reuse), GHL review ingestion cron, Haiku draft
  pipeline with the tone matrix, post-approval publishing, review-request
  automation, nightly spike detection. Seed client: Bakerellas.
VERIFY: /agents count = 28 with rahab active; insert a fake 3-star review row,
the cron drafts a response, it appears in the approval inbox, approving flips
status to posted (mock the GHL publish call in test mode).

PHASE 3 — AGENT 27: ZACCHAEUS
- Execute Sprint Z: ai_employees row (department 'finance'; handoff_to →
  joanna-finance, miriam-cfo, abigail-clo), zb_transactions /
  zb_tax_deadlines / zb_contractors with RLS, system prompt, Stripe read via
  connection_broker (stub the broker if item C hasn't shipped — leave a
  clearly marked TODO, never a silent no-op), Sonnet categorization with the
  <0.7-confidence clarification queue, daily cron (deadline reminders
  T-30/7/1, 1099 sweep, anomaly flags). Seed clients: Delivered Fireworks and
  LUTS; backfill 90 days of Stripe.
VERIFY: /agents count = 29; one categorization batch runs end-to-end on real
backfilled rows; the four federal quarterly dates are seeded per client;
llm_usage shows zacchaeus rows with costs.

PHASE 4 — AGENT 29: SILAS (implements HyperSchedule Phase 1)
- Migration: CREATE EXTENSION IF NOT EXISTS postgis; then fs_crews, fs_jobs,
  fs_slot_offers with RLS, and the atomic claim_slot() function
  (FOR UPDATE SKIP LOCKED, first-confirm-wins).
- Execute the rest of Sprint S: ai_employees row (department 'operations';
  handoff_to → naomi, joanna-finance, rahab-reputation), system prompt with
  per-client weather_rules (Exterior Rescue: no roofing when precip>40% or
  wind>25mph), 05:30 dispatch builder using Google Maps Distance Matrix
  (env GOOGLE_MAPS_API_KEY — stop and ask John if it is not set), run sheets
  via GHL SMS, night-before confirmations, Haiku ETA texts, 15-minute slip
  monitor against the GPS clock-in feed, weather-conflict job using the
  approve_reschedule action type (reuses the Phase 2 inbox), completion hook
  (done → Rahab review request + Joanna invoicing notify), nightly owner
  recap. Seed: Exterior Rescue WNY with 2 demo crews + 8 demo jobs.
VERIFY: /agents count = 29; one full simulated dispatch cycle (build → run
sheets → force one job late → slip alert → complete a job → Rahab request +
Joanna notify created); two concurrent claim_slot() calls on one slot —
exactly one wins.

PHASE 5 — ROSTER INTEGRITY SWEEP
- All 30 rows complete on the 00_STATE §4 column set; backfill gaps in the
  three new agents by matching existing department members.
- employee_platform_subscriptions rows exist for the three new agents on
  every platform slug the original 26 have.
- Frontend roster components in this repo render the count dynamically.
VERIFY: /agents and /public/agents both return 30 active; frontend builds
clean.

PHASE 6 — QA + SHIP
- Full test suite; lint; `supabase migration list` shows nothing pending.
- Write docs/specs/BATCH1_COMPLETION_REPORT.md: what shipped, migration list,
  env vars in play, seeded clients, anything deferred, the exact Enterprise
  flip instruction. Update docs/state/CURRENT.md and DECISIONS.md.
- Merge batch1-expansion → main; confirm Render deploy goes green.
VERIFY: production /agents returns 30; one live smoke call per new agent
logs to llm_usage.

When Phase 6 is green, report completion and WAIT. Batches 2 and 3 (Obadiah,
Bezalel, Priscilla, Amos, Tabitha) will arrive as a separate spec. Do not
begin them on your own.
```

**Done when**
- `/agents` = 30; Phase 6 completion report written; Render green
- Rahab's approval inbox works end to end; `claim_slot()` concurrency test passes


---

## D — OPS AUDIT, PART A  (`AGENT_OPS_AUDIT_ELIJAH_V1_1.md` A.1–A.4)

> Do this immediately after B. It is what turns the roster into a screen you can show people.

**You do first**
- Have Render dashboard access ready — the audit will produce a list of env vars only you can set (`PIPELINE_API_KEY`, the `gemini_voice_proxy.py` deploy, etc.).

**Paste into Claude Code** (session header first, then this)

```
Foundation repo, branch ops-audit. Same GLOBAL RULES as the Batch 1 master
prompt. Build Part A of docs/specs/AGENT_OPS_AUDIT_ELIJAH_V1_1.md:
1. Migrations: required_capabilities column + agent_jobs registry; backfill
   required_capabilities for all agents per A.2; retrofit every existing cron
   to heartbeat agent_jobs.
2. Build ops_audit.py + /ops/agent-health (admin auth) + nightly audit cron
   + the admin grid page.
3. RUN THE FULL AUDIT and write docs/state/OPS_AUDIT.md listing every agent's
   L1–L5 status with the exact failing reason and the exact fix, separated
   into: (a) fixes Claude Code can do itself — DO THEM, re-run, iterate until
   stable; (b) fixes requiring John (env vars, OAuth connects, dashboard
   toggles, third-party accounts) — list precisely, one line each, with where
   to click.
4. Re-run until every agent is green except items blocked on John's list.
Report the final board and John's blocking list.
```

**Done when**
- `/ops/agent-health` returns a 30-row board; `docs/state/OPS_AUDIT.md` exists
- Every red row is either fixed or on your named list with a click-path


---

## C — CONNECTIONS HUB  (`CONNECTIONS_HUB_BUILD.md`)

**You do first**
- **Day one:** create a separate Google Cloud OAuth client for the hub and submit Google's app verification for `gmail.send` + calendar scopes. 1–2 weeks; can't be shortened.
- Confirm your GHL agency white-label level (decides embed vs new-tab for GHL social connect).

**Paste into Claude Code** (session header first, then this)

```
Repos: Foundation (jjcesare86-CLE/Foundation) + the AN client dashboard frontend.

Build the "Connections Hub" per CONNECTIONS_HUB_BUILD.md:

1. Supabase: create client_connections table exactly as specced (Part 4),
   with RLS and encrypted token columns via Supabase Vault/pgsodium. Read the
   live schema first to reference the correct clients table PK.

2. Foundation API: implement the five /connections endpoints. Google OAuth
   first (reuse the working signInWithOAuth pattern from Blast Video, but as
   a standard authorization-code flow with offline access for refresh
   tokens; scopes: gmail.send, calendar.events). Encrypt tokens at rest.
   NEVER return tokens in any API response.

3. Frontend: /dashboard/connections page per the UX spec in Part 3 — card
   grid, one Connect button per card, popup OAuth, live status states,
   progress banner, plain-English copy exactly as written. GHL social cards
   deep-link into the client's GHL subaccount social integration page
   (location ID lives on the client record from the pipeline bridge).
   Stripe card links to a Stripe Connect onboarding session.

4. connection_broker.py: agent-facing access layer per Part 4. Add the
   missing-connection fallback line to Nathan, Esther, Naomi, and Lydia
   system prompts.

5. Replace the dead auth.automaitionnation.com stub URLs in
   an-sales-pipeline/onboarding/teams/social_media.py with real hub links:
   {dashboard_url}/dashboard/connections?client={id}.

6. Render cron: nightly token health check per Part 4.

Do not build custom Meta/TikTok OAuth apps — GHL carries those in v1.
```

**Done when**
- Connect Google on a test client → green check → token encrypted at rest → nightly health cron flips an expired token to amber
- Onboarding stub URLs to `auth.automaitionnation.com` are gone


---

## E — PROOF OF WORK + UNLAZY  (`UNLAZY_AND_PROOF_OF_WORK.md`)

**You do first**
- Decision already made: Unlazy per-project on Foundation only. Nothing to set up by hand.

**Paste into Claude Code** (session header first, then this)

```
Foundation repo, branch proof-of-work. Read
docs/specs/UNLAZY_AND_PROOF_OF_WORK.md fully. Same GLOBAL RULES as the Batch 1
master prompt (Supabase project rhtwtoinmiekttvunlzs, CLI migrations only,
live-schema introspection first, verify gates, no secrets, don't touch
eden_sessions / tier gating / GABRIEL / LYDIA-shopify).

PART 1 — DEV SKILL
1. Install unlazy: `npx skills add Leonxlnx/unlazy -g`. Verify the files are
   actually on disk and report the path — do not claim installed without
   checking. Pin the commit SHA into docs/state/DECISIONS.md.
2. Install the Stop hook for this project
   (scripts/install-hooks.mjs); add .unlazy-hook-state.json to .gitignore.
3. Read the shipped references/orchestration.md and report whether v2 already
   does rolling parallel dispatch. If it does NOT, apply the §1.5 edit. If it
   does, skip the edit and note that in the completion report.
4. Add the §1.7 CLAUDE.md block to Foundation and each product repo present
   locally.
5. Add a `Tier:` field convention to PLAN.md leaves and wire leaf subagent
   model selection through llm_router, logging to llm_usage with
   project='Foundation-dev'.

PART 2 — RUNTIME PROOF OF WORK
6. Migration: agent_actions columns + agent_task_receipts table per §2.2,
   with RLS.
7. connection_broker: every action method returns a receipt
   {external_id, status, count} and writes it to agent_actions.evidence with
   verification_status. Broker methods that cannot verify must set
   verify_method='none' and verification_status='pending' — never 'verified'.
8. Append the §2.3 PROOF OF WORK block to all agent system prompts in the
   prompt store EXCEPT Eden (exempt — no receipt logging crosses her
   boundary). Add per-agent receipt requirements per §2.4.
9. Switchboard: render completed actions as receipt cards in the thread
   (claim + evidence links).
10. Ops audit L5: extend to assert last-10-actions have evidence and
    verification_status='verified'; unverified completions = amber.

VERIFY:
- Force a GHL publish failure in test mode: Rahab must report the failure with
  the reason, NOT report success, and the action row must show
  verification_status='failed'.
- Run an Esther campaign against a seeded list with 3 invalid addresses: the
  client-facing report must read "sent N of M" with the 3 named as failures.
- Confirm no Eden action rows carry receipt metadata.
- Confirm the Stop hook blocks ending a turn with an unmet gate (test on a
  throwaway gates file).
Finish with docs/specs/PROOF_OF_WORK_COMPLETION.md.

ALSO IN THIS SWEEP (added Sep 4): append the CONVERSATION DISCIPLINE block from
docs/specs/05_CONVERSATION_DISCIPLINE.md §3 to every agent prompt (Eden
included), and add the six tests in §4 to the gates file for this item.
```

**Done when**
- The six conversation-discipline tests pass ("hi" mid-decision returns a greeting AND the restated choices; nothing resolved)
- Forced GHL failure → Rahab reports failure, action row `verification_status='failed'`
- Esther test campaign reports "sent N of M" with failures named
- No Eden rows carry receipt metadata; Stop hook blocks an unmet gate on a throwaway file


---

## H — BATCHES 2 + 3: OBADIAH, BEZALEL, PRISCILLA, AMOS, TABITHA

**You do first**
- Nothing manual. Seed clients (Broker Broker, LUTS) already exist.

**Paste into Claude Code** (session header first, then this)

```
Foundation repo, branch batch2-3-expansion. Same GLOBAL RULES as the Batch 1
master prompt (Supabase rhtwtoinmiekttvunlzs, schema foundation, CLI migrations,
live-schema introspection first, verify gates, no secrets, protected areas).
Read docs/specs/FOUNDATION_ROSTER_FABLE_EXPANSION.md Part 3 (agents 30–34) and
docs/specs/00_STATE_OF_THE_BUILD.md §4 (the real column set). Follow the Batch 1
pattern exactly — each agent = ai_employees row + employee_platform_subscriptions
rows + system prompt + its own tables with RLS + crons + seed client + smoke test.

BATCH 2 (one phase per agent, verify gate between each):
  OBADIAH  — Property & Tenant Manager, department operations, standard tier.
             Tables ob_units, ob_leases, ob_maintenance_tickets. Rent reminders,
             maintenance intake → Silas dispatch handoff, lease renewals, owner
             statements. Seed: Broker Broker Realty. Handoffs: silas, joanna, rahab.
  BEZALEL  — Design & Creative Director, department marketing, standard tier +
             image generation through the existing Higgsfield/Gemini pipeline and
             brand_assets. Tables bz_briefs, bz_assets. Logo concepts, brand kits,
             social graphics, ad creatives — every output lands in brand_assets with
             a receipt. Preflight the Higgsfield balance before any render.
             Handoffs: deborah, nathan, anna, gideon.
  PRISCILLA — Training & SOP Builder, department hr, standard tier.
             Tables pr_sops, pr_courses, pr_quizzes. Turns interview-engine
             transcripts into SOPs, onboarding curricula, quizzes; per-client
             process wiki. Handoffs: delilah (HR), leah.
VERIFY after Batch 2: /agents = 33.

BATCH 3:
  AMOS     — Compliance & License Tracker, department legal, FAST tier for
             deadline logic with Sonnet for analysis. Tables am_licenses,
             am_requirements. Tracks licenses, permits, insurance, OSHA, CEUs by
             trade and state; T-90/30/7 reminders; drafts renewal paperwork.
             Seed: LUTS (ATF), Broker Broker (NMLS). Handoffs: peter, abigail.
  TABITHA  — Nonprofit & Donor Relations, department sales, standard tier.
             Tables tb_donors, tb_grants, tb_appeals. Donor CRM, grant deadline
             tracking + drafts, receipts, appeals, board reports. Handoffs:
             esther, joanna, elijah.
VERIFY after Batch 3: /agents = 35; every new agent has a green L1–L5 row on the
ops board (/ops/agent-health); PROOF OF WORK block present in all five prompts.

Update docs/state/CURRENT.md and DECISIONS.md; write
docs/specs/BATCH2_3_COMPLETION_REPORT.md. Merge to main; confirm Render green.
```

**Done when**
- `/agents` = 35; all five green on the ops board; completion report written


---

## H+ — GABRIEL REACTIVATION

> You asked for Gabriel to be 100% at launch. He was PAUSED by decision; this un-pauses him on top of the action library from B and the receipts from E.

**You do first**
- Decide: is GABRIEL in the launch roster? If yes, run this. If not, skip and leave him paused.

**Paste into Claude Code** (session header first, then this)

```
Foundation repo, branch gabriel-reactivate. GABRIEL (Meeting Scribe & Executor)
was specced and PAUSED. Un-pause him now that the typed action library exists.
1. Read the existing GABRIEL spec/prompt in the repo (search "GABRIEL" and
   "meeting scribe"). Do not rewrite his purpose.
2. ai_employees row (department operations, standard tier, is_active=true) +
   employee_platform_subscriptions rows, per 00_STATE §4 columns.
3. Wire his typed actions (send_email, create_task, update_crm, schedule_meeting)
   onto the shared action library built in Batch 1 Phase 2 — same agent_actions
   table, same approval inbox, same receipt columns from Proof of Work.
4. Meeting ingestion: transcript in → action items extracted → each becomes an
   agent_actions row with verification_status='pending' → approval inbox →
   executed with receipt.
VERIFY: /agents = 36; a seeded transcript yields three pending actions in the
inbox; approving one executes it and the receipt shows verified. Green row on
the ops board. Update DECISIONS.md: "GABRIEL reactivated <date>".
```

**Done when**
- `/agents` = 36; seeded transcript → three pending actions → approve one → verified receipt


---

## F — AUTOPILOT NUANCES  (`AUTOPILOT_NUANCES_IMPLEMENTATION.md`)

**You do first**
- Nothing manual. Preflight lands first and starts protecting Higgsfield credits immediately.

**Paste into Claude Code** (session header first, then this)

```
Read docs/specs/AUTOPILOT_NUANCES_IMPLEMENTATION.md in full. Execute Modules
3 → 2 → 1 → 4 → 5 → 6 in that order under the same GLOBAL RULES as the Batch 1
master prompt (migrations via Supabase CLI only, introspect live schema first,
verify gates between modules, branch autopilot-nuances, no secrets, don't touch
eden_sessions/tier-gating/GABRIEL/LYDIA-shopify).
Module-specific verification:
- M3: kill a test client's connection token, run a Blast Video preflight —
  pipeline must halt BEFORE any Higgsfield call and emit the Connections Hub
  deep-link message.
- M2: generate the same announcement for linkedin/instagram/x for a seed
  client — three structurally different outputs, validator passes all three;
  then plant a banned word in voice profile and confirm one auto-regeneration.
- M1: run the Silas setup interview with deliberately vague answers — confirm
  exactly one pushback per question and low_confidence flags on surrendered
  fields.
- M4: set humor=90 on rahab for a test client — confirm composer caps it at 40
  in the rendered prompt block.
- M5/M6: state files exist and CLAUDE.md references them; scout runs once
  manually and produces SCOUT_REPORT.md without auto-merging anything.
Finish with docs/specs/AUTOPILOT_NUANCES_COMPLETION.md summarizing what shipped.
```

**Done when**
- Blast Video halts before any Higgsfield call when a token is dead
- Same announcement renders three structurally different ways for LinkedIn / Instagram / X and the validator passes
- Rahab's humor slider caps at 40 regardless of client setting


---

## G — ELIJAH SCOREBOARD + CALLS/TRAFFIC  (`ELIJAH_SCOREBOARD_BUILD.md`, then Ops Audit B.3)

**You do first**
- Provision per-channel GHL tracking numbers for the pilot client (website / GMB / Facebook ad) — config, not code.
- Add `analytics.readonly` to the hub's Google OAuth client for GA4.

**Paste into Claude Code** (session header first, then this)

```
Read docs/specs/ELIJAH_SCOREBOARD_BUILD.md. Same GLOBAL RULES as the Batch 1
master prompt (CLI migrations, live-schema introspection first, verify gates,
branch elijah-scoreboard, no secrets, protected areas untouched).
Phases:
1. Migrations: mkt_metrics_daily, mkt_cta_performance, mkt_insights with RLS.
2. Ingestion: nightly GHL metrics cron via connection_broker (preflight
   first); in-house CTA logging hooks in Esther's send pipeline and Nathan's
   publish pipeline (UTM short links generated at publish).
3. Elijah prompt-store update (Section 4 verbatim) + nightly anomaly job +
   Monday weekly-scoreboard job writing mkt_insights and dispatching the GHL
   digest.
4. Frontend /dashboard/scoreboard per Section 5, matching the approved
   mockup's layout; recommendation approve button creates an action-library
   task (reuse Rahab's inbox infrastructure, action type: execute_marketing_action).
5. Seed the demo client with 8 weeks of plausible metrics; VERIFY end-to-end:
   ingestion → anomaly → weekly scoreboard renders → approving the
   recommendation creates a task assigned to esther.
Finish with a completion report in docs/specs/.

--- then, next session, v1.1 ---

Foundation repo, branch elijah-v1-1, after the base scoreboard ships. Build
Part B of docs/specs/AGENT_OPS_AUDIT_ELIJAH_V1_1.md:
1. Migrations: new columns on mkt_metrics_daily (calls, calls_answered,
   calls_booked, avg_call_seconds, sessions, site_conversions) +
   mkt_call_log + mkt_pageviews, all RLS'd, idempotent.
2. VAPI ingestion job + Haiku call-outcome classifier; GHL call events merge;
   after-hours detection from client business_hours.
3. GA4: Connections Hub card (analytics.readonly on the existing Google OAuth
   client), nightly ingestion via connection_broker with preflight; build the
   first-party beacon (script + endpoint + table) as the no-GA4 fallback.
4. Scoreboard UI: add Calls and Website visitors cards, funnel sentence
   component, and the two new insight rules (missed-calls upsell,
   traffic-up-bookings-flat).
5. Elijah prompt-store update: calls + traffic duties, attribution honesty
   extends to tracking-number sourcing.
6. Seed demo client with 8 weeks of call + traffic data; VERIFY the funnel
   sentence renders with correct math and the missed-call insight fires on
   seeded data.
```

**Done when**
- Demo client shows 8 weeks of metrics; weekly scoreboard renders; approving Elijah's recommendation creates an Esther task
- Funnel sentence renders with correct math; missed-calls insight fires on seeded data


---

## I — SWITCHBOARD, WEB  (`SWITCHBOARD_BUILD.md` + Addenda B and C)

**You do first**
- Register domains: `switchboard.ai`, `getswitchboard.com`, `switchboard.automaitionnation.com` (DNS only for now).
- Trademark knockout search on "Switchboard" in classes 9 and 42; file once cleared.
- Open `demo/switchboard-demo-v11.html` in Chrome — it is the reference for every front-end behavior in this phase.

**Paste into Claude Code** (session header first, then this)

```
Foundation repo, branch foundation-dock. Same GLOBAL RULES as the Batch 1
master prompt (CLI migrations, live-schema introspection, gates, no secrets,
protected areas). Read docs/specs/SWITCHBOARD_BUILD.md fully. Execute
Phases 1→5 in order with a verify gate per phase:
- P1 verify: Switchboard renders in AN dashboard inside Shadow DOM with zero style
  bleed; send/receive works for 3 different agents with per-agent history;
  entitlement mask correctly locks a non-plan agent; RLS blocks cross-user
  thread reads (test it).
- P2 verify: an approval-inbox action (Rahab draft) appears as an unread DM
  with working inline approve; agent_jobs heartbeat changes presence line;
  a Caleb→Miriam handoff opens Miriam's window with carried context.
- P3 verify: call button mints a live VAPI session; post-call summary posts
  into the same thread.
- P4 verify: script-tag embed on the Exterior Rescue staff dashboard works
  with their auth and their agent roster.
- P5 verify: locked-agent tap under $5K opens checkout with correct pricing
  engine values; ≥$5K routes to the sales voice flow.
- Eden check at every phase: eden threads unreadable by any other role.
Finish with a completion report + a one-page EMBED_GUIDE.md for adding the
Switchboard to any future product in under 5 minutes.

ALSO IMPLEMENT (added after this prompt was written):
- Addendum B: per-user bubble_color, lang, voice_id on sb_settings; the
  translation layer (sb_message_renderings, FAST-tier Haiku pass, cached per
  message+lang, "show original" always available; never translate receipts,
  IDs, numbers).
- 05_CONVERSATION_DISCIPLINE.md §2: sb_threads.open_items JSONB, appended
  whenever an agent asks or presents buttons; prompt_composer injects open
  items ABOVE the recent-message window; 72h digest surfacing.
- Addendum C: sb_memberships; per-workspace JWT; no cross-workspace reads
  (tests in C.7 must pass); pins are references, not moves; workspace switcher
  for users with multiple memberships; lock line naming the workspace.
```

**Done when**
- Board renders in Shadow DOM on AN with zero style bleed; per-agent history; RLS blocks cross-user AND cross-workspace reads
- Rahab draft arrives as an unread DM with inline approve; agent_jobs heartbeat drives presence
- Call button mints a VAPI session; summary posts to the thread
- Embed works on Exterior Rescue's staff dashboard; locked-agent tap routes to pricing correctly
- Spanish rendering with "ver original"; pin/unpin keeps the person in their category


---

## J — SPECIALIZATION ENGINE  (`SWITCHBOARD_V1_1_TIERS_AND_SPECIALIZATION.md`)

**You do first**
- `industries` and `industry_playbooks` ALREADY EXIST in Foundation — the prompt must read their live columns and extend, not recreate. Tell Claude Code that in the first line.
- You personally review the fireworks and roofing playbook sets before activation.

**Paste into Claude Code** (session header first, then this)

```
industries and industry_playbooks tables ALREADY EXIST in Foundation's public
schema (created ~Aug 18). Introspect their live columns first and EXTEND them —
do not create parallel tables. Then:

Foundation repo, branch industry-specialization. Same GLOBAL RULES. Read
docs/specs/SWITCHBOARD_V1_1_TIERS_AND_SPECIALIZATION.md.
1. Migrations: industries table, industry_playbooks table,
   requires_industry_playbook column on ai_employees (backfill per Section 2.3
   — 14 niche agents TRUE, 20 universal agents FALSE), is_internal_property
   on sb_settings, industry_slug on clients table if not present.
2. prompt_composer.py: playbook injection per Section 2.4 — playbook block
   renders between brand_voice and operational_params; role_override replaces
   the generic role line in the agent header.
3. Switchboard bootstrap: implement the two-tier flow per Section 5 — internal
   properties get full unfiltered roster; client properties get industry-
   filtered + entitlement-masked + "Show all" directory.
4. Playbook generation pipeline: admin endpoint POST /admin/generate-playbooks
   { industry_slug, agent_slugs[] } → Fable 5.1 batch call (MODEL_ORCH_MAX)
   with the structured prompt from Section 2.5 → insert rows →
   status=pending_review. Admin review endpoint to activate.
5. On-demand trigger: when a new client's industry has no playbooks, auto-
   queue generation + set client.onboarding_status='team_training' with a
   message: "Your team is getting trained on {industry} — ready within 24h."
6. Seed Wave 1 (7 industries from Section 3): run the generation pipeline
   for all 7 × their listed agents. Human-review the fireworks + roofing
   sets (John knows these cold); spot-check the rest.
VERIFY: bootstrap for an internal property returns 34 unlocked; bootstrap
for a roofing client returns ~12 filtered agents with roofing role_overrides;
bootstrap for a niche with no playbooks returns universals only + training
message; Nathan's composed prompt for a roofing client contains roofing
terminology and themes; same Nathan for a restaurant client contains
restaurant terminology.
Finish with docs/specs/SPECIALIZATION_ENGINE_COMPLETION.md including the
playbook count and any industries that need human review.
```

**Done when**
- Internal property bootstrap returns all agents unlocked; roofing client returns ~12 with roofing role_overrides
- Nathan's composed prompt for a roofer contains roofing terminology; same Nathan for a restaurant does not
- Wave 1 (7 industries) generated; fireworks + roofing reviewed by you


---

## N — LAUNCH PAGES: switchboard.automaitionnation.com + SECURITY PAGE

> This runs in the AN repo, not Foundation — same pattern as lydia.automaitionnation.com.

**You do first**
- Decided: the security page is `caleb.automaitionnation.com` and the agent is **Caleb, Chief Information Security Officer** (Phase 0.6). Decide separately whether the AN homepage "Ask Caleb" button becomes "Ask Nehemiah" (recommended — a front door should be operations, not security).
- DNS: point both subdomains at the AN Render service.

**Paste into Claude Code** (session header first, then this)

```
AN repo (C:\Users\jjces\OneDrive\Desktop\AN-repo — Automation Nation, Supabase
rzsryxvlaezfvftqpvbx, NOT Foundation). Follow the exact pattern used for
lydia.automaitionnation.com (see commits "feat(lydia): move Lydia landing page to
lydia.automaitionnation.com" and the static landing page work). Read
docs/specs/SWITCHBOARD_NAMING.md and SWITCHBOARD_BUILD.md from the Foundation repo
for product facts; use assets/switchboard-logo.jpg for the mark.

1. switchboard.automaitionnation.com — hand-authored static landing page in the
   Lydia pattern. Hero: the board itself (embed demo/switchboard-demo-v11.html
   behavior as a live, interactive hero, or a faithful static capture if the
   embed is too heavy). Copy lines: "Your whole team, on the board." /
   "If you ever had a buddy list, you already know how to use this." /
   "Other AI tools tell you they did it. Ours shows you the receipt." Pricing
   from SWITCHBOARD_ADDENDUM_A §4.3. CTA → existing AN checkout/sales flow.
   Colors: copper #B4672B, cobalt #2F5FA8, navy #17212B on warm white.
2. caleb.automaitionnation.com — the security page. Pattern: the
   quarantined-invoice scenario from the demo as the hero story; receipts shown;
   plain-language explanation that this is a hold-and-ask layer on top of the
   client's existing mail security, never a replacement. The agent is Caleb (CISO); Ezra
   is named as the one who executes fixes.
3. DNS + Render: add both subdomains to the AN Render service, SSL, and to
   ALLOWED_ORIGINS on foundation-api-9gpl.
4. SEO per the per-route SEO pattern already in the repo.
VERIFY: both pages load over HTTPS, mobile-clean, Lighthouse ≥ 90, CTAs reach
checkout. Commit in the AN repo's existing message style.
```

**Done when**
- Both pages live over HTTPS, mobile-clean, Lighthouse ≥ 90, CTAs reach checkout
- Both subdomains in `ALLOWED_ORIGINS` on the Foundation API


---

## K — SWITCHBOARD NATIVE MOBILE, PHASES 1–4  (`SWITCHBOARD_NATIVE_MOBILE_VOICE.md`)

**You do first**
- **Day one:** request the Apple `com.apple.developer.push-to-talk` entitlement through the developer account. It is the long pole for M.
- Apple Developer Program + Google Play console active. A real Android device and a real iPhone for on-device VERIFY steps.

**Paste into Claude Code** (session header first, then this)

```
New repo: switchboard-mobile. Read docs/specs/SWITCHBOARD_NATIVE_MOBILE_VOICE.md.
Same GLOBAL RULES as the Batch 1 master prompt (no secrets, verify gates
between phases, Supabase project rhtwtoinmiekttvunlzs where relevant).

Phase 1: Scaffold a Capacitor app that loads the existing Switchboard web
build. Implement VoiceBridge.capabilities() returning all-false stubs on web.
Wire Switchboard's voice settings sheet to show the browser-limitation line when
backgroundCapture is false. VERIFY: Switchboard renders identically in the shell and
in a browser; capabilities() returns correct values on each.

Phase 2 (Android): VoiceBridge native module with a microphone-typed foreground
service. Manifest: android:foregroundServiceType="microphone", permissions
FOREGROUND_SERVICE, FOREGROUND_SERVICE_MICROPHONE, RECORD_AUDIO. Enforce the
ordering: request and confirm RECORD_AUDIO BEFORE startForeground(), or the
system throws SecurityException. Persistent notification reads "Foundation is
listening — tap to stop" and stopping from the notification ends capture
cleanly. VERIFY on a real device: hold mic, switch to another app mid-sentence,
return — transcript is complete and unbroken.

Phase 3 (iOS Tier A): UIBackgroundModes audio; AVAudioSession configured for
record with correct category/options. Handle AVAudioSession interruption
notifications on iOS and audio focus loss on Android: stop capture, preserve
the partial transcript as a composer draft, post the "recording stopped" system
line into the thread. VERIFY: app-switch survival on device; incoming phone
call preserves the draft rather than losing it.

Phase 4: Local capture queue (audio written to disk before any network call),
queued-state message rendering, background drain on reconnect, on-device
transcription where available with server fallback. VERIFY in airplane mode:
message records, shows "waiting for signal", and sends with a real receipt on
reconnect — and never shows a receipt while queued.

Phase 5: iOS PushToTalk framework integration behind the
com.apple.developer.push-to-talk entitlement (do not start until John confirms
approval). Channel model, APNs wiring, Bluetooth PTT button support.

Phase 6: Android hardware PTT key event mapping.

Verify each platform API against current Apple and Android developer docs
before implementing — these requirements change between OS versions, and the
spec's citations are a starting point, not gospel.
```

**Done when**
- Hold mic, switch apps mid-sentence, return: transcript unbroken (both platforms)
- Incoming phone call preserves the draft; airplane-mode message shows "waiting for signal" and sends with a receipt on reconnect — never a receipt while queued


---

## L — LIVE TWO-WAY PTT  (`SWITCHBOARD_ADDENDUM_A_LIVE_PTT.md`)

**You do first**
- Decide SFU hosting (self-host LiveKit on Render vs managed) — Claude Code documents the choice, you approve the cost.
- Retention is decided: transcripts forever, audio 30 days. It's in the prompt.

**Paste into Claude Code** (session header first, then this)

```
Repo switchboard-mobile + Foundation API. Read
docs/specs/SWITCHBOARD_NATIVE_MOBILE_VOICE.md and SWITCHBOARD_ADDENDUM_A_LIVE_PTT.md.
Same GLOBAL RULES (Supabase rhtwtoinmiekttvunlzs, CLI migrations, verify
gates, no secrets).

P5: Migrations for ptt_channels, ptt_members, ptt_transmissions with RLS.
Stand up an SFU (evaluate LiveKit self-hosted on Render vs managed; document
the choice and cost in docs/state/DECISIONS.md). Foundation endpoints for
join/leave/transmit and a transcript webhook that posts each transmission
into its linked Switchboard thread with delivered_to/intended_for as the receipt.
VERIFY: two browser clients on one channel, one talks, the other hears it,
transcript lands in the thread with a correct delivery count.

P6 (Android): extend VoiceBridge to hold a persistent channel connection in
the existing microphone foreground service; audio playback via media session;
notification doubles as channel indicator; map Bluetooth media-button and
rugged-handset PTT key events to transmit start/stop. VERIFY on device:
receive a transmission with the app backgrounded and screen off.

P7 (iOS): PushToTalk framework — only after John confirms the entitlement.
Channel join, incoming playback, Bluetooth PTT button, Dynamic Island state.
If the entitlement is denied, implement the live-audio-room fallback against
the same P5 channels instead.

P8: Agent transmission. Agents transmit only where ptt_members grants
can_transmit. Enforce one unsolicited transmission per agent per channel per
hour (alerts/approvals exempt). Decision-requiring content transmits a short
form and posts full detail plus action buttons to the thread. Honor per-channel
quiet mode, with an exception path for safety items only.
VERIFY: Silas's weather reschedule transmits once, the thread receives the full
detail with approve buttons, and a second unsolicited transmit in the same hour
is blocked and logged.

Add a ptt_usage table metering per-client relay minutes and transcription
minutes from P5 onward — cost visibility is not optional on this one.

RETENTION (decided): implement audio_expires_at / audio_deleted_at on
ptt_transmissions, clients.voice_retention_days (default 30, max 30), and the
nightly ptt-retention-sweep that only marks deleted after storage confirms.
Transcripts are never deleted by the sweep.
```

**Done when**
- Two clients on one channel: one talks, the other hears; transcript lands in the thread with a correct delivery count
- Android receives with the app backgrounded and screen off
- Silas transmits once; a second unsolicited transmit in the hour is blocked and logged
- Retention sweep deletes a seeded expired audio object and leaves its transcript


---

## M — iOS PUSHTOTALK FRAMEWORK + APP STORE READINESS

**You do first**
- Wait for Apple's entitlement decision. Approved → P7 in the L prompt. Denied → the live-audio-room fallback in the same prompt.
- TestFlight first (your properties + one pilot client); App Store only after PTT survives a LUTS show night and a week of Exterior Rescue dispatch.
- Privacy policy published with the voice retention language; App Privacy labels; crash reporting; minimum-version gate; support runbook and SLA written before you sell a seat.

**Done when**
- Locked-screen transmit and Bluetooth PTT button work on a real iPhone (or the fallback room works if denied)
- App Store submission accepted; forced-update path tested


---

## LAUNCH GATE — what "100% good to go" means, in one list

**Foundation**
- [ ] `/ops/agent-health` shows every agent green on all five layers (27 after Phase 0; 30 after B; 35 after H; 36 with Gabriel)
- [ ] Solomon logs `claude-fable-5-1`; C-suite logs `claude-opus-4-8`; department heads log `claude-sonnet-5`
- [ ] Every agent's completed actions carry verified receipts (E); Eden isolated
- [ ] `supabase migration list` clean; no drift

**Automation Nation**
- [ ] Security foundations live (A); Connections Hub live (C); homepage roster reads the Foundation API dynamically
- [ ] `switchboard.automaitionnation.com` and the security page live (N); `lydia.automaitionnation.com` unaffected
- [ ] AN-repo linked to its own database, not Foundation

**Switchboard**
- [ ] Web board embedded on AN and on at least one client property (I)
- [ ] Tenancy tests in Addendum C §C.7 passing
- [ ] Mobile in TestFlight with background capture (K); PTT and App Store are post-launch milestones, not launch blockers

**Two clocks you don't control — start them early**
- [ ] Google OAuth app verification (started at C)
- [ ] Apple PTT entitlement (started at K)

When every box above is ticked, you launch. Everything after M is growth, not readiness.
