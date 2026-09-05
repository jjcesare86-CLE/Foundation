# FOUNDATION AI EMPLOYEE ROSTER — FABLE 5 UPGRADE & EXPANSION PLAN
**Version 1.0 · July 6, 2026 · Foundation Layer (Supabase `rhtwtoinmiekttvunlzs` · foundation-api-9gpl.onrender.com)**

---

## PART 1 — CURRENT ROSTER (26 AGENTS)

Single source of truth: Foundation. AN, AssistMIO, VoiceMIO, Blast Video, and MRLIN all pull from it. Tier gating lives in the platforms, never in Foundation. Internal all-caps slugs (MAYA, REX, OTTO…) retained for AN backward compatibility; biblical names are the product identity.

### C-SUITE — Orchestrators (currently `claude-opus-4-7` · Enterprise tier)
| # | Name | Role | Excels At |
|---|------|------|-----------|
| 1 | **Solomon** | CEO | Strategic direction, P&L ownership, partnership decisions, cross-department synthesis, quarterly planning. Delegates day-to-day to Caleb. |
| 2 | **Caleb** | COO | Strategy-to-execution translation, KPI tracking, blocker removal, operational oversight. Redirects financial modeling to Miriam. |
| 3 | **Miriam** | CFO | Cash flow management, investor-ready financial models, burn rate monitoring, financial risk flagging. Redirects invoicing/AR to Lydia. |
| 4 | **Isaiah** | CSO | M&A opportunities, competitive intelligence, 12-month roadmap, partnership identification, market positioning. |
| 5 | **Abigail** | CLO | Contract authority, IP filings, cross-jurisdiction compliance, executive legal counsel. |

### SALES — `claude-sonnet-4-6`
| # | Name | Role | Excels At |
|---|------|------|-----------|
| 6 | **John** (REX) | VP of Sales | Outbound closing, objection handling, pipeline ownership, booking meetings around the clock. |
| 7 | **Paul** (ACE) | Sales Automation Engineer | Connecting tools, eliminating repetitive sales tasks, workflow automation. |
| 8 | **Mary** (ARIA) | Client Success Manager | Support tickets, satisfaction, escalation, onboarding support, proactive check-ins, retention & upsell. |
| 9 | **Luke** (BLAKE) | Proposal & Pricing Specialist | Proposals, quotes, pricing structures, retention depth. |

### MARKETING — `claude-sonnet-4-6`
| # | Name | Role | Excels At |
|---|------|------|-----------|
| 10 | **Deborah** (MAYA) | Brand & Content Strategist | Brand voice, content strategy, blogs, emails, scripts — always on-brand. |
| 11 | **Nathan** (KAI) | Social Media Manager | 33-platform brand launches, social strategy, engagement, community management. |
| 12 | **Anna** (NINA) | Ads & Paid Media Specialist | Google + Meta campaign management across every channel. |
| 13 | **Esther** (CLARA) | Email & SMS Marketing | Sequences, campaigns, nurture flows on autopilot. |
| 14 | **Gideon** (DREW) | Video & Content Producer | Blast Video pipeline integration — scripts, storyboards, production. |

