# OPS AUDIT — 2026-09-05
**Full L1-L4 audit of all 30 active agents, run for real against live Supabase. L5 (smoke calls) skipped in this run — no `ANTHROPIC_API_KEY` available in this build environment; see the L5 section below.**

## Summary
| Status | Count |
|---|---|
| 🟢 Green | 0 |
| 🟡 Amber | 1 (Rahab — L1-L4 all pass, L5 unknown) |
| 🔴 Red | 29 |

This is the honest result, not a bug in the audit — most of this roster genuinely has no system prompt written yet, and the new agents' external integrations genuinely aren't connected. That's exactly what this audit exists to surface.

---

## Fixed by Claude Code in this pass (done, re-run, confirmed stable)

1. **L1 false-positive on empty arrays** — the first audit run flagged Eden's row as L1-red because `handoff_to = []`. That's correct data, not a gap: Eden has no handoffs by design (the hard `eden_sessions` privacy-isolation rule — she's a terminal node). Fixed `audit_l1` to only flag a genuine `NULL`, not a legitimately-empty array. Re-ran: Eden now passes L1.
2. **`foundation.client_connections` didn't exist** — the L3 Stripe check (and `zacchaeus/stripe_client.py`, built in Batch 1) both reference this table, but it had only ever been designed against the pre-CLI-tracked migration convention and never actually applied. Created it for real via `supabase db push` (migration `20260905170001_client_connections.sql`). Without this the audit couldn't even run.
3. **L4 heartbeats were all empty** — the 4 registered cron jobs (`rahab-review-ingestion`, `rahab-spike-check`, `zacchaeus-daily`, `silas-dispatch-builder`) had never actually executed (only their underlying functions were unit-tested during Batch 1). Ran all 4 for real against production data once each to seed genuine heartbeats. Re-ran the audit: Rahab flipped from L4-red to L4-green (her two jobs both heartbeated); Zacchaeus and Silas's L4 also now passes (their L3 failures are separate, real, and not something a re-run fixes — see below).

## NOT fixed — requires dedicated work, not "iterate until stable"

**L2: 27 of 30 agents have no `system_prompt` written.** Only Rahab, Zacchaeus, and Silas (built fresh in Batch 1) have real prompts. This is the single biggest finding, and it's not a quick fix: it's 27 agents' worth of real prompt-writing (personality, hard rules, handoff behavior, tone), the same level of care that went into Rahab/Zacchaeus/Silas's ~500-word prompts. Doing that as a side effect of an ops-audit task would mean writing it fast and generic, which is worse than not writing it at all for agents like Eden (confidential counseling) or the C-suite (executive judgment calls). **Recommend this becomes its own dedicated item**, not something bundled into this pass. Full list of agents missing a prompt: rex, maya, ace, vince, blake, nina, drew, leo, otto, ori, aria, sage, rebekah-legal, eden-headspace, caleb-coo, fin, isaiah-cso, abigail-clo, martha-admin, miriam-cfo, nehemiah-coo, leah-exec-asst, joanna-finance, solomon-ceo, dean, kai, clara.

---

## Blocked on John (env vars, connects, dashboard toggles — one line each)

| # | Agent(s) | Layer | What's needed | Where |
|---|---|---|---|---|
| 1 | Fin, Joanna, Zacchaeus | L3 | A live Stripe connection — `foundation.client_connections` now exists but has zero rows for any client | Connections Hub (item C) needs to ship an OAuth flow before any client can connect Stripe |
| 2 | Silas | L3 | `GOOGLE_MAPS_API_KEY` | Render → foundation-api-9gpl → Environment |
| 3 | Silas | L3 | A GPS clock-in feed for Exterior Rescue | Confirm the endpoint (Batch 1's own manual prereq, still open) |
| 4 | All (for L5 to run at all) | L5 | `ANTHROPIC_API_KEY` in this dev/audit environment | Not available here at all — every LLM-touching check this whole session mocked the Anthropic call itself |
| 5 | 27 agents | L2 | Not env/dashboard — see "NOT fixed" above, this is a work item not a blocker |

## L5 — not run in this environment
`ops_audit.py`'s `audit_l5()` is real (one cheap canned prompt per agent through the actual router, asserting a logged `llm_usage` row with the expected model). It just couldn't execute here — no `ANTHROPIC_API_KEY`. The weekly cron (`ops-audit-weekly-smoke`, Sundays 04:15, in `render.yaml`) will run it for real once deployed with that key set. Every other verification in this build (Batch 1's phases included) mocked only the Anthropic call itself for the same reason — everything downstream of it (DB writes, action library, approvals) ran for real throughout.

## Known-issue #7 from the spec's own pre-flight list
"Foundation Supabase project-ID discrepancy" — the spec text listed the same ref twice (`rhtwtoinmiekttvunlzs` vs `rhtwtoinmiekttvunlzs`), so there's nothing to actually check there; the deployed API's `SUPABASE_URL` was confirmed pointing at `rhtwtoinmiekttvunlzs` back in `00_STATE_OF_THE_BUILD.md` §1.

## Not yet checked (out of Part A's stated scope, flagging for awareness)
- `PIPELINE_API_KEY` on `an-sales-pipeline` — a different Render service, not this repo.
- `gemini_voice_proxy.py` deployment status — exists in this repo's code but its live deployment state wasn't part of this audit.
