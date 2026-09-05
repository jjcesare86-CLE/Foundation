# AUTOPILOT NUANCES — FOUNDATION IMPLEMENTATION SPEC
**Source: external video analysis (MCP autopilot pipeline) → adapted for Foundation agents**
v1.0 · July 9, 2026 · Drop into docs/specs/ · Run AFTER Batch 1 Phase 6 is green

---

## VERDICT TABLE — what we adopt, refine, or skip

| Technique from video | Verdict | Why |
|---|---|---|
| A. Non-linear interview loops (one question at a time + pushback on vague answers) | **ADOPT** | Directly fixes our weakest link: intake quality. Bad intake = generic output across every agent. |
| B. Platform tailoring matrix via brand-voice.md | **ADOPT (as data, not files)** | We have `brand_assets` but no enforced per-platform constraint engine. Nathan/Deborah/Esther need this. |
| C. Self-checking connection routines (preflight before expensive generation) | **ADOPT** | We literally just built `connection_broker` + Connections Hub — preflight is the missing top layer. Saves Higgsfield credits and Fable tokens on doomed runs. |
| D. Behavioral sliders (humor/rigor/proactivity dials) | **ADOPT** | Becomes a RESELLABLE feature: "tune your AI employee." Cheap to build on our schema. |
| E. Markdown "second brain" state directory | **REFINE** | We already have the superior version (Supabase as shared state + skills). Adopt only the thin repo-level piece: per-repo `docs/state/` operational files for Claude Code sessions. |
| F. Claude Code scheduled routines | **REFINE** | Our agent scheduling lives in Render crons (correct — server-side, always-on). Adopt only for DEV-OPS on our own repos (nightly repo scout). Verify current Claude Code scheduling/hooks support in docs before building; fall back to cron + headless `claude -p` if needed. |
| G. Blotato MCP publishing hub | **SKIP** | Redundant: Connections Hub v1 rides GHL's approved social apps (locked decision). Blotato = second subscription doing the same job. Park it in the Phase-4 aggregator bake-off next to Ayrshare if a client ever needs platforms GHL lacks. |
| H. 3D semantic map UI | **SKIP (for now)** | Demo candy. Zero operational lift for clients. Revisit only as an AN sales-demo visual. |

---

## MODULE 1 — INTERVIEW ENGINE (technique A)

**What it is:** a reusable intake pattern any agent can invoke: ask ONE question at a time, score each answer for specificity, and push back (once, politely) when an answer is too vague to build on — instead of accepting garbage and generating generic output.