### OPERATIONS — Sonnet 4.6 (Haiku 4.5 for Naomi + Martha)
| # | Name | Role | Excels At |
|---|------|------|-----------|
| 15 | **Joseph** (OTTO) | Operations Director | Request routing, gap flagging, operational coordination. |
| 16 | **Naomi** (SAGE) | Scheduling & Appointments *(Haiku)* | High-volume booking, calendar management, appointment triage. |
| 17 | **Lydia** | Finance & Invoicing | Invoicing, AR, Stripe operations. (Distinct from LYDIA the Shopify Agent #18 — flag for rename/dedup, see Part 3 notes.) |
| 18 | **Martha** | Admin & Back-Office *(Haiku)* | High-volume admin, document handling, back-office triage. |
| 19 | **Ezra** (VINCE) | Tech & IT Support | Technical builds, IT support, voice automation infrastructure. |

### LEGAL & STRATEGY — `claude-sonnet-4-6`
| # | Name | Role | Excels At |
|---|------|------|-----------|
| 20 | **Peter** (LEO) | Legal Operations | Contracts, ToS, privacy policies, legal review, risk assessment. |
| 21 | **Elijah** (DEAN) | Strategic Analyst | Performance reporting, KPI dashboards, A/B analysis, channel attribution. |
| 22 | **Rebekah** | Legal Analyst | Legal research, compliance analysis, supports Abigail. |

### PEOPLE & CULTURE — Sonnet 4.6 (Haiku for Eden intake)
| # | Name | Role | Excels At |
|---|------|------|-----------|
| 23 | **Leah** | Executive Assistant | Calendar, correspondence, executive support. |
| 24 | **Hannah** (FIN) | Financial Analyst | Revenue reporting, expense tracking, Stripe analytics, projections. |
| 25 | **Delilah** (ORI) | Talent & HR Director | Finding, screening, onboarding hires; HR operations. |
| 26 | **Eden** | Headspace Counselor | Confidential wellbeing support. **Hard privacy rule:** `eden_sessions` isolated — zero foreign keys to HR/performance data. Available on all tiers, never gated. |

**Adjacent (not in the 26):** GABRIEL (#17-adjacent, Meeting Scribe & Executor — PAUSED), LYDIA Shopify Engine (multi-tenant), and the AssistMIO sales pipeline squad (Andrew, Phoebe, Tobias, Magdalene, Luke-Sales).

---

## PART 2 — FABLE 5 UPGRADE PLAN

### 2.1 The facts that drive the plan
- **Fable 5.1** (`claude-fable-5-1`): $10/$50 per MTok. Mythos-class — a tier *above* Opus. 1M context, 128K output. Its lead over Opus grows with task length/complexity. Prompt caching cuts cached input to $0.25/MTok.
- **Opus 4.8** (`claude-opus-4-8`): $5/$25 — exactly half Fable. Your C-suite is still pinned to `claude-opus-4-7`, which is now previous-generation. **Upgrading 4.7 → 4.8 is free performance at the same price.**
- **Sonnet 5**: $2/$10 is now the permanent price (the planned Sept 1 increase was cancelled) — cheaper than Sonnet 4.6. Cheaper than Sonnet 4.6 right now. Evaluate for all 17 department heads.
- **Tokenizer:** Fable 5.1 and Opus 4.7+ produce ~30% more tokens for the same text. Prompt caching on every C-suite system prompt is non-negotiable.
- **Fallback API:** Fable 5.1 safeguard-flagged queries (bio/cyber — essentially irrelevant to your business agents) reroute to Opus 4.8 and bill at Opus rates. API customers must configure this. Wire it into `llm_router.py` once.
- **Retention:** Fable traffic carries a 30-day safety-monitoring retention requirement. Fine for AN internal + client business ops; note it in AssistMIO's privacy policy.

### 2.2 New routing (recommended — Option A, "Sniper")
```
Solomon (CEO)                          → claude-fable-5-1        (NEW TIER: orchestrator_max)
Caleb, Miriam, Isaiah, Abigail         → claude-opus-4-8       (upgrade from 4.7)
All 17 department heads/specialists    → claude-sonnet-4-6     (evaluate Sonnet 5 @ intro pricing)
Naomi, Martha, Eden-intake triage      → claude-haiku-4-5-20251001 (unchanged)
All voice                              → gemini-3.1-flash-live (unchanged)
```

**Why Solomon alone gets Fable:** Solomon's job — cross-department synthesis, quarterly planning, P&L strategy — is the exact "long-running, ambiguous, multi-step" workload Fable dominates at. The other four C-suite agents run bounded workflows (Caleb's KPI reviews, Miriam's models, Abigail's contract passes) where Opus 4.8 clears the quality bar at half the cost. This is your own skill rule: *never use the expensive model where the cheaper one reliably clears the bar.*

**Escalation valve:** add an `orchestrator_max` tier so ANY C-suite agent can escalate a single task to Fable 5.1 when Solomon (or the task classifier) deems it high-complexity. Haiku pre-filter decides; Fable executes only when justified. This gives you Mythos-class capability across the whole C-suite without Mythos-class bills.

### 2.3 Option B — "Full Mythos C-Suite" (marketing play)
Put all 5 C-suite agents on Fable 5.1 and market the Enterprise tier as **"Powered by Anthropic's Mythos-class intelligence."** Cost: ~2x current C-suite spend (before the ~30% tokenizer uplift, largely offset by caching + Fable's fewer-turns token efficiency on complex tasks). If Enterprise seats are $1,999+/mo, the margin absorbs it and the positioning is a genuine differentiator no competitor selling GPT-wrapper "AI employees" can claim. **My call: ship Option A now, flip to Option B via env vars the day an Enterprise client signs.** Zero code changes needed — that's what the router is for.

### 2.4 `llm_router.py` changes
```python
class TaskTier(Enum):
    FAST = "fast"
    STANDARD = "standard"
    COMPLEX = "complex"                 # C-suite default
    ORCHESTRATOR_MAX = "orchestrator_max"  # NEW — Solomon + escalations
    VOICE = "voice"
    LONGCTX = "longctx"

MODEL_MAP = {
    TaskTier.FAST:             os.getenv("MODEL_FAST", "claude-haiku-4-5-20251001"),
    TaskTier.STANDARD:         os.getenv("MODEL_STANDARD", "claude-sonnet-4-6"),
    TaskTier.COMPLEX:          os.getenv("MODEL_COMPLEX", "claude-opus-4-8"),          # was 4-7
    TaskTier.ORCHESTRATOR_MAX: os.getenv("MODEL_ORCH_MAX", "claude-fable-5-1"),          # NEW
    TaskTier.VOICE:            os.getenv("MODEL_VOICE", "gemini-3.1-flash-live"),
    TaskTier.LONGCTX:          os.getenv("MODEL_LONGCTX", "claude-fable-5-1"),           # 1M ctx — replaces Gemini Pro for Claude-native long-context
}
```
Additional router work:
1. **Fallback API config** for `claude-fable-5-1` calls (safeguard reroutes → Opus 4.8, billed at Opus rates; log the fallback in `llm_usage.task_type = 'fable_fallback'`).
2. **Force `use_cache=True`** whenever model is Fable or Opus — reject uncached C-suite calls at the router level.
3. **Cost tracking:** update `estimated_cost_usd` rates: fable-5 = 10/50, opus-4-8 = 5/25, cached Fable 5.1 input = 0.25.
4. **Render env vars:** `MODEL_COMPLEX=claude-opus-4-8`, `MODEL_ORCH_MAX=claude-fable-5-1`.

### 2.5 Per-agent capability upgrades unlocked by Fable 5.1
- **Solomon:** 1M context means he can ingest an ENTIRE client's Foundation footprint (all agent transcripts, financials, campaigns) in one quarterly-review pass. Build a `quarterly_synthesis` skill that dumps everything and lets Fable produce the board-level readout. This was impossible before.
- **Miriam:** Fable's document/chart/table vision is markedly better — pipe raw PDFs (bank statements, P&Ls, investor decks) directly instead of pre-extracting.
- **Abigail + Rebekah:** Fable redlining benchmarked at/above senior-lawyer-tool level in blind review. Add an escalation path: Rebekah (Sonnet) does first-pass review → flags high-stakes contracts → Abigail escalates those to `orchestrator_max`.
- **Isaiah:** long-horizon competitive-intel research runs (multi-hour agentic loops) are Fable's home turf — wire his deep-research jobs through `orchestrator_max` with the Batch API where async is acceptable (50% discount stacks).
- **All dept heads:** evaluate Sonnet 5 before Aug 31 while intro pricing makes the test free-ish. If it clears quality bars, `MODEL_STANDARD=claude-sonnet-5` is another env-var flip.

### 2.6 Update the efficiency skill to v1.2
Your `internal-educating-efficiency-skill` registry still lists `claude-opus-4-6` as the complex tier and predates Fable entirely. v1.2 changes: add Fable 5.1 row (orchestrator_max / longctx), bump complex tier to Opus 4.8, add Sonnet 5 evaluation note, add Fallback API + 30-day retention notes, add version-history entry.

---

## PART 3 — NEW RESELLABLE AI EMPLOYEES (AGENTS 27–34)

Selection criteria: (a) real recurring SMB pain, (b) maps to verticals you already have credibility in (fireworks/events, home services via Exterior Rescue, real estate via Broker Broker, e-comm via LYDIA/Bakerellas), (c) no name collisions with the existing 26 + sales squad + GABRIEL, (d) biblical name that actually FITS the job.

### Tier-1 builds (do these first — fastest to revenue)

**27. ZACCHAEUS — Tax & Bookkeeping Specialist** · Finance dept · Sonnet 4.6
The tax collector himself. Receipt categorization, quarterly estimated-tax reminders, sales-tax nexus tracking, 1099 contractor tracking, books-to-CPA handoff packages. *Why it sells:* every SMB dreads this; bookkeepers charge $300–800/mo. Sell at $149–249/mo standalone. Integrations: Stripe (already in stack), Plaid read-only, QuickBooks API. **You dogfood it on Delivered Fireworks + LUTS immediately.**

**28. RAHAB — Reputation & Review Manager** · Marketing dept · Sonnet (Haiku for review-response drafting)
Protected her house and family by managing dangerous relationships — the reputation defender. Monitors Google/Yelp/Facebook reviews, drafts on-brand responses (approval inbox pattern from GABRIEL's action library), automated review-request campaigns post-job via GHL, local-SEO reputation reporting. *Why it sells:* #1 request from local service businesses; standalone tools charge $99–299/mo with no intelligence. Perfect wedge product for the prospect engine's four campaigns.

**29. SILAS — Field Service Dispatcher** · Operations dept · Sonnet (Haiku triage)
Paul's traveling companion — always on the road. Job scheduling + routing for field crews, GPS-aware dispatch, customer ETA texts, weather-delay rescheduling (fireworks shows AND roofing!), crew clock-in reconciliation. *Why it sells:* HVAC/plumbing/roofing/landscaping is the richest vertical in your prospect engine; ServiceTitan starts ~$300/mo/tech. Exterior Rescue is the live pilot — its GPS clock-in system already exists.

### Tier-2 builds

**30. OBADIAH — Property & Tenant Manager** · Operations dept · Sonnet (Haiku for tenant comms)
Steward of the king's house. Rent reminders, maintenance-ticket intake + vendor dispatch (pairs with Silas), lease renewal tracking, tenant communication, owner statements. *Why it sells:* landlords with 2–50 units are massively underserved (AppFolio requires 50+ units). Broker Broker Realty is the built-in pilot + referral channel.

**31. BEZALEL — Design & Creative Director** · Marketing dept · Sonnet + Gemini/Higgsfield image gen
The first person in scripture described as Spirit-filled *for craftsmanship*. Logo concepts, brand kits, social graphics, ad creatives, one-pagers — generated through your existing Higgsfield/Gemini image pipeline and brand_assets table. *Why it sells:* completes your marketing suite (Deborah writes, Nathan posts, Anna runs ads, Gideon does video — nobody DESIGNS). Bundles beautifully with Blast Video and the Social Brand Launcher.

**32. PRISCILLA — Training & SOP Builder** · People & Culture dept · Sonnet
She taught Apollos — the great teacher. Turns tribal knowledge into SOPs, builds onboarding curricula for new hires, generates training scripts/quizzes, keeps a living process wiki per client. *Why it sells:* every business that hires employee #2 needs this; nothing good exists under $500/mo. Natural upsell alongside Delilah (HR) and Jubilant Careers placements — hire through Jubilant, train through Priscilla.

### Tier-3 builds (vertical plays)

**33. AMOS — Compliance & License Tracker** · Legal dept · Haiku (it's mostly deadline logic) with Sonnet analysis
The prophet who held everyone to the standard. Tracks licenses, permits, insurance renewals, OSHA requirements, CEU deadlines by trade and state; files renewal reminders with lead time; drafts renewal paperwork. *Why it sells:* trades, cannabis (canna.ai tie-in — Metrc compliance), pyrotechnics (ATF licensing — you live this), mortgage (NMLS — Broker Broker lives this). Nobody wakes up wanting this; everybody pays after one lapsed license.

**34. TABITHA — Nonprofit & Donor Relations** · Sales dept (donor pipeline = sales pipeline) · Sonnet
"Full of good works and acts of charity." Donor CRM management, grant-deadline tracking + draft writing, donation-receipt automation, campaign appeals, board-report generation. *Why it sells:* 1.5M US nonprofits, chronically understaffed, grant writers charge $75–150/hr. Zero competitors in the "AI employee" framing. Also a genuinely good-karma product line.

### Roster hygiene items (do during the same migration)
1. **Lydia collision:** Foundation #17 Lydia (Finance & Invoicing) vs. LYDIA the Shopify Agent. Recommend renaming the Shopify agent's display to "Lydia · Commerce" or giving the invoicing agent a merged home under Hannah — pick one before AssistMIO clients see both.
2. **GABRIEL:** stays PAUSED per standing decision — but when reactivated he slots in as #35, and his typed action library (send_email, create_task, update_crm…) is the execution backbone Rahab and Silas should reuse. Build their approval-inbox on his spec so the work compounds.
3. **Seed data pattern:** insert the 8 new agents using the same `foundation.ai_employees` column pattern as the C-suite migration (slug, all-caps internal, biblical display, role, dept, model_tier, tier, personality, handles, redirects, handoff arrays, colors, is_active). Have Claude Code read the live schema first — don't trust any doc over the actual table.

### Suggested à la carte pricing (mirrors Foundation Pricing Engine logic)
| Agent | Standalone | In-bundle role |
|---|---|---|
| Zacchaeus | $199/mo | Professional+ tiers |
| Rahab | $149/mo | Essentials+ (wedge product — price to land) |
| Silas | $249/mo | Field-services vertical bundle anchor |
| Obadiah | $199/mo | Real-estate vertical bundle anchor |
| Bezalel | $179/mo | Marketing bundle add-on |
| Priscilla | $149/mo | HR bundle add-on, Jubilant cross-sell |
| Amos | $99/mo | Compliance add-on, canna.ai/trades bundles |
| Tabitha | $179/mo | Nonprofit vertical anchor |

Roster grows 26 → 34. Enterprise tier messaging: **"34 AI employees. One payroll line."**

---

## PART 4 — CLAUDE CODE KICKOFF PROMPT

```
Read the Foundation repo (jjcesare86-CLE/Foundation). Tasks, in order:

1. MODEL ROUTING: In llm_router.py, add TaskTier.ORCHESTRATOR_MAX → env
   MODEL_ORCH_MAX default "claude-fable-5-1". Change MODEL_COMPLEX default to
   "claude-opus-4-8". Add Anthropic Fallback API config for fable-5 calls
   (reroutes bill at Opus 4.8 rates — log tier as 'fable_fallback' in
   llm_usage). Enforce prompt caching on all COMPLEX and ORCHESTRATOR_MAX
   calls. Update cost table: fable-5 10/50, opus-4-8 5/25, cache-hit 10%.

2. AGENT ASSIGNMENTS: Read the live foundation.ai_employees schema FIRST.
   Set solomon-ceo model_tier to orchestrator_max. Set nehemiah (COO), caleb (CISO),
   miriam-cfo, isaiah-cso, abigail-clo to claude-opus-4-8. Leave all
   Sonnet/Haiku assignments unchanged.

3. NEW AGENTS: Insert 8 new employees matching the existing column pattern:
   zacchaeus (Tax & Bookkeeping, finance, standard), rahab (Reputation &
   Reviews, marketing, standard), silas (Field Dispatch, ops, standard),
   obadiah (Property Manager, ops, standard), bezalel (Design Director,
   marketing, standard), priscilla (Training & SOPs, people, standard),
   amos (Compliance Tracker, legal, fast), tabitha (Donor Relations,
   sales, standard). Full role descriptions in
   FOUNDATION_ROSTER_FABLE_EXPANSION.md Part 3. All is_active=true,
   with handles/redirects/handoff arrays written in the house style.

4. VERIFY: hit /agents (or /public/agents) and confirm 34 active employees
   return, then confirm AN and AssistMIO frontends render the new count.

5. SKILL: bump internal-educating-efficiency-skill to v1.2 per Part 2.6.

Do NOT touch eden_sessions isolation, tier-gating (stays in platforms),
or GABRIEL (paused).
```

---

**Decision points for John:**
- Option A (Solomon-only on Fable + escalation valve) vs Option B (full Mythos C-suite) — A recommended, B is one env-var flip away.
- Lydia name collision resolution.
- Which 2–3 of the 8 new agents to build FIRST (my vote: Zacchaeus, Rahab, Silas — all three dogfood on businesses you already own or serve).

---

## VERIFICATION NOTE — SEPTEMBER 2026

**Sep 2 roster change:** Caleb becomes Chief Information Security Officer (stays C-suite, `complex`); Nehemiah is added as COO; Ezra reports to Caleb. See `04_ROSTER_CHANGE_CALEB_SECURITY.md`. Baseline becomes 27, so the eight new agents take the roster to 35 (36 with Gabriel).

The 26-agent roster in Part 1 was checked row by row against `foundation.ai_employees` in project `rhtwtoinmiekttvunlzs` and **matches**. Two corrections to the text above:
1. Joanna (finance, `product_name = Lydia`) is already live — the "Lydia collision" item in Part 3 is resolved; the Shopify agent keeps Lydia.
2. Solomon's row is already `orchestrator_max`, but the router did not map that value until Phase 0 — see `03_PHASE0_RESTORE_API.md` §0.4.

Model updates since this doc was written: Fable 5.1 (`claude-fable-5-1`) replaces Fable 5 at the same $10/$50 with cache reads at $0.25 (2.5%); Sonnet 5's $2/$10 is now permanent, so it becomes the `standard` tier. The Option A / Option B recommendation is unchanged.
