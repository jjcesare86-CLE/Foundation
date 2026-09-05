# UNLAZY ADOPTION + FOUNDATION PROOF-OF-WORK STANDARD
**v1.0 · Two separate implementations from one principle**
Drop into docs/specs/ · Source: github.com/Leonxlnx/unlazy (v2, verified Aug 22 2026)

---

## 0. THE DISTINCTION THAT DRIVES THIS DOC

| | Unlazy (dev-time) | Proof-of-Work (runtime) |
|---|---|---|
| Who it governs | Claude Code / Codex building our software | The 34 Foundation AI employees serving clients |
| What it prevents | "Built the feature" when 3 of 5 parts are stubs | "Posted your reviews" when nothing was published |
| Mechanism | Gates files, CHECK commands, Stop hook, subagent trees | Evidence-required completion claims, action-library receipts |
| Where it lives | `~/.claude/skills/unlazy` + repo `PLAN.md`/`gates/` | Agent system prompts + `agent_actions` schema |

Both answer the same question: *how do you know it's actually done?* Never take the agent's word for it. Same philosophy, two entirely different builds. Do NOT paste `tree 5` into Nathan's system prompt — that is a category error.

---

# PART 1 — UNLAZY AS OUR DEV STANDARD

## 1.1 What it actually is (verified, not from the video)
Before work starts, the agent writes acceptance gates to a file. Each gate is a checkbox with an outcome, a `CHECK:` command that proves it, an `EXPECT:` string that command must return, and an `EVIDENCE:` line that starts as `pending`. A script runs the CHECK commands and only ticks boxes when EXPECT matches, replacing `pending` with the deciding output. **A ticked box still reading `pending` counts as unmet** — that's the agent grading itself, which is the exact failure being fixed.

Five enforcement layers, weakest to strongest: SKILL.md discipline → gates files → runnable CHECK scripts → parent re-verification of each leaf → the Stop hook, which mechanically blocks Claude Code from ending its turn while gates are unmet.

## 1.2 Install (correct commands — the video was vague here)
```powershell
# Recommended — detects your agents, installs to the right paths
npx skills add Leonxlnx/unlazy

# Add -g for user-level (all projects), --all for every detected agent
npx skills add Leonxlnx/unlazy -g

# Manual for Claude Code:
git clone https://github.com/Leonxlnx/unlazy $HOME/.claude/skills/unlazy
```
**Hard mode (Claude Code only, optional but recommended for our big builds):**
```powershell
node <path-to-skill>/scripts/install-hooks.mjs            # this project only
node <path-to-skill>/scripts/install-hooks.mjs --global    # every project
```
The hook costs zero tokens (file scan). Add `.unlazy-hook-state.json` to `.gitignore`. If the agent makes no gate progress across six blocked stops, the hook releases it with a warning rather than trapping it, and an explicit `ABANDON: <gate> <reason>` line is always honored as an honest exit.

**Pin the version.** This repo is new (12 stars, 9 commits) and actively changing. Clone, then pin to a commit SHA in `docs/state/DECISIONS.md` so a mid-build upstream change can't shift our process under us. Treat it as a useful pattern we've adopted, not vendor infrastructure.

## 1.3 Honest cautions the video skipped
1. **Depth does not multiply effort the way the tagline claims.** The repo's own controlled test found `tree 6` cost roughly 1.0–1.5x `tree 3`, not the 8x the original arithmetic promised. Depth is decomposition, not effort multiplication. Pick depth by task shape, not by hoping for more effort.
2. **Orchestrated mode multiplies cost with leaf count, deliberately.** The repo's own guidance: below roughly half an hour of work, stay solo. This matters enormously for us — 10 parallel agents on Fable 5.1 ($10/$50 per MTok) is a real bill.
3. **Solo vs orchestrated:** `tree 2-3` for a feature or bug hunt, `tree 4-5` for a subsystem, `tree 6-7` only for a whole project built leaf by leaf.
4. **The video's 3–4-hour/login-page run** was the sequential dispatch problem — fixed by the parallel edit in 1.5. Their fixed run: ~2 hours, 10 agents, full app.
5. The measured benefit that *did* hold: 1.6–3.9x effort increase and 4–10 self-found defects fixed pre-delivery, plus the report-audit rule (re-measure every number at report time) which fixed "confidently wrong numbers in final summaries."

## 1.4 Our depth policy for Foundation work
| Task | Mode | Depth |
|---|---|---|
| Single agent build (one Batch 1 sprint) | solo | `tree 3` |
| A full Batch (3 agents + shared infra) | orchestrated | `tree 4` |
| Switchboard (widget + backend + 5 phases) | orchestrated | `tree 5` |
| Specialization engine + 700-playbook generation | orchestrated | `tree 4` (generation itself is a batch job, not a tree) |
| Bug fix / CORS patch / env wiring | solo | `tree 2` or no skill at all |
| Ops audit remediation | solo | `tree 3` |

