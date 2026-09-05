# ELIJAH MARKETING SCOREBOARD — BUILD SPEC v1.0
**Operationalizing agent #21 (Elijah/DEAN, Strategic Analyst) into a client-facing analytics product**
Drop into docs/specs/ · Run after Batch 1 + Autopilot Nuances (depends on connection_broker, preflight, playbook engine)

---

## 1. WHAT EXISTS vs WHAT'S MISSING

| Piece | Status |
|---|---|
| Elijah on the roster (performance reporting, KPI dashboards, A/B analysis, attribution) | ✅ Exists — on paper |
| Data pipelines feeding him (GHL, Meta Ads, Google Ads/GA4/GMB, email/SMS stats) | ❌ None |
| Metrics warehouse tables | ❌ None |
| Client-facing visual dashboard | ❌ None |
| Plain-English weekly digest | ❌ None |
| Recommendation → action handoff to other agents | ❌ None |

Decision: NO new agent. Elijah keeps the seat; we give him data, a screen, and a voice. This also completes the marketing team story for sales: Deborah writes → Nathan posts → Anna runs ads → Esther emails → Rahab defends → **Elijah proves it worked.**

## 2. PRODUCT PRINCIPLES (fifth-grader rules, same as Connections Hub)
- Four numbers max above the fold. Leads, cost per lead, click rate, booked revenue/jobs. Everything else is one tap deeper.
- Every metric gets a plain-English translation ("$18 to get one customer — down from $24").
- Never show a chart without a sentence saying what it means.
- Every insight ends in a button, not a homework assignment: "Want Esther to rewrite that CTA?" → one tap → task created via the action library.
- Honest by default: if data is thin ("only 40 clicks — too early to judge"), Elijah says so instead of fake confidence. Rigor slider floors at 80 for Elijah.

## 3. DATA LAYER

### 3.1 Metrics warehouse (migrations)
```sql
CREATE TABLE mkt_metrics_daily (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  client_id UUID NOT NULL REFERENCES clients(id),
  metric_date DATE NOT NULL,
  source TEXT NOT NULL,          -- ghl | meta_ads | google_ads | ga4 | gmb | email | sms | stripe
  channel TEXT,                  -- facebook | instagram | google | email | sms | organic | referral
  campaign_ref TEXT,
  impressions INT DEFAULT 0,
  clicks INT DEFAULT 0,
  spend NUMERIC(12,2) DEFAULT 0,
  leads INT DEFAULT 0,
  bookings INT DEFAULT 0,
  revenue NUMERIC(12,2) DEFAULT 0,
  raw JSONB,
  UNIQUE (client_id, metric_date, source, channel, campaign_ref)
);
CREATE TABLE mkt_cta_performance (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  client_id UUID NOT NULL REFERENCES clients(id),
  cta_text TEXT NOT NULL,
  asset_ref TEXT,                -- email id, ad id, post id, page url
  channel TEXT NOT NULL,
  period_start DATE, period_end DATE,
  impressions INT DEFAULT 0,
  clicks INT DEFAULT 0,
  conversions INT DEFAULT 0,
  created_by_agent TEXT          -- esther | anna | nathan | deborah — closes the loop on WHOSE copy wins
);
CREATE TABLE mkt_insights (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  client_id UUID NOT NULL REFERENCES clients(id),
  week_of DATE NOT NULL,
  insight_type TEXT,             -- winner | loser | anomaly | opportunity | too_early
  headline TEXT NOT NULL,        -- plain-English one-liner
  evidence JSONB,                -- metric refs backing it
  recommended_action TEXT,
  action_agent TEXT,             -- which agent executes if approved
  action_status TEXT DEFAULT 'proposed',  -- proposed | approved | executed | dismissed
  confidence TEXT DEFAULT 'solid'         -- solid | early | thin
);
-- RLS: client isolation on all three.
```

### 3.2 Ingestion (via connection_broker — Connections Hub powers all of it)
- **GHL** (v1 workhorse): contacts/leads by source, pipeline stage moves, SMS/email stats, GMB insights where exposed. Nightly cron.
- **Meta Ads + Google Ads**: v1 = through GHL's ad reporting where the client's account is connected there (zero new OAuth apps). v2 = direct Marketing API tokens as new Connections Hub cards.
- **Esther's sends**: log CTA text + clicks straight into mkt_cta_performance at send/track time (we own this pipeline end-to-end — richest data, zero external deps).
- **Nathan's posts / Rahab's review links**: same in-house logging pattern; use UTM-tagged short links generated at publish time so attribution is deterministic, not inferred.
- **Stripe/Joanna**: revenue join for true ROI (spend → revenue, not just spend → clicks).
- Preflight (Module 3) runs before every ingestion batch.

## 4. ELIJAH'S JOBS (system prompt additions)
```
SCOREBOARD DUTIES:
1. Nightly: reconcile ingested metrics; flag anomalies (metric ±40% vs 4-week
   baseline) into mkt_insights as type=anomaly.
2. Weekly (Mon 07:00 client-local): produce the Weekly Scoreboard — top 4
   numbers with week-over-week deltas, 2-3 "what's working" rows, 1-2 "what's
   not" rows, exactly ONE recommended action routed to the agent who owns it
   (Esther/Anna/Nathan/Rahab) through the approval inbox.
3. Attribution honesty: state HOW you know ("UTM-tracked", "GHL source field")
   and mark confidence. If sample size is too small, say type=too_early and
   recommend waiting, not acting.
4. Plain English always: translate every metric ("CTR 6.1%" → "6 of every 100
   people who saw it clicked — that's excellent for Facebook").
5. Never invent numbers. Missing connection → name it + Connections Hub link.
6. A/B calls require minimum sample (default 100 clicks or 1,000 impressions
   per variant) before declaring a winner.
HANDOFFS: execute-copy changes → Esther/Nathan/Deborah, budget shifts → Anna
(owner approval required for any spend change), review issues → Rahab,
revenue questions → Hannah/Miriam.
```

## 5. DASHBOARD (client-facing, per mockup approved in chat)
Route `/dashboard/scoreboard`. Components:
1. Header: Elijah avatar + week selector.
2. Four metric cards with deltas (green/red arrows).
3. "What's working / what's not" card: CTA-level rows with rates, tap → detail
   (trend sparkline + Elijah's sentence).
4. "Elijah's call" card: the ONE weekly recommendation + approve button →
   action library task for the owning agent; dismissed recommendations log
   action_status=dismissed (Elijah learns client preferences from dismissals).
5. Channel breakdown (tap-deeper page): leads + cost per lead by channel,
   simple bar chart, one sentence per channel.
6. Delivery: dashboard + weekly GHL email/SMS digest ("Your scoreboard is
   ready — 47 leads this week, up 21%") + optional Mia voice briefing
   ("Call me and I'll read you the week").

## 6. RESELL PACKAGING
- Included in Professional+ marketing bundles (it's the proof layer that
  retains subscriptions — clients cancel what they can't see working).
- À la carte "Marketing Scoreboard" $99/mo for clients who only buy Rahab or
  Esther — cheapest door into the full marketing team.
- Sales demo: seed a fictional client with 8 weeks of realistic metrics so
  reps (and the AN homepage) can show a living scoreboard.

## 7. CLAUDE CODE PROMPT
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
```
