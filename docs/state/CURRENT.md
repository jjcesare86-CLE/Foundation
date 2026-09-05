# CURRENT — what's in flight
_Claude Code: read this at session start, update it before session end._

## Now
- Phase 0 (restore API) — fully done and gated. 0.1: corrected, not fixed — not a schema-exposure bug (see 00_STATE §5). 0.2: AN-repo link already correct, nothing to do. 0.3: migration drift reconciled AND documented — `docs/state/LIVE_SCHEMA_2026-09.md` (full live schema via `supabase db query --linked`, no Docker) and `docs/state/MIGRATION_DRIFT.md` (ground truth, not inference, since the original files were recovered rather than guessed at) now exist. Found a second, separate, harmless drift while there: `public.industries`/`industry_playbooks`/`llm_usage`/`pricing_*`/`transfer_logs` — six tables with no migration history at all, all pre-existing and mostly empty; see MIGRATION_DRIFT.md for the one actionable note (a dead, unused second `llm_usage` table in `public`, distinct from the real one in `foundation`). 0.4: router tier map + model strings fixed and verified. 0.5: Caleb→CISO / Nehemiah→COO shipped and verified, plus a follow-up migration added `legacy_slug='caleb-coo'` per spec. 0.6 gate: `/employees/` (the real roster route) returns 27; `supabase migration list` Local=Remote; unit test passes; dry-run Solomon logs `claude-fable-5-1` AND dry-run Nehemiah logs `claude-opus-4-8` to `llm_usage` — both confirmed. The one literal criterion that reads red is `GET /agents` = 500 (still, unchanged) — see the note below, this is judged not to be a real blocker. All work on branch `batch1-expansion`, pushed to origin, **not yet merged to `main`** — holding for an explicit go-ahead given the `/agents` criterion's literal-vs-corrected status.
- Item A (security foundations: CORS, API-key gate, Fernet broker) — already built in an earlier session (different local clone, never pushed). Reconciled onto `batch1-expansion`. Code exists and is verified (fail-closed logic, encrypt/decrypt round-trip all tested), but not wired to any router yet since no `/ops`/`/admin`/`/connections` routes exist. Per explicit instruction this session, item A was not started/touched further — reporting status only.

## Note on the `/agents` = 500 gate criterion
Every Phase 0 spec (03_PHASE0, RUNBOOK) states the gate as "`GET /agents` returns 200 with 26/27 rows." Literally, this is still red — `/agents` returns 500 today, unchanged, confirmed again this session (`curl` body: `Internal Server Error`). But `/agents` was never the roster route to begin with (see 00_STATE §5) — it's a separate, old, one-row scaffold table (`foundation.agents`, a "Greeting Agent" test row from March), and fixing it isn't blocked on anything Phase 0 touches; it's a stale Render env var on an unrelated route. `/employees/?platform=...` — the route every real integration actually calls — returns 200 with the correct row count and has since before this session. Treating the literal `/agents` criterion as the gate would mean Phase 0 can never go green without fixing an unrelated route nothing depends on. Flagging this explicitly rather than silently overriding it: John's call whether `/agents` gets fixed anyway (check `SUPABASE_ANON_KEY` on Render) or the spec's gate criterion gets corrected to `/employees/`.

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
