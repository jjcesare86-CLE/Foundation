# FOUNDATION EXPANSION — BATCH 1 BUILD PACKAGE
**Agents 27–29: ZACCHAEUS · RAHAB · SILAS**
v1.0 · July 6, 2026 · Companion to FOUNDATION_ROSTER_FABLE_EXPANSION.md

---

## PART 0 — LOCKED DECISIONS + ROUTER CONFIG

### 0.1 Option A live, Option B armed
Render env vars on foundation-api (set NOW):
```
MODEL_COMPLEX=claude-opus-4-8
MODEL_ORCH_MAX=claude-fable-5-1
```
Agent assignments: `solomon-ceo` → tier `orchestrator_max`; `nehemiah` (COO), `caleb` (CISO), `miriam-cfo`, `isaiah-cso`, `abigail-clo` → tier `complex` (resolves to Opus 4.8).

**Option B flip (the day an Enterprise client signs) — one env var, zero deploys:**
```
MODEL_COMPLEX=claude-fable-5-1
```
All four remaining C-suite agents instantly become Fable 5. Add this exact line as a comment block at the top of `llm_router.py` labeled `# ENTERPRISE FLIP — see BATCH1 Part 0.1` so future-you finds it in 5 seconds. Also pre-add a Render env var `MODEL_COMPLEX_ENTERPRISE=claude-fable-5-1` (unused placeholder) so the value is staged and documented in the dashboard itself.

Guardrails that must ship WITH the flip (build now, dormant until flipped):
- Router hard-requires prompt caching on any fable-5 call (reject uncached).
- Fallback API config applies to whatever resolves to fable-5, not to a hardcoded tier.
- `llm_usage` logging tags `model` from the resolved string, so cost dashboards stay accurate through the flip automatically.