**Where it plugs in (immediate):**
- Pipeline-bridge onboarding (Business Profile step) — replaces the flat form-dump with a conversational intake that produces a far richer profile.
- Social Brand Launcher intake (feeds Module 2's brand voice profile).
- Rahab client setup (comp policy, tone boundaries), Silas setup (weather rules, territories, crew skills), Zacchaeus setup (industry chart of accounts, entity type).

**Build:**
1. New Foundation module `interview_engine.py`:
   - `run_interview(client_id, interview_key)` loads a question set from a new `interview_templates` table (columns: interview_key, question_order, question_text, answer_type, specificity_hint, required BOOLEAN).
   - After each answer, a Haiku call scores specificity 0–1 against the hint
     ("we serve everyone" → 0.2; "roofing + gutter repair for homeowners within
     40 min of Dunkirk, avg ticket $8K" → 0.9).
   - Score < 0.6 → ONE follow-up push: "Help me get specific — [tailored probe]."
     Second vague answer → accept, but mark the field `low_confidence=true` so
     downstream agents know to hedge or re-ask later. Never badger a client twice.
   - Writes results to `client_profiles` JSONB (or the existing business_profiles
     table — introspect live schema and extend rather than duplicate).
2. Delivery channels: dashboard chat UI AND voice (Mia/Celeste via VAPI reading
   the same template — one template, two modalities).

**System-prompt fragment to add to every intake-capable agent:**
```
INTAKE DISCIPLINE: Ask exactly one question at a time. If an answer is vague or
generic, push back once with a specific probe. Never stack questions. Never
accept "everyone/anything/whatever you think" as a final answer on a required
field without one clarifying attempt.
```

---

## MODULE 2 — BRAND VOICE + PLATFORM PLAYBOOK ENGINE (technique B)

**What it is:** per-client brand voice rules and per-platform formatting constraints stored as structured data, injected into every content-producing prompt, and validated on output. Kills the #1 failure mode: identical payload cross-posted everywhere.

**Why data, not .md files:** the video stores brand-voice.md in a repo — fine for one user, wrong for a multi-tenant platform. Ours lives in Supabase so every client has their own, editable from the dashboard, versioned, and injected at runtime.

**Build:**
1. Migration — `brand_voice_profiles`:
```sql
CREATE TABLE brand_voice_profiles (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  client_id UUID NOT NULL REFERENCES clients(id),
  version INT DEFAULT 1,
  is_active BOOLEAN DEFAULT TRUE,
  voice JSONB NOT NULL,          -- tone words, banned words/phrases, reading level,
                                 -- emoji policy, POV (we/I), signature phrases,
                                 -- things we never claim (FTC-safe list)
  created_from TEXT DEFAULT 'interview',   -- interview | brand_scrape | manual
  created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE TABLE platform_playbooks (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  platform TEXT NOT NULL,        -- linkedin | instagram | x | facebook | tiktok | gmb | email | sms
  constraints JSONB NOT NULL,    -- max_chars, structure, hashtag_count, cta_placement,
                                 -- link_policy, hook_style
  is_global BOOLEAN DEFAULT TRUE,
  client_id UUID REFERENCES clients(id)  -- NULL = global default; client row overrides
);
```
2. Seed global playbooks (adapt from the video's matrix, tuned to ours):
   - linkedin: ≤1400 chars, narrative/builder-story structure, end on a business
     lesson, 0–3 hashtags, no link in body (first comment).
   - instagram: carousel-first, exactly 5 relevant hashtags, CTA in caption tail
     + comments, meme-energy allowed IF voice.tone permits.
   - x: ≤280/post, hook-first, value in line one, thread when multi-part,
     no hashtags unless voice says otherwise.
   - facebook: conversational, 1–3 short paragraphs, question CTA.
   - gmb: 750 chars, local keywords, one CTA button reference.
   - email (Esther): subject ≤45 chars, preview-text aware, one CTA per email.
   - sms (Esther/Silas/Rahab): ≤160 chars, first name, one link max, opt-out aware.
3. `prompt_composer.py` addition: any content task auto-prepends
   `[BRAND VOICE vN]` + `[PLATFORM RULES: {platform}]` blocks resolved from these
   tables. Agents affected: Nathan, Deborah, Esther, Anna (ad copy), Rahab
   (review responses — voice only), Gideon (scripts), future Bezalel.
4. **Output validator (cheap + mechanical):** post-generation Haiku pass checks
   char limits, hashtag counts, banned words, link policy. Fail → one automatic
   regeneration with the violation named. Log validator failures to llm_usage
   task_type='playbook_violation' so we can see which agents drift.
5. Populate: the brand-scrape pipeline (once the brand_previews table fix ships)
   and Module 1 interviews both write brand_voice_profiles rows.

---

## MODULE 3 — PREFLIGHT CHECK ROUTINE (technique C)

**What it is:** before any expensive run (Higgsfield render, multi-platform publish, dispatch cycle, Fable 5.1 synthesis), verify every required connection/credential/balance is live. Fail fast, cheap, and loud — never discover a dead token after burning 40K tokens and 200 Higgsfield credits.

**Build:**
1. `connection_broker.preflight(client_id, required: list[str]) -> PreflightReport`
   - Checks each required connection's status in client_connections (+ live token
     verify if last_verified_at > 24h old).
   - Extended checks by key: `higgsfield` → credit balance above task estimate;
     `ghl` → subaccount reachable; `stripe` → account active; `maps` → key valid.
   - Returns pass/fail per item + one human-readable line per failure.
2. Wire into (in order of money saved):
   - **Blast Video pipeline** — before ANY generation chain starts (this alone
     pays for the module; no more burning Kling/Seedance credits into a dead
     webhook).
   - Nathan/Esther publish jobs — before composing, not after.
   - Silas 05:30 dispatch build — GHL + Maps + GPS feed check; failure pages the
     owner BEFORE crews are waiting on run sheets.
   - Solomon `quarterly_synthesis` (orchestrator_max) — verify all data-source
     connections before the 1M-context Fable call.
3. Failure UX: agent messages the client in plain English with the Connections
   Hub deep link ("Your Facebook connection expired — one tap to fix:
   {url}/dashboard/connections"). Log preflight failures to a `preflight_events`
   table for the nightly health cron to trend.

---

## MODULE 4 — BEHAVIORAL SLIDERS (technique D)

**What it is:** per-agent, per-client operational parameters as data — not prompt rewrites. And it's a sellable differentiator: clients tune THEIR Nathan.

**Build:**
1. Migration: add `operational_params JSONB` to foundation.ai_employees defaults
   AND a `client_agent_params` override table (client_id, agent_slug, params
   JSONB) — client row wins over agent default.
2. Standard schema (0–100 ints):
```json
{
  "rigor": 90,        // pushback on unverified data / vague asks
  "conciseness": 80,  // brevity preference
  "proactivity": 60,  // suggest adjacent work unprompted
  "formality": 70,    // professional ↔ casual
  "humor": 20         // capped at 40 for Rahab public replies, Joanna, Zacchaeus,
                      // Peter, Abigail regardless of client setting (guardrail)
}
```
3. `prompt_composer.py` renders these as an `## Operational Parameters` block with
   one behavioral sentence per dial (numbers alone don't steer models reliably —
   pair each with its meaning, e.g. "humor: 20 — at most a light touch, never in
   sensitive contexts").
4. Dashboard UI: five sliders per agent on the client's agent-settings page.
   Store every change with timestamp (auditability: "why did Nathan get sassy in
   May" is answerable).
5. Hard floors regardless of sliders: FTC rules (Rahab), CPA-review footer
   (Zacchaeus), safety weather rules (Silas), Eden privacy isolation. Sliders
   tune STYLE, never guardrails — enforce in composer, not in trust.

---

## MODULE 5 — REPO STATE DIRECTORY (technique E, thin version)

Supabase remains the agents' shared brain (correct architecture — multi-tenant,
queryable, RLS'd). Adopt only the dev-side piece: each product repo gets
`docs/state/` with three living files Claude Code reads at session start and
updates at session end:
- `CURRENT.md` — what's in flight, blockers, next actions (kills the
  "re-explain the project every session" tax)
- `DECISIONS.md` — append-only log of locked decisions with dates
  (e.g., "2026-07-09: Joanna replaces Lydia #17; Shopify keeps Lydia")
- `COSTS.md` — running notable-spend notes (Higgsfield credits, API tiers)
Add to each repo's CLAUDE.md: "Read docs/state/CURRENT.md and DECISIONS.md before
any work. Update CURRENT.md before ending the session."

---

## MODULE 6 — DEV-OPS ROUTINE: nightly-repo-scout (technique F, scoped)

Client-agent scheduling STAYS in Render crons. This module is for OUR repos only.
1. First, check current Claude Code docs for native scheduled-task/hooks support
   and use it if present; otherwise implement as a local cron/Task Scheduler job
   running headless Claude Code (`claude -p`) with a fixed playbook file.
2. Playbook `routines/nightly-scout.md` (per priority repo — Foundation,
   an-sales-pipeline, blast-video):
   - pull latest; scan for: failing tests, dependency vulnerabilities, TODO/FIXME
     added this week, dead env-var references, migration drift
     (supabase db diff).
   - Write findings to docs/state/SCOUT_REPORT.md + open a draft PR ONLY for
     zero-risk fixes (lint, dep patch bumps). Anything behavioral = report only,
     never auto-merge. Human (John) merges.
3. Start with Foundation only; expand after a week of clean reports.

---

## ROLLOUT ORDER & CLAUDE CODE PROMPT

Order (each gated like Batch 1): Module 3 preflight (saves money from day one,
tiny build) → Module 2 voice/playbook engine (unblocks quality across 6 agents)
→ Module 1 interview engine (feeds Module 2 with better data) → Module 4 sliders
(fast, sellable) → Module 5 state dirs (an afternoon) → Module 6 scout (last).

Paste into Claude Code (Foundation repo, after Batch 1 completion):
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
