# AGENT OPS AUDIT + ELIJAH v1.1 ADDENDUM
v1.0 · Drop into docs/specs/ · Foundation repo

---

# PART A — FULL-ROSTER OPERATIONAL READINESS AUDIT

## A.1 The five layers (an agent is GREEN only if all five pass)
| Layer | Test | Common failure |
|---|---|---|
| L1 Roster | Row active in foundation.ai_employees, valid model_tier, complete house fields | Missing handoff arrays, stale tier |
| L2 Prompt | System prompt present in prompt store, template vars resolvable | Prompt never written; var like {business_phone} unresolvable |
| L3 Access | Required connections/keys live (connection_broker preflight per agent) | Env var never set; token expired; integration never wired |
| L4 Delivery | The agent can actually be reached AND its scheduled jobs fire | Cron never created; endpoint 404; VAPI assistant unlinked |
| L5 Proof | A real smoke invocation completes and logs to llm_usage with cost | Router misroutes; silent exception swallowed |

## A.2 Build: /ops/agent-health (internal, admin-auth)
1. New module `ops_audit.py`:
   - For each active agent: run L1–L5 automatically. L5 = one cheap canned
     smoke prompt per agent ("Introduce yourself in one sentence and name your
     department") through the real router, asserting a logged llm_usage row
     with the EXPECTED model string for its tier.
   - Each agent declares its L3 requirements in a new `required_capabilities`
     JSONB column on ai_employees (e.g. rahab: ["ghl"], zacchaeus:
     ["stripe_read"], silas: ["ghl","maps","gps_feed"], esther: ["ghl"],
     elijah: ["ghl"], joanna: ["stripe"], nathan: ["ghl_social"]). Agents that
     are pure-LLM (Deborah, Peter, Leah…) declare [] and auto-pass L3.
   - L4: enumerate expected crons per agent from a new `agent_jobs` registry
     table (agent_slug, job_name, schedule, last_run_at, last_status) — every
     existing cron must heartbeat this table at run end. No heartbeat in
     (schedule interval × 2) = L4 red.
2. Output: JSON + a simple admin dashboard grid (34 rows × 5 columns,
   green/amber/red) + a markdown report written to docs/state/OPS_AUDIT.md.
3. Schedule: full audit nightly; smoke-call layer weekly (costs pennies);
   red statuses page John via GHL SMS.

## A.3 Claude Code prompt — run the audit NOW
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

## A.4 John's known/likely to-do list (expect the audit to confirm these)
Pre-known blockers from build history — the audit will verify each:
1. `PIPELINE_API_KEY` on the an-sales-pipeline Render service (pending since
   the pipeline-bridge build).
2. `gemini_voice_proxy.py` not deployed to Foundation API — blocks every
   voice-delivery path (Mia/VoiceMIO layer of L4).
3. Google Maps key (Silas) — created? in Render?
4. PostGIS enabled (Silas migration will fail loudly if not).
5. Connections Hub OAuth: Google Cloud app verification submitted (sensitive
   gmail.send scope, 1–2 week review) — gates Esther's client-mailbox sending.
6. Client-side connects only a human can do: each client tapping Connect on
   their cards (Bakerellas, Exterior Rescue, LUTS, Delivered Fireworks as
   dogfood seeds).
7. Foundation Supabase project-ID discrepancy (rhtwtoinmiekttvunlzs vs
   rhtwtoinmiekttvunlzs) — audit's first act is confirming which project the
   deployed API actually points at; everything else assumes that answer.

---

# PART B — ELIJAH v1.1: PHONE CALLS + WEBSITE TRAFFIC

## B.1 Phone call performance (you OWN this data — VAPI/VoiceMIO)
New scoreboard section "Calls" + ingestion:
1. Sources: VAPI call logs (volume, duration, outcome) + GHL call events.
   New rows in mkt_metrics_daily with source='voice', channel='phone', and
   new columns: calls INT, calls_answered INT, calls_booked INT,
   avg_call_seconds INT (migration: ALTER TABLE ADD COLUMN, idempotent).
2. Outcome classification: VAPI end-of-call reports → Haiku classifier tags
   each call (booked | question_answered | missed | voicemail | spam) into a
   new mkt_call_log table (client_id, call_at, direction, duration_s,
   outcome, source_number, vapi_call_id, transcript_ref).
3. **Call attribution via tracking numbers:** provision per-channel GHL
   tracking numbers (website number ≠ GMB number ≠ Facebook ad number) so
   Elijah can say "9 of your 14 calls came from your Google listing." This is
   config work per client, not code: document as a Connections-Hub-style
   setup step in client onboarding.
4. Scoreboard additions: metric card "Calls answered" (e.g. "14 of 15 — Mia
   caught 6 after hours"); What's-working rows can now be call-sourced
   ("Google listing calls booked 4 jobs"). After-hours saves are explicitly
   celebrated — it is THE VoiceMIO retention stat.
5. Insight rule: calls that ended 'missed' during business hours → immediate
   recommendation card routed to owner ("3 missed calls Tuesday 12–1pm —
   want Mia to cover lunch hours?"). That upsell writes itself.

## B.2 Website traffic
1. v1 source: GA4 Data API — add "Google Analytics" card to the Connections
   Hub (same Google OAuth client, add analytics.readonly scope — read-only,
   uncontroversial). Nightly ingestion: sessions, users, top sources, top
   pages, conversions → mkt_metrics_daily source='ga4', new columns:
   sessions INT, site_conversions INT.
2. Fallback for clients without GA4 (common in small biz): if AN built/hosts
   the site, inject our own lightweight first-party pageview beacon (one
   script tag, writes to a mkt_pageviews table) — zero client setup, cookie-
   light, and we control it. Offer both; prefer GA4 when connected.
3. Scoreboard additions: metric card "Website visitors" with WoW delta;
   channel breakdown gains a "where visitors came from" bar; Elijah connects
   the dots across layers in plain English ("Your Facebook ad drove 210
   visits → 31 clicked Book Now → 9 called → 5 booked. That funnel made you
   ~$4,100.").
4. Insight rules: traffic spike with flat bookings → "people are looking but
   not booking — want Deborah to look at the landing page?" ; GMB views up +
   calls up → attribute and celebrate.

## B.3 Claude Code prompt — Elijah v1.1
```
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
