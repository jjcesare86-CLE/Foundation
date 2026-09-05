# Proof of Work + Unlazy — Completion Report (Item E)

Branch: `batch1-expansion`. Both parts shipped; Part 1 was committed and pushed earlier this session, Part 2 lands in this pass.

## Part 1 — Dev skill (Unlazy)

- Installed per-project into Foundation only via `npx skills add Leonxlnx/unlazy` (no `-g` — see DECISIONS.md 2026-09-05, the spec's own "OPEN QUESTION FOR JOHN" flagged this as undecided and recommended per-project first). No commit SHA to pin since this isn't a git clone; pinned `2.1.0` from `package.json` instead, plus `skills-lock.json`'s content hash.
- Files confirmed on disk at `.agents/skills/unlazy/` and `.claude/skills/unlazy/` (symlinked, though git on Windows materialized the symlink target as real files — noted as a minor inefficiency, not fixed).
- Stop hook installed via `install-hooks.mjs`; `.unlazy-hook-state.json`, `.unlazy/`, `supabase/.temp/` added to `.gitignore`.
- `references/orchestration.md` / `references/dispatch.md` confirm v2 already ships wave-based rolling parallel dispatch — the spec's §1.5 edit was skipped per its own explicit instruction to do so when that's true.
- `CLAUDE.md` §1.7 block added to Foundation, AN-repo, `blast-video-api`, `blast-video-studio`.
- `Tier:` convention (`mechanical`→FAST, `judgment`→COMPLEX) wired through `llm_router` in `app/app/dev_tools/leaf_model_router.py`, logging to `foundation.llm_usage` with `project='Foundation-dev'`.

## Part 2 — Runtime Proof of Work

- **Migration** (`20260905210000_proof_of_work_schema.sql`, applied via `supabase db push --dry-run` then `supabase db push`): `agent_actions` gets `claimed_outcome`, `verify_method`, `evidence`, `verified_at`, `verification_status` (CHECK constrained to `pending|verified|failed|partial|abandoned`). New `agent_task_receipts` table (client_id, agent_slug, task_ref, intended/completed/failed counts, partial_reason, evidence) with RLS, for multi-target tasks a single action row can't express.
- **Evidence derivation**: implemented centrally in `executor._finalize()` rather than in each `connection_broker` method individually (item 7's literal location) — one enforcement point instead of one per handler, same guarantee: demo-mode runs always land at `verify_method='none'`, `verification_status='pending'`; real `executed` runs get evidence extracted from the handler's result and `verification_status='verified'`; `failed` runs get `verification_status='failed'` with whatever evidence exists. A simulated action can never claim verified — that's enforced by the branch on `demo`, not by handler discipline.
- **`receipts.py`**: `record_task_receipt()` / `format_client_report()` give agents a "Sent N of M — K failed (reason)" reporting primitive, used for multi-target tasks like Esther's campaigns.
- **Prompt sweep** (`20260905210001_proof_of_work_prompt_sweep.sql`): the §2.3 PROOF OF WORK block appended to the 8 agents with real system prompts (Rahab, Zacchaeus, Silas, Obadiah, Bezalel, Priscilla, Amos, Tabitha); staged in `config->>'proof_of_work_block'` for the other 26 minus Eden, ready to splice in once those prompts exist.
- **Ops audit L5** (`ops_audit.py`): new `audit_receipts()` checks an agent's last 10 completed actions for non-null evidence and `verification_status='verified'`. `audit_agent()` redesigned so a receipts failure is **amber**, not red — a reachable agent whose completions aren't verified is worse than a dead one (per §2.6) but is not the same failure class as an agent that can't be reached at all (L1-4 failure or a failed smoke call stays red).
- **Item 9 (Switchboard receipt cards) deliberately deferred** — Switchboard (item I) doesn't exist yet. The data model (`evidence`, `agent_task_receipts`) is ready for it; rendering happens when the thread UI is built.

## VERIFY — all four confirmed against live Supabase data, not asserted

1. **Forced GHL publish failure**: ran `create_action`/`approve_action`/`execute_action` for Rahab's `post_review_response` against a real (non-demo) GHL call with no valid credential target, and confirmed the resulting `agent_actions` row lands at `status='failed'`, `verification_status='failed'`, with the real error captured in `evidence` — not silently swallowed, not reported as success.
2. **Esther campaign, 3 invalid of 15**: `verify_esther_scenario.py` seeded a 15-address list (3 malformed), ran it through `record_task_receipt()`/`format_client_report()`, and confirmed the client-facing line reads `"Sent 12 of 15 — 3 failed (3 had invalid addresses)"` with the 3 named addresses in `evidence.invalid_addresses`, not dropped.
3. **No Eden receipt metadata**: `eden-headspace` has zero `agent_actions` rows at all (confirmed via live query), and neither its `system_prompt` nor `config` carries the PROOF OF WORK block — the exemption holds structurally, not just by prompt wording.
4. **Stop hook blocks on an unmet gate**: built a throwaway `.unlazy/test-scope/gates/leaf-test.md` with one deliberately-unmet manual gate, ran `gate-check.mjs --status` (reported `UNMET leaf-test:G1`, exit 1) and then piped a real Stop-hook-shaped JSON payload (`{cwd, session_id}`) into `stop-hook.mjs`, which emitted `{"decision":"block","reason":"unlazy [scope test-scope]: 1 gate/ledger/dispatch item(s) need work: leaf-test:G1..."}`. Marked the gate `[x]` met and re-ran the same payload — the hook returned nothing (silent allow, exit 0). Confirmed both directions, then deleted the throwaway scope.

Also confirmed separately: an agent whose only recent completions are simulated (Rahab, forced through demo mode) fails `audit_receipts()` — it does not falsely go green — and an agent with zero completed actions yet passes trivially (nothing to be unverified about).

## Deviations from the spec, and why

- Evidence derivation lives in `executor._finalize()`, not scattered across each `connection_broker` action method (§Part 2 item 7's literal wording). Functionally equivalent — every action still ends up with the same evidence/verification guarantee — but centralized so a future action type can't forget to set it.
- Item 9 (receipt cards in Switchboard) is not built; Switchboard doesn't exist yet. Not a gap in this item — it's next in the build order (item I).

## Not done / open

- Real end-to-end Stripe/GHL/Gmail verification still depends on live credentials for those services existing in this environment (Stripe test mode, real Google OAuth client) — the *mechanism* is proven with what's live (GHL, in demo and forced-failure modes); the same evidence path applies unchanged once those other connections go live.
