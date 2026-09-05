# CLAUDE CODE — MASTER PROMPT, BATCH 1 (item B)
**Prerequisite: Phase 0 green (`/agents` returns 26) and item A merged.**
Paste `01_PROJECT_REF_CORRECTION.md` first, then everything below the line.

---

You are working in the Foundation repo (C:\Users\jjces\OneDrive\Desktop\Foundation, jjcesare86-CLE/Foundation), Supabase project rhtwtoinmiekttvunlzs (CLI linked), deployed at foundation-api-9gpl.onrender.com. Docker is not available; introspect the live database with SQL, never with `db dump` or `db pull`.

Read in full before writing any code:
- docs/specs/00_STATE_OF_THE_BUILD.md   (verified facts — wins over every other doc)
- docs/specs/04_ROSTER_CHANGE_CALEB_SECURITY.md (Phase 0.6 must be done; roster is 27)
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
