# CURRENT — what's in flight
_Claude Code: read this at session start, update it before session end._

## Now
- Phase 0 (restore API) — DONE except 0.1 (see below, and it turned out not to be the real bug). 0.2 checked clean. 0.3 migration drift reconciled (no repair needed — the CLI already had them recorded remotely, just needed the local files, now committed). 0.4 router tier map + model strings fixed and verified. 0.5 Caleb→CISO / Nehemiah→COO shipped and verified. 0.6 gate: 3 of 4 true (`/employees/` — the real roster route — returns 27; migration list agrees; unit test + dry-run pass). AN-repo link was already correct. All work is on branch `batch1-expansion` (pushed to origin, not yet merged to `main`).
- Item A (security foundations: CORS, API-key gate, Fernet broker) — turns out this was already built in an earlier session (different local clone, never pushed). Reconciled onto `batch1-expansion` today. Code exists and is verified (fail-closed logic, encrypt/decrypt round-trip all tested), but not wired to any router yet since no `/ops`/`/admin`/`/connections` routes exist — that wiring happens naturally when items B and C build those routes.

## Blockers on John
- ~~Tick `foundation` in Exposed Schemas~~ — not the bug, don't do this (see 00_STATE §5). If you want `/agents` (the old scaffold route, NOT the roster) fixed anyway, check `SUPABASE_ANON_KEY` on Render matches the Foundation project's anon key.
- Set Render env: `MODEL_ORCH_MAX=claude-fable-5-1`, `MODEL_COMPLEX=claude-opus-4-8`, `MODEL_STANDARD=claude-sonnet-5`, `MODEL_COMPLEX_ENTERPRISE=claude-fable-5-1` (staged, unused).
- Confirm Delilah/Leah moving from Caleb to Nehemiah (see DECISIONS.md 2026-09-05) — not blocking, just wasn't explicit in the 0.5 spec.
- Merge `batch1-expansion` → `main` when ready (not done yet — holding for review).
- Google Maps API key (needed at Batch 1 Phase 4 / Silas) — still open.

## Next up
- Land `batch1-expansion` → `main`, confirm Render deploys it.
- Item B: `CLAUDE_CODE_MASTER_PROMPT_BATCH1.md` — Rahab first (creates the typed action library), then Zacchaeus, then Silas.

## Last verified facts
See docs/specs/00_STATE_OF_THE_BUILD.md — 27 agents live in foundation.ai_employees (Nehemiah added, Caleb is CISO); Joanna rename done; router tier map fixed and verified against every live model_tier value; `/employees/` (not `/agents`) is the real roster route and returns 200 live.
