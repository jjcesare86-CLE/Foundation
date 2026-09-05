# CURRENT — what's in flight
_Claude Code: read this at session start, update it before session end._

## Now
- **Batch 1 (item B) is fully green — Phases 0-6 done.** See `docs/specs/BATCH1_COMPLETION_REPORT.md` for the full writeup. 30 active agents live in `foundation.ai_employees` (Rahab, Zacchaeus, Silas added). Everything verified against live Supabase this session, including a real two-thread concurrency test on `claim_slot()`.
- **Item D (Ops Audit Part A) is done too.** `required_capabilities` + `agent_jobs` registry, `ops_audit.py` (L1-L5), `/ops/agent-health` + a simple HTML grid at `/ops/agent-health/dashboard`, 4 existing crons retrofitted to heartbeat, nightly + weekly-smoke audit crons added. Ran the real audit against live data: **0 green, 1 amber (Rahab), 29 red** — full breakdown and John's blocking list in `docs/state/OPS_AUDIT.md`. The single biggest finding: 27 of 30 agents have no `system_prompt` written at all — flagged as its own dedicated work item, not something bundled into this pass.
- All work is on branch `batch1-expansion` (pushed to origin). **Not merged to `main` yet** — holding for an explicit go-ahead before touching production deploy.
- Item A (security foundations) is also on this branch, done in an earlier session, reconciled and verified here.

## Blockers on John
- Merge `batch1-expansion` → `main` and confirm Render deploys green — **waiting on your go-ahead**, not done automatically.
- Set Render env: `MODEL_ORCH_MAX=claude-fable-5-1`, `MODEL_COMPLEX=claude-opus-4-8`, `MODEL_STANDARD=claude-sonnet-5`, `MODEL_COMPLEX_ENTERPRISE=claude-fable-5-1` (code defaults already correct, but the dashboard should say so explicitly).
- Google Maps API key (Distance Matrix + Geocoding) — Silas's route ordering works today via a PostGIS straight-line stand-in, but real drive-time needs this.
- A weather data source for Silas's weather-conflict job, and confirmation of Exterior Rescue's GPS clock-in feed endpoint — both still open, both explicitly flagged rather than faked.
- Confirm Delilah/Leah moving from Caleb to Nehemiah (Phase 0.5 judgment call, see DECISIONS.md 2026-09-05) — not blocking.
- `GHL_API_KEY` was found already set in this environment mid-build — confirmed real and intentional by you. Its scope (which client/location) hasn't been independently verified beyond that.

## Next up
- Your call: merge Batch 1 + Ops Audit to main, or hold for review first.
- The 27-agent system-prompt gap (see OPS_AUDIT.md) — worth deciding whether this becomes its own item before or alongside C.
- Item C: Connections Hub — unblocks Zacchaeus's real Stripe sync, Silas/Rahab's live GHL messaging, and the L3 Stripe/Maps failures in the ops audit. File Google's OAuth verification the day this starts (1-2 weeks, can't be shortened).

## Last verified facts
See `docs/specs/00_STATE_OF_THE_BUILD.md`, `docs/specs/BATCH1_COMPLETION_REPORT.md`, `docs/state/OPS_AUDIT.md`. 30 agents live; `/employees/` (not `/agents`, which was removed) is the real roster route and returns 200 with 30 rows in production right now, even before the branch merges, since the roster query itself didn't need code changes to reflect the new DB rows. Ops audit run for real 2026-09-05: 0 green / 1 amber / 29 red, honest result not a bug.