**Rule: never invoke Unlazy on work under ~30 minutes.** The overhead is real and our own efficiency skill governs here — the cheapest thing that reliably clears the bar wins.

## 1.5 The parallel-dispatch edit (from the video, transcribed from John's screenshot)
Their skill edit prompt, for reference if we hit the same sequential bottleneck on v2:
```
Speed up orchestrated mode in the unlazy skill. Read SKILL.md, references/*.md,
templates/PLAN.md first.

orchestration.md:15 dispatches one leaf at a time and verifies in lockstep, though
leaves already own disjoint files. Bare gate-check globs all gates/*.md, so every
verify re-runs the whole tree.

1. gate-check.mjs is already rewritten (--jobs, shared CHECK commands, `Jobs: 1`)
   but untested — test on a fixture, fix what breaks.
2. Driver loop → rolling dispatch: launch all ready leaves at once, verify each on
   return, dispatch what it unblocks.
3. PLAN.md: Owns/Needs/Tier per leaf + dispatch schedule.
4. gates.md: leaf gates cover only that leaf; whole-project checks move to branch
   gates, run once.
5. Hand the tiering prose off to model-router.

Keep the gate format, exit codes, stop-hook compat, zero deps, existing voice.
Route your own work via model-router — expect its bail-out to say do the prose
inline; don't fan out five agents for five edits.
```
**Check first whether v2 already ships rolling dispatch** — the repo now documents `--jobs` on `gate-check.mjs` and PLAN.md file-ownership contracts fixed before fan-out, which is most of what this edit adds. Run one orchestrated build unmodified before editing anything. If leaves still dispatch in lockstep, apply the edit; if not, skip it entirely.

## 1.6 Pairing with our llm_router (the real win)
The video's closing tip — pair Unlazy with a model-router so cheap mechanical leaves go to a cheap model — is something **we already own**. Wire it:
- Add a `Tier:` field per leaf in `PLAN.md` (the edit above does this): `fast` | `standard` | `complex`.
- Leaf subagents inherit the tier: boilerplate/migrations/tests → Haiku or Sonnet; architecture, security-sensitive, or ambiguous leaves → Opus 4.8; only genuine whole-system synthesis → Fable 5.
- Log dev-time spend to `llm_usage` with `project='Foundation-dev'` so build cost is visible separately from client runtime cost.

## 1.7 Where to apply it
All future builds in: Foundation, an-sales-pipeline, blast-video, jubilant-api, and every client repo (Exterior Rescue, Broker Broker, LUTS, Delivered Fireworks). Add to each repo's `CLAUDE.md`:
```
For any build task over ~30 minutes, invoke the unlazy skill with an
appropriate tree depth (see docs/specs/UNLAZY_AND_PROOF_OF_WORK.md §1.4).
Gates must be written before work begins. Never report a phase complete
without its gates file showing N of N checked with real evidence lines.
```
This composes cleanly with our existing Batch 1 GLOBAL RULES — the phase VERIFY steps we already wrote *are* gates; Unlazy just makes them structural instead of prose.

---

# PART 2 — FOUNDATION PROOF-OF-WORK STANDARD (runtime, all 34 agents)

## 2.1 The principle, translated
Unlazy's insight: *a claim is not proof, and the claimant cannot be the judge.* Our client-facing agents have exactly this failure mode, and it's worse than in code because the client can't inspect it:
- Rahab says "responded to your reviews" — did GHL actually publish, or did the call 500?
- Silas says "crews dispatched" — did the SMS send, or did the GHL rate limit eat it?
- Esther says "campaign sent" — to 400 contacts, or to the 12 that had valid emails?
- Zacchaeus says "books categorized" — all 340 transactions, or the 200 that were easy?

**Standard: no Foundation agent may report a task complete without a machine-verifiable receipt.**

