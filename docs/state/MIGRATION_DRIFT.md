# MIGRATION DRIFT — RESOLVED 2026-09-05

This is ground truth, not inference — the three "drifted" migrations were written by an earlier session working from a different local clone (`C:\Users\jjces\OneDrive\Desktop\Claude Foundation`) that never got pushed to `origin`, which is why `supabase migration list` showed them applied remotely with no local file. That session's actual `.sql` files were recovered and committed here rather than reconstructed from schema introspection, so this is exact, not a guess.

## The three originally-drifted migrations

- **`20260818193841_create_llm_usage`** — creates `foundation.llm_usage` (project, agent_name, model, tier, input_tokens, output_tokens, cache_read_input_tokens, cache_creation_input_tokens, estimated_cost_usd, task_type, fallback_from, created_at). Service-role-only RLS. This is the table `llm_router.py`'s `_log_usage()` actually writes to.
- **`20260818193842_update_csuite_model_tiers`** — `UPDATE foundation.ai_employees SET model_tier = 'orchestrator_max' WHERE id = 'solomon-ceo'` and `SET model_tier = 'complex' WHERE id IN ('caleb-coo','miriam-cfo','isaiah-cso','abigail-clo')`. Splits the old single `'orchestrator'` value into the two tiers the router now understands.
- **`20260818195000_joanna_rename`** — renames Foundation #17 from `lydia-finance` to `joanna-finance` (id, name, biblical_name), adds `legacy_slug` column, repoints the `employee_platform_subscriptions` FK to `ON UPDATE CASCADE` first so the rename cascades cleanly, sweeps `fin`/`miriam-cfo`'s `outside_scope` text and handoff/coverage arrays.

`supabase migration list` now shows all three (plus two from today — `20260905120000_caleb_ciso_nehemiah_coo`, `20260905130000_caleb_legacy_slug`) with Local and Remote in agreement. No `migration repair` was needed — repair is for when the two disagree; here the remote history already had them recorded correctly (from the original `supabase db push`), the local repo just didn't have the files until they were recovered and committed.

**The RUNBOOK's own guess about what these three created — "industries, industry_playbooks, and the LLM cost tables (llm_usage, llm_cost_daily, llm_cost_monthly, llm_model_distribution) — all present in Foundation's public schema" — is wrong on every count**, now that it can be checked against fact instead of guessed:
- These three migrations created *zero* tables in the `public` schema. `llm_usage` is in `foundation`, not `public`.
- `llm_cost_daily`, `llm_cost_monthly`, `llm_model_distribution` do not exist anywhere in this database. Never did.
- `industries` and `industry_playbooks` do exist (see below) but not from these migrations.

## A second, separate drift, found while checking the first: `public` schema has six tables with no migration history at all

Live introspection (`docs/state/LIVE_SCHEMA_2026-09.md`) found these in `public`, none of them referenced anywhere in `supabase_migrations.schema_migrations`:

| Table | Rows | Notes |
|---|---|---|
| `public.industries` | 0 | Empty scaffold. Matches the Specialization Engine spec's expected shape but has no data yet. |
| `public.industry_playbooks` | 0 | Same. |
| `public.llm_usage` | 0 | **A second, unused `llm_usage` table, distinct from `foundation.llm_usage`.** Nothing in this codebase writes to it — `llm_router.py` targets `foundation.llm_usage` exclusively. Dead weight, not active drift, but worth deleting or renaming before it confuses a future session into thinking there are two cost-logging paths. Not touched here — deletion wasn't asked for and it's harmless as-is. |
| `public.pricing_config`, `public.pricing_outcomes`, `public.pricing_quotes`, `public.transfer_logs` | not checked | Matches `00_STATE_OF_THE_BUILD.md` §8's note that these exist in **both** Foundation and AN databases — a known, already-flagged two-sources-of-truth cleanup item in `02_BUILD_ORDER.md`, not new. |

None of these six tables were created by any CLI-tracked migration in this project's history — they predate migration tracking here entirely, most likely created directly via the Supabase dashboard SQL editor at some earlier point (the same way `industries`/`industry_playbooks` are described as "already exist" in `00_STATE_OF_THE_BUILD.md` §8 and `02_BUILD_ORDER.md`'s item J). Exact provenance beyond that isn't recoverable from the schema alone — flagging as unknown rather than guessing further.

None of this blocks anything: `industries`/`industry_playbooks` are exactly what item J (Specialization Engine) is supposed to extend, per the build order's own instruction to read their live columns first. The stray `public.llm_usage` is inert. Nothing here needed a migration to fix — it's a documentation gap, not a schema problem.