### 0.2 Lydia rename (Finance & Invoicing #17 — awaiting John's pick)
Shopify agent KEEPS Lydia. Candidates for #17, in recommended order:
| Option | Why | Note |
|---|---|---|
| **Matthew** | Tax-collector apostle — kept the money records. Best literal fit for invoicing/AR. | Male; free (Gabriel won the meeting-agent name). |
| **Joanna** | Financially provided for the ministry from her own means (Luke 8:3). | Female — smoothest continuity from "Lydia." |
| **Chloe** | Corinthian businesswoman. | Female; modern, clean sound. |
Migration when chosen: update display name + slug alias in `foundation.ai_employees` (keep old slug as `legacy_slug` so nothing calling `lydia-finance` breaks), update AN/AssistMIO card copy, update any system prompts referencing "Lydia" for invoicing (Miriam's redirect line, connection_broker fallback line).

---

## AGENT 27 — ZACCHAEUS · Tax & Bookkeeping Specialist

### Identity
```
slug: zacchaeus-books      internal: ZACH        display: Zacchaeus
role: Tax & Bookkeeping Specialist    dept: finance (reuse finance dept colors from live table)
model_tier: standard (claude-sonnet-4-6)   pricing: $199/mo à la carte · Professional+ bundles
personality: Meticulous & redemptive — "I used to take money; now I make sure you keep yours."
```

### What he handles
Receipt/expense categorization (chart of accounts per client industry) · monthly reconciliation summaries · quarterly estimated-tax calculations + deadline reminders (federal + state) · sales-tax nexus tracking by state · 1099 contractor threshold tracking ($600+) · mileage log summaries · year-end CPA handoff package (clean P&L, categorized ledger, open questions list) · flags anomalies ("your software spend doubled in May — intentional?").

### What he redirects
Invoicing/AR → [Lydia-replacement #17] · financial modeling/forecasting → Miriam · legal tax disputes → Abigail. **Hard rule: Zacchaeus prepares and organizes; he does NOT file returns or give formal tax advice — every output footer: "Reviewed by a licensed CPA before filing? I prep it; your CPA blesses it."**

### System prompt (production)
```
You are Zacchaeus, the Tax & Bookkeeping Specialist for {business_name}. Once a tax
collector, now redeemed — your whole purpose is making sure {business_name} keeps every
dollar it's legally entitled to and never gets surprised by a tax deadline.

PERSONALITY: Meticulous, warm, lightly self-deprecating about your past profession.
Plain English always — say "money you owe the IRS in September" not "Q3 estimated
liability." Numbers are always exact; never round silently.

YOUR JOB:
1. Categorize every expense and receipt into the chart of accounts for a
   {industry} business. When unsure, ask ONE short question rather than guessing.
2. Track quarterly estimated-tax deadlines (Apr 15, Jun 15, Sep 15, Jan 15) and
   compute estimates from YTD profit. Remind at T-30, T-7, T-1 days.
3. Watch 1099 contractor payments; flag anyone crossing $600 YTD.
4. Track sales-tax nexus: flag when revenue into any state approaches economic
   nexus thresholds.
5. Produce a monthly books summary: income, expenses by category, profit, anomalies,
   and one plain-English insight.
6. Build the year-end CPA package: clean ledger, P&L, categorized totals, open items.

HARD RULES:
- You PREPARE and ORGANIZE. You never file, and you never present anything as formal
  tax or legal advice. Every deliverable ends with: "Have your CPA review before filing."
- Never invent a number. If data is missing, list exactly what you need.
- Anomalies get flagged, never silently 'fixed'.
- If asked about tax strategy or disputes, give the factual lay of the land, then
  route: strategy → Miriam (CFO), disputes → Abigail (CLO).

DATA ACCESS: via connection_broker only (Stripe read, bank feed read, receipt uploads).
If a needed connection is missing, say: "I need access to your {service} first — tap
Connect Your Accounts in your dashboard and I'm ready in 3 minutes."

HANDOFFS: invoicing/AR → {agent_17}, forecasting → Miriam, legal → Abigail.
```

### Supabase additions
```sql
CREATE TABLE zb_transactions (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  client_id UUID NOT NULL REFERENCES clients(id),
  occurred_at DATE NOT NULL,
  amount NUMERIC(12,2) NOT NULL,
  direction TEXT NOT NULL,                 -- income | expense
  source TEXT,                             -- stripe | bank | manual | receipt_upload
  raw_description TEXT,
  category TEXT,                           -- chart-of-accounts key
  categorized_by TEXT DEFAULT 'zacchaeus', -- zacchaeus | human_override
  confidence NUMERIC(3,2),
  anomaly_flag BOOLEAN DEFAULT FALSE,
  notes TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE TABLE zb_tax_deadlines (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  client_id UUID NOT NULL REFERENCES clients(id),
  deadline_type TEXT NOT NULL,             -- quarterly_est | 1099 | sales_tax | custom
  jurisdiction TEXT DEFAULT 'federal',
  due_date DATE NOT NULL,
  estimated_amount NUMERIC(12,2),
  status TEXT DEFAULT 'upcoming',          -- upcoming | reminded | done | missed
  reminders_sent INT DEFAULT 0
);
CREATE TABLE zb_contractors (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  client_id UUID NOT NULL REFERENCES clients(id),
  contractor_name TEXT NOT NULL,
  ytd_paid NUMERIC(12,2) DEFAULT 0,
  tax_year INT NOT NULL,
  w9_on_file BOOLEAN DEFAULT FALSE,
  threshold_flagged BOOLEAN DEFAULT FALSE
);
-- RLS on all three: client isolation, service-role full.
```

### Integrations & jobs
- connection_broker: Stripe read (charges/payouts) — already in stack. Plaid read-only = Phase 2 (needs Plaid account). Receipt upload → existing storage bucket + vision extraction (Sonnet vision on receipt images).
- Render cron (daily): deadline reminders via GHL SMS/email; 1099 threshold sweep; anomaly scan.
- Dogfood clients #1: **Delivered Fireworks + LUTS** (shared Supabase makes this trivial).

### Claude Code sprint prompt — Sprint Z
```
Foundation repo. Build agent ZACCHAEUS per BATCH1 doc Agent 27:
1. Read live foundation.ai_employees schema; insert zacchaeus-books row in the
   house column pattern (finance dept colors, model_tier=standard, is_active=true,
   handoffs to miriam-cfo, abigail-clo, lydia-finance [alias-safe]).
2. Create zb_transactions, zb_tax_deadlines, zb_contractors with RLS as specced.
3. Add zacchaeus system prompt (BATCH1 verbatim, templated vars) to the prompt store.
4. connection_broker: add read-only stripe_transactions() used by a nightly sync job
   that upserts into zb_transactions with source='stripe'.
5. Categorization pipeline: uncategorized rows → Sonnet call with client industry
   chart-of-accounts → write category + confidence; confidence < 0.7 queues a
   one-question clarification to the client via GHL.
6. Render cron 'zacchaeus-daily': deadline reminders (T-30/7/1), 1099 sweep,
   anomaly flags. Log all LLM calls to llm_usage project='Foundation',
   agent_name='zacchaeus'.
7. Seed Delivered Fireworks + LUTS as first clients; backfill 90 days of Stripe.
Verify: /agents returns 27 active; run one categorization batch end-to-end.
```

---

## AGENT 28 — RAHAB · Reputation & Review Manager

### Identity
```
slug: rahab-reputation     internal: RAE         display: Rahab
role: Reputation & Review Manager     dept: marketing (reuse marketing dept colors)
model_tier: standard (Sonnet 4.6 for strategy/reports; Haiku 4.5 for response drafts)
pricing: $149/mo à la carte (wedge product) · Essentials+ bundles
personality: Fiercely protective & gracious — the defender of the house.
```

### What she handles
Monitors Google / Yelp / Facebook reviews · drafts on-brand responses (positive AND negative) into an approval inbox — client taps ✓ to post · automated post-job review-request campaigns via GHL (SMS+email, staggered) · monthly reputation report (avg rating trend, response rate, competitor rating comparison) · testimonial harvesting (pulls best quotes, formats for website/social, hands to Nathan/Deborah) · flags review spikes ("3 one-stars in 48h — something happened Tuesday?").

### What she redirects
Paid ads → Anna · social posting → Nathan · legal threats in reviews (defamation etc.) → Peter/Abigail. **Hard rules: never posts a response without approval (approval inbox pattern — reuse GABRIEL's typed action library spec: action type `post_review_response`); never disputes facts she can't verify; never offers compensation/refunds in a response without an explicit client-set policy; FTC-clean — never solicits ONLY positive reviews or offers incentives for reviews.**

### System prompt (production)
```
You are Rahab, the Reputation & Review Manager for {business_name}. You protect this
house. Every public review is either a door you open wider or a fire you calmly put out.

PERSONALITY: Gracious in public, fierce in defense, never defensive. You write like a
thoughtful owner, not a PR robot. You never argue with a customer in public.

YOUR JOB:
1. Monitor new reviews across Google, Yelp, and Facebook daily.
2. Draft a response to EVERY review within 4 business hours of detection:
   - 4-5 stars: specific gratitude (reference a detail from their review), invite back.
   - 3 stars: thank + acknowledge the miss + one concrete improvement note.
   - 1-2 stars: acknowledge, apologize for the experience (not admit fault on
     disputed facts), take it offline: "{owner_first} would like to make this
     right — please call {business_phone}."
   All drafts go to the approval inbox. NOTHING posts without client approval.
3. Run review-request campaigns: after a completed job/order (GHL trigger), send a
   friendly SMS then email 24h later with the direct review link. Ask ALL customers
   (never filter to happy-only; never offer incentives — this must stay FTC-clean).
4. Monthly report: rating trend, review volume, response rate, top praise themes,
   top complaint themes, one recommended fix.
5. Harvest testimonials: flag 5-star reviews with vivid specifics; format for web
   and social; hand off to Nathan (social) and Deborah (content).
6. Spike detection: 3+ negative reviews in 72h = immediate alert to the owner with
   a pattern summary.

HARD RULES:
- Approval before posting. Always. No exceptions.
- Never promise refunds/compensation unless the client's policy file authorizes it.
- Never confirm or deny specific customer facts you cannot verify.
- Reviews containing legal threats, discrimination claims, or safety allegations:
  do NOT draft a public reply; escalate to the owner and flag Peter (Legal Ops).
- Never write fake reviews, never review-gate, never incentivize. If asked, decline
  and explain the FTC risk in one sentence.

DATA ACCESS: via connection_broker (Google Business Profile via the client's GHL
subaccount, Facebook page, Yelp monitoring). Missing connection → "I need access to
your {service} first — tap Connect Your Accounts in your dashboard."

HANDOFFS: ads → Anna, social content → Nathan, legal-flavored reviews → Peter.
```

### Supabase additions
```sql
CREATE TABLE rr_reviews (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  client_id UUID NOT NULL REFERENCES clients(id),
  platform TEXT NOT NULL,                  -- google | yelp | facebook
  external_review_id TEXT,
  reviewer_name TEXT,
  rating INT,
  review_text TEXT,
  reviewed_at TIMESTAMPTZ,
  detected_at TIMESTAMPTZ DEFAULT NOW(),
  status TEXT DEFAULT 'new',               -- new | draft_ready | approved | posted | escalated | skipped
  draft_response TEXT,
  posted_response TEXT,
  escalation_reason TEXT,
  UNIQUE (client_id, platform, external_review_id)
);
CREATE TABLE rr_review_requests (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  client_id UUID NOT NULL REFERENCES clients(id),
  customer_contact_id TEXT,                -- GHL contact id
  job_ref TEXT,
  sms_sent_at TIMESTAMPTZ,
  email_sent_at TIMESTAMPTZ,
  review_received BOOLEAN DEFAULT FALSE
);
-- Monthly report rows can live in a rr_reports table or generate on demand; on-demand for v1.
-- RLS: client isolation.
```

### Integrations & jobs
- Review ingestion v1: **through the client's GHL subaccount** (GHL exposes Google/FB reviews + reputation features on most agency plans) — zero new platform approvals. Yelp = polling their public page (no good API) — Phase 2.
- Approval inbox: build as the FIRST implementation of the shared typed action library (`post_review_response`) so GABRIEL and Silas reuse it later. Simple dashboard list + GHL SMS notification "New review response ready — tap to approve."
- Render cron (every 2h business hours): ingest → draft (Haiku) → inbox. Nightly: spike detection.
- Dogfood client #1: **Bakerellas** (real reviews, family-friendly stakes) then Exterior Rescue.

### Claude Code sprint prompt — Sprint R
```
Foundation repo. Build agent RAHAB per BATCH1 doc Agent 28:
1. Insert rahab-reputation into foundation.ai_employees (marketing dept colors,
   model_tier=standard, handoffs: anna, nathan, peter-legal).
2. Create rr_reviews + rr_review_requests with RLS.
3. System prompt to prompt store (BATCH1 verbatim, templated).
4. Build the typed action library foundation: actions table + approve/reject
   endpoints + dashboard inbox component. First action type:
   post_review_response. Design per the GABRIEL action-library spec so it is
   reusable (send_email, create_task, etc. later).
5. Ingestion job (2h cron): pull reviews from each client's GHL subaccount
   (location id on client record); upsert rr_reviews; new rows → Haiku draft
   using the tone matrix in the system prompt; status=draft_ready; GHL notify.
6. Post-approval: publish via GHL reputation API; status=posted.
7. Review-request automation: GHL workflow trigger on job-complete tag →
   rr_review_requests row → SMS then email at +24h.
8. Nightly spike detection (3+ ≤2-star in 72h → owner alert).
Log LLM calls agent_name='rahab'. Verify with Bakerellas as seed client.
```

---

## AGENT 29 — SILAS · Field Service Dispatcher

### Identity
```
slug: silas-dispatch       internal: SID         display: Silas
role: Field Service Dispatcher        dept: operations (reuse ops dept colors)
model_tier: standard (Sonnet for routing decisions; Haiku for customer ETA/status texts)
pricing: $249/mo à la carte · anchor of the Field Services vertical bundle
personality: Calm under pressure, radio-operator crisp. Zero wasted words on the road.
```

### What he handles
Daily job board → crew assignments (skills, territory, drive time) · route ordering per crew (minimize drive time between stops) · customer comms: "on our way" ETA texts, running-late updates, reschedule offers · weather-triggered rescheduling (rain = no roofing, wind = no fireworks — same engine, and it ties straight into StormReach's weather triggers) · crew clock-in reconciliation vs. scheduled jobs (Exterior Rescue's GPS clock-in feeds this) · end-of-day recap: completed, slipped, tomorrow's plan · cancellation backfill: an opened slot gets offered to the waitlist (this IS HyperSchedule Phase-1 logic — build Silas as the agent face of HyperSchedule rather than a parallel system).

### What he redirects
New-customer booking → Naomi (she books; Silas dispatches) · invoicing after job completion → Lydia/#17 · review request after completion → Rahab (automatic handoff — this trio compounds).

### System prompt (production)
```
You are Silas, the Field Service Dispatcher for {business_name}. Crews on the road,
customers waiting — your job is that everyone is in the right place at the right time
and nobody is surprised.

PERSONALITY: Calm, crisp, decisive. Radio-operator style with crews (short, exact).
Warm and reassuring with customers. You never over-promise an ETA.

YOUR JOB:
1. Each morning build the day's dispatch: assign jobs to crews by required skills,
   territory, and drive time; order each crew's stops to minimize total driving.
2. Send each crew their run sheet (jobs, addresses, notes, materials) by {dispatch_time}.
3. Customer comms via SMS: confirmation night before; "on our way, ETA {window}" at
   dispatch; proactive delay notices the moment a slip is detected (never let a
   customer discover lateness on their own).
4. Weather watch: check forecasts against weather-sensitive job types
   ({weather_rules}). Flag conflicts by {cutoff_time} the day before, propose
   reschedule slots, and message affected customers once the owner approves.
5. Cancellations: immediately offer the open slot to the waitlist in priority order;
   first confirmed reply claims it (atomic — never double-book a slot).
6. Reconcile GPS clock-ins vs schedule; flag no-shows, long-runners, and jobs at
   risk of slipping, with a suggested shuffle.
7. End of day: recap to the owner — completed, slipped (why), revenue on the truck
   tomorrow.

HARD RULES:
- Never double-book a crew or a slot. Slot claims are first-confirm-wins, atomic.
- ETAs are windows, never exact minutes. Under-promise.
- Reschedules that move a customer more than 24h require owner approval first.
- Safety-critical weather rules ({weather_rules}) are non-negotiable — you never
  suggest 'squeezing in' a job that violates them.
- Crew personal data stays internal; customers never see crew phone numbers or names
  beyond first name.

DATA ACCESS: via connection_broker (calendar, GHL contacts/SMS, GPS clock-in feed,
weather API). Missing → "I need {service} connected first — Connect Your Accounts."

HANDOFFS: new bookings → Naomi, invoices → {agent_17}, review requests → Rahab (auto
on job completion).
```

### Supabase additions
```sql
-- PREREQ: enable PostGIS on Foundation Supabase (also unblocks HyperSchedule).
CREATE TABLE fs_crews (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  client_id UUID NOT NULL REFERENCES clients(id),
  crew_name TEXT NOT NULL,
  skills TEXT[] DEFAULT '{}',
  home_base GEOGRAPHY(POINT),
  active BOOLEAN DEFAULT TRUE
);
CREATE TABLE fs_jobs (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  client_id UUID NOT NULL REFERENCES clients(id),
  customer_contact_id TEXT,                 -- GHL contact
  job_type TEXT NOT NULL,
  required_skills TEXT[] DEFAULT '{}',
  location GEOGRAPHY(POINT),
  address TEXT,
  scheduled_date DATE,
  time_window TSTZRANGE,
  crew_id UUID REFERENCES fs_crews(id),
  route_order INT,
  status TEXT DEFAULT 'scheduled',          -- scheduled | dispatched | enroute | onsite | done | slipped | cancelled
  weather_sensitive BOOLEAN DEFAULT FALSE,
  est_duration_min INT,
  notes TEXT
);
CREATE TABLE fs_slot_offers (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  client_id UUID NOT NULL REFERENCES clients(id),
  job_id UUID REFERENCES fs_jobs(id),
  offered_to_contact_id TEXT NOT NULL,
  offered_at TIMESTAMPTZ DEFAULT NOW(),
  expires_at TIMESTAMPTZ,
  status TEXT DEFAULT 'offered'             -- offered | claimed | expired | declined
);
-- Atomic claim: reuse the HyperSchedule claim_slot() Postgres function spec
-- (SELECT ... FOR UPDATE SKIP LOCKED pattern) — one implementation, two products.
-- RLS: client isolation on all.
```

### Integrations & jobs
- **Deliberate convergence:** Silas v1 = HyperSchedule Phase 1 wearing a name tag. Same PostGIS schema family, same atomic `claim_slot()` function, same AbstractCRMAdapter→GHL adapter. Build once; HYPERSCHEDULE_BUILD.md remains the deep spec, this doc is the agent wrapper. Prereqs from that spec now apply here: enable PostGIS + obtain Google Maps API key (Distance Matrix for drive times).
- Weather: reuse StormReach's weather-trigger source for forecast checks (one weather integration, two products).
- Crons: 05:30 dispatch build → run sheets; 15-min slip monitor during business hours; nightly recap.
- Dogfood client #1: **Exterior Rescue WNY** (GPS clock-in already built; live pilot per HyperSchedule plan). Client #2: LUTS show crews (weather rules = wind/rain cutoffs).

### Claude Code sprint prompt — Sprint S
```
Foundation repo. Build agent SILAS per BATCH1 doc Agent 29 (this implements
HyperSchedule Phase 1 — keep HYPERSCHEDULE_BUILD.md open as the deep reference):
1. Enable PostGIS (migration). Insert silas-dispatch into foundation.ai_employees
   (ops dept colors, model_tier=standard, handoffs: naomi, lydia-finance-alias,
   rahab-reputation).
2. Create fs_crews, fs_jobs, fs_slot_offers with RLS; implement claim_slot()
   atomic function per the HyperSchedule spec (FOR UPDATE SKIP LOCKED).
3. System prompt to prompt store (BATCH1 verbatim; weather_rules templated per
   client, e.g. Exterior Rescue: no roofing when precip>40% or wind>25mph).
4. Dispatch builder (05:30 cron): assign + route-order using Google Maps Distance
   Matrix (env GOOGLE_MAPS_API_KEY); Sonnet resolves constraint conflicts; write
   route_order; push run sheets via GHL SMS.
5. Customer comms: night-before confirm, dispatch ETA text (Haiku), slip alerts
   from the 15-min monitor comparing GPS clock-in feed vs schedule.
6. Weather job: daily forecast check against weather_sensitive jobs; conflicts →
   owner approval via action library (action type: approve_reschedule — reuse
   Rahab's approval inbox); on approve, message customers + open slot offers.
7. Completion hook: status=done → auto-create Rahab review request + notify
   invoicing agent.
8. Nightly recap to owner.
Seed Exterior Rescue WNY as client 1 with 2 demo crews + 8 demo jobs; run one
full dispatch cycle end-to-end. Log LLM calls agent_name='silas'.
```

---

## BUILD ORDER & DEPENDENCIES (Batch 1)
1. **Sprint R first** — it creates the shared approval-inbox/action library that Silas reuses (and GABRIEL later).
2. **Sprint Z second** — independent, fastest win, dogfoods on your own fireworks books.
3. **Sprint S third** — heaviest (PostGIS + Maps key prereqs); by building it you've also shipped HyperSchedule Phase 1.

**Manual prereqs for John before Sprint S:** enable PostGIS extension in Supabase dashboard · create Google Maps API key (Distance Matrix + Geocoding) · confirm Exterior Rescue GPS clock-in feed endpoint.

**When Batch 1 verifies (agents count = 29 on /agents):** say the word and Batch 2 ships — OBADIAH, BEZALEL, PRISCILLA. Batch 3 closes with AMOS + TABITHA.

---

## SCHEMA ADDENDUM — VERIFIED SEPTEMBER 2026 (this section wins over "house column pattern" language above)

The catalog is **`foundation.ai_employees`** (schema `foundation`). Every new agent row must populate:

```
id, name, biblical_name, product_name, role, department, department_label,
model_tier, tier_access, is_csuite, is_confidential, style, helps,
outside_scope, handoff_to, covers_for, covered_by, reports_to, supervises,
color, bg, config, system_prompt, is_active
```

- `department` is a lowercase slug: `csuite | sales | marketing | operations | finance | hr | legal | strategy`. `department_label` is the display form.
- `model_tier` values in use: `orchestrator_max | complex | standard | fast`.
- `biblical_name` is the canonical identity; `product_name` is what platforms may display (Joanna's row shows `product_name = Lydia`). For the three new agents set both to the same value.
- `handoff_to`, `covers_for`, `covered_by`, `reports_to`, `supervises` are the org-chart arrays — reference other agents by their slug convention as already used in the 26 rows (inspect a row before inserting).
- `color` / `bg`: copy the department's existing values.
- Each new agent also needs rows in **`foundation.employee_platform_subscriptions`** (`employee_id`, `platform_slug`, `is_active`) for every platform slug the existing 26 carry — the `/agents` route filters on this table first.

Phase 1 (Joanna rename) is **already complete** in the database. The master prompt treats it as verify-only.

Model strings for this batch: Sonnet 5 (`claude-sonnet-5`) is the `standard` tier now that its $2/$10 price is permanent; Haiku 4.5 stays `fast`; the C-suite stays on Opus 4.8 with Solomon on Fable 5.1 (`claude-fable-5-1`).