## 2.2 Schema — the receipt layer
```sql
-- Extend the existing action library (built in Batch 1 Phase 2) rather than duplicating
ALTER TABLE agent_actions ADD COLUMN IF NOT EXISTS claimed_outcome TEXT;
ALTER TABLE agent_actions ADD COLUMN IF NOT EXISTS verify_method TEXT;   -- api_response | db_read | webhook | none
ALTER TABLE agent_actions ADD COLUMN IF NOT EXISTS evidence JSONB;       -- external ids, status codes, counts
ALTER TABLE agent_actions ADD COLUMN IF NOT EXISTS verified_at TIMESTAMPTZ;
ALTER TABLE agent_actions ADD COLUMN IF NOT EXISTS verification_status TEXT DEFAULT 'pending';
  -- pending | verified | failed | partial | abandoned

CREATE TABLE agent_task_receipts (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  client_id UUID NOT NULL REFERENCES clients(id),
  agent_slug TEXT NOT NULL,
  task_ref TEXT NOT NULL,              -- job/campaign/dispatch identifier
  intended_count INT,                  -- what the agent set out to do
  completed_count INT,                 -- what actually verified
  failed_count INT DEFAULT 0,
  partial_reason TEXT,                 -- why the gap exists, in plain English
  evidence JSONB,                      -- per-item receipts (ids, statuses)
  reported_to_client BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
-- RLS: client isolation.
```
`connection_broker` already sits between every agent and every external call — so it is the natural place to capture receipts. Every broker method returns a receipt; the agent cannot bypass it because it has no direct token access. **The broker is our Stop hook.**

## 2.3 System-prompt block — append to ALL 34 agents
```
PROOF OF WORK (non-negotiable):
1. You never report a task complete based on your own belief that you did it.
   Completion is a receipt: an external id, a status code, a row count, or a
   confirmed webhook. No receipt means not done.
2. Report exact numbers, always as completed-of-intended. "Sent 387 of 400 —
   13 had invalid addresses" is a good report. "Campaign sent!" is a bad one.
3. Partial completion is reported as partial, immediately, with the reason and
   what you need to finish. Never round a partial up to a success.
4. If a task turns out to be impossible, say so explicitly and name what
   blocked it. An honest abandon beats a quiet drop every time.
5. Re-measure every number at report time. Do not carry a count from earlier
   in the task into your summary — read it fresh.
6. If a required connection is missing or a call failed, name the service and
   give the Connections Hub link. Never silently skip and report success.
```
Rule 5 is directly lifted from Unlazy's report-audit finding: in their controlled test, *every* skill run's final report contained 1–3 wrong numbers. Agents summarizing their own work drift on figures. Re-reading before reporting fixes it.

## 2.4 Per-agent verification methods
| Agent | Claim | Receipt required |
|---|---|---|
| Rahab | Review response posted | GHL publish response + review id + status |
| Nathan | Post published | Platform post id + permalink |
| Esther | Campaign sent | Per-recipient delivery counts from GHL, not the send-call ack |
| Silas | Crews dispatched | Per-crew SMS delivery receipts + run-sheet ids |
| Zacchaeus | Books categorized | Row counts: categorized / clarification-queued / total |
| Joanna | Invoice sent | Stripe invoice id + status |
| Elijah | Scoreboard delivered | mkt_insights rows written + digest delivery id |
| Anna | Budget shifted | Platform API confirmation + owner approval id |
| Naomi | Appointment booked | Calendar event id |
| Bezalel (future) | Asset generated | Storage URL + render job id |
| C-suite / advisory agents | Analysis delivered | N/A — advice isn't an external action; Rule 5 (fresh numbers) still applies |

Advisory agents (Solomon, Caleb, Miriam, Isaiah, Abigail, Peter, Rebekah, Priscilla, Eden, Leah) have no external side effects, so they carry the prompt block for numerical honesty only. **Eden is explicitly exempt from all receipt logging** — her sessions stay isolated; no verification metadata leaves her boundary.

## 2.5 Client-visible payoff
This isn't just internal hygiene — it's the thing that makes Switchboard trustworthy. In the Switchboard thread, a completed task renders as a receipt card: "Responded to 4 reviews · view them" with real links. In Elijah's scoreboard, every number already carries a confidence level; now it also carries provenance. **The pitch: "Other AI tools tell you they did it. Ours shows you the receipt."** That line sells, and unlike most marketing claims it's structurally true because the broker enforces it.

## 2.6 Ops-audit integration
Layer L5 of the agent health audit already smoke-tests each agent. Extend it: L5 now also asserts the agent's last 10 completed actions have non-null `evidence` and `verification_status='verified'`. An agent producing unverified completions goes **amber** on the health board even if it responds normally — because a chatty agent that silently fails its side effects is worse than a dead one.

---

# PART 3 — CLAUDE CODE PROMPT

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
```

---

## OPEN QUESTION FOR JOHN
Do you want the Unlazy **Stop hook installed globally** (`--global`, every project on your machine) or **per-project** (Foundation first, expand once you've felt it)? Global is stronger enforcement but it will also block quick one-off sessions in unrelated repos until gates are satisfied, which gets annoying on small edits. Recommend per-project on Foundation for two weeks, then decide.
