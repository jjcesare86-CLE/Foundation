# CURRENT — what's in flight
_Claude Code: read this at session start, update it before session end._

## Now
- **Batch 1 (item B) is fully green — Phases 0-6 done.** See `docs/specs/BATCH1_COMPLETION_REPORT.md` for the full writeup. 30 active agents live in `foundation.ai_employees` (Rahab, Zacchaeus, Silas added). Everything verified against live Supabase this session, including a real two-thread concurrency test on `claim_slot()`.
- All work is on branch `batch1-expansion` (pushed to origin). **Not merged to `main` yet** — that's the one remaining step in Phase 6, holding for an explicit go-ahead before touching production deploy.
- Item A (security foundations) is also on this branch, done in an earlier session, reconciled and verified here.

## Blockers on John
- Merge `batch1-expansion` → `main` and confirm Render deploys green — **waiting on your go-ahead**, not done automatically.
- Set Render env: `MODEL_ORCH_MAX=claude-fable-5-1`, `MODEL_COMPLEX=claude-opus-4-8`, `MODEL_STANDARD=claude-sonnet-5`, `MODEL_COMPLEX_ENTERPRISE=claude-fable-5-1` (code defaults already correct, but the dashboard should say so explicitly).
- Google Maps API key (Distance Matrix + Geocoding) — Silas's route ordering works today via a PostGIS straight-line stand-in, but real drive-time needs this.
- A weather data source for Silas's weather-conflict job, and confirmation of Exterior Rescue's GPS clock-in feed endpoint — both still open, both explicitly flagged rather than faked.
- Confirm Delilah/Leah moving from Caleb to Nehemiah (Phase 0.5 judgment call, see DECISIONS.md 2026-09-05) — not blocking.
- `GHL_API_KEY` was found already set in this environment mid-build — confirmed real and intentional by you. Its scope (which client/location) hasn't been independently verified beyond that.

## Next up
- Your call: merge Batch 1 to main, or hold for review first.
- Item D: Ops Audit Part A (`AGENT_OPS_AUDIT_ELIJAH_V1_1.md`) — requested and queued, explicitly sequenced after B per the build order. Starting now.
- Item C: Connections Hub — unblocks Zacchaeus's real Stripe sync and Silas/Rahab's live GHL messaging. File Google's OAuth verification the day this starts (1-2 weeks, can't be shortened).

## Last verified facts
See `docs/specs/00_STATE_OF_THE_BUILD.md` and `docs/specs/BATCH1_COMPLETION_REPORT.md`. 30 agents live; `/employees/` (not `/agents`, which was removed) is the real roster route and returns 200 with 30 rows in production right now, even before the branch merges, since the roster query itself didn't need code changes to reflect the new DB rows.
