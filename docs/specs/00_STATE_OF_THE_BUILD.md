# STATE OF THE BUILD — VERIFIED FACTS
**What is actually true about Foundation as of September 2, 2026. Read before any session.**

This document exists because the previous session found several places where the plans and reality disagreed. Every line below was checked against the live system, not recalled from memory. When a spec in this folder contradicts this document, this document wins.

---

## 1. WHERE THINGS LIVE

| Thing | Location | Verified how |
|---|---|---|
| Foundation repo (local) | `C:\Users\jjces\OneDrive\Desktop\Foundation` | `git log` shows `d3556cd refactor: remove all tier logic from Foundation — catalog only` |
| Foundation repo (remote) | `jjcesare86-CLE/Foundation`, branch `main` | same |
| Foundation Supabase project | `rhtwtoinmiekttvunlzs` (named "Foundation") | `supabase projects list` |
| Foundation API | `https://foundation-api-9gpl.onrender.com` | Render; `SUPABASE_URL` env var confirmed pointing at `rhtwtoinmiekttvunlzs` |
| **NOT** Foundation | `C:\Users\jjces\OneDrive\Desktop\AN-repo` = Automation Nation; `Foundation_Scaffold` = empty, not a git repo | both checked |
| **NOT** Foundation DB | `rzsryxvlaezfvftqpvbx` = Automation Nation's database | `supabase projects list` |

**Two local folders start with "Foundation."** `Foundation` is the repo. `Foundation_Scaffold` is dead weight and should be renamed (`ZZ_old_scaffold`) so tab-completion stops landing on it.

## 2. THE AGENT CATALOG IS REAL AND IN THE RIGHT PLACE

`foundation.ai_employees` (schema `foundation`, **not** `public`) holds the operational roster: **27 active agents**, verified row by row (was 26; Phase 0.5 landed 2026-09-05, see below).

| Dept slug | Agents | model_tier |
|---|---|---|
| `csuite` | Solomon (CEO), Nehemiah (COO — new, `nehemiah-coo`), Caleb (CISO — was COO, id unchanged `caleb-coo`), Miriam (CFO), Isaiah (CSO), Abigail (CLO) | Solomon `orchestrator_max`; others `complex` |
| `sales` | John, Luke, Mary, Paul | `standard` |
| `marketing` | Anna, Deborah, Esther, Gideon, Nathan | `standard` |
| `operations` | Ezra (`vince`, reports to Caleb — unchanged), Joseph (`otto`, reports to Nehemiah now), Martha (`martha-admin`, reports to Nehemiah now), Naomi (`sage`, reports to Joseph — unchanged) | Martha + Naomi `fast`; others `standard` |
| `finance` | Hannah, Joanna | `standard` |
| `hr` | Delilah (`ori`, reports to Nehemiah now), Eden, Leah (`leah-exec-asst`, reports to Nehemiah now) | `standard` |
| `legal` | Peter, Rebekah | `standard` |
| `strategy` | Elijah | `standard` |

**Phase 0.5 is DONE** (2026-09-05, migration `20260905120000_caleb_ciso_nehemiah_coo.sql`, branch `batch1-expansion`): Caleb → CISO (id kept as `caleb-coo` — a PK rename was judged riskier than the mismatch between id and role, same call as Joanna's product_name pattern), Nehemiah inserted as COO (`nehemiah-coo`). Ezra stays reporting to Caleb per spec. The other four of Caleb's old direct reports (Joseph/otto, Delilah/ori, Leah/leah-exec-asst, Martha/martha-admin) were moved to report to Nehemiah — the spec named Joseph/Naomi/Martha explicitly but was silent on Delilah and Leah; both were moved on the same "COO-line reports go to the new COO" logic since neither read as security-adjacent. Worth John's confirmation, not treated as ambiguous enough to block on. Live-verified: `GET /employees/?platform=automation-nation` returns 27, both CALEB and NEHEMIAH present.

Department slugs in the database are lowercase (`csuite`, `finance`…), not the display labels the roster doc uses — the API returns both `department` and `department_label`.

**A different table, `public.ai_employees` in the AN database, has 24 rows with different names (Abraham, Moses, Samson…).** That is the Automation Nation homepage's display roster — marketing copy, no operational columns. It is not the catalog and nothing in this package touches it. Do not migrate it, do not reconcile it, do not confuse it with the real one again.

## 3. JOANNA IS ALREADY DONE

The row reads `biblical_name = Joanna`, `product_name = Lydia`. The rename decided last session was already implemented using the two-column pattern (product name stays stable for anything that displays it). **Batch 1 Phase 1 as originally written must be skipped** — it would try to rename a row that is already correct. The updated master prompt reflects this.

## 4. THE ACTUAL COLUMNS (build to these, not to the specs' guesses)

From `app/app/routers/employees.py`, the router selects:

```
id, name, biblical_name, product_name, role, department, department_label,
model_tier, tier_access, is_csuite, is_confidential, style, helps,
outside_scope, handoff_to, covers_for, covered_by, reports_to, supervises,
color, bg, config [, system_prompt]
```
plus `is_active` in the filter. A second table `foundation.employee_platform_subscriptions` (`employee_id`, `platform_slug`, `is_active`) gates which agents each platform sees.

Any new agent row (Rahab, Zacchaeus, Silas, and Batches 2–3) must populate **this** column set. Where earlier specs say "match the house column pattern," this is the pattern.

## 5. WHY `/agents` RETURNS 500 — CORRECTED 2026-09-05

**The schema-exposure theory is wrong.** Verified directly against the live project: both the anon key and the service-role key successfully query `foundation.ai_employees` *and* `foundation.agents` via PostgREST right now (`SELECT` succeeds, real rows returned). `foundation` is exposed and grants are fine. Do not re-tick the checkbox or re-run the GRANT block on this theory — there's nothing to fix there.

**The real story: `/agents` and `/employees` are two different, unrelated routes.**
- `GET /employees/?platform=...` (`app/app/routers/employees.py`, service-role client, queries `foundation.ai_employees`) is the real 26-agent catalog endpoint. **It already returns 200 live.** This is the route every platform integration should call.
- `GET /agents` (`app/app/routers/agents.py`, anon client via `get_client()`, queries `foundation.agents`) is a separate, older, largely-unused table — one row, a "Greeting Agent" playground entry from March. It is **not** the roster and never was. It still 500s live on Render as of this check; reproducing the identical query locally (both anon and service-role keys) succeeds, so the cause is Render-environment-specific — most likely `SUPABASE_ANON_KEY` on Render (`render.yaml` marks it `sync: false`, dashboard-managed) is stale or wrong. Needs a Render dashboard check, not a schema-exposure fix. Low priority: nothing in the build order actually depends on this route.

Phase 0's real gate is `/employees/` returning 26 (27 after 0.5) — already true.

## 6. A ROUTER BUG THAT MATTERED FOR SOLOMON — FIXED 2026-09-05

`_resolve_model()` mapped only `orchestrator → COMPLEX`, `standard`, `fast`. The database uses `complex` and `orchestrator_max`; neither was in the map, so every C-suite agent silently fell back to STANDARD (Sonnet). Fixed in `app/app/routers/employees.py` (tier map now covers `orchestrator_max`, `complex`, the legacy `orchestrator` alias, `standard`, `fast`) and `app/app/llm_router.py` (added `TaskTier.ORCHESTRATOR_MAX`, `MODEL_COMPLEX` default `claude-opus-4-8`, `MODEL_STANDARD` default `claude-sonnet-5`, `MODEL_ORCH_MAX` default `claude-fable-5-1`). Verified: every `model_tier` value actually present in `foundation.ai_employees` resolves to the correct model string, and a simulated dry-run Solomon call logs `claude-fable-5-1` to `llm_usage` with the correct cache-blended cost. Branch `batch1-expansion`.

## 7. MIGRATION DRIFT

Foundation's remote database has three migrations (`20260818193841`, `20260818193842`, `20260818195000`) that do not exist in the local repo — applied on August 18 by something outside this repo. `supabase db pull` refuses to run until the histories match, and `supabase db dump` needs Docker, which isn't installed.

Do **not** run the `migration repair --status reverted` commands the CLI suggests until you know what those migrations contain. The safe path is in Phase 0: inspect the live schema through the dashboard SQL editor, capture it into a baseline migration, then reconcile.

Almost certainly those three migrations created `industries`, `industry_playbooks`, and the LLM cost tables (`llm_usage`, `llm_cost_daily`, `llm_cost_monthly`, `llm_model_distribution`) — all present in Foundation's `public` schema.

## 8. WORK THAT ALREADY EXISTS — DON'T DUPLICATE

- `industries` + `industry_playbooks` tables exist in Foundation. The Specialization Engine spec must **extend** them, not create them. Read their live columns first.
- `llm_usage` and the cost rollups exist. The router already logs to them.
- `pricing_config`, `pricing_outcomes`, `pricing_quotes`, `transfer_logs` exist in **both** Foundation and AN databases. That's a drift problem with two sources of truth; it's noted in `02_BUILD_ORDER.md` as a cleanup item, not blocking.

## 9. ENVIRONMENT — DONE; ITEM A CODE ALREADY WRITTEN, NOT YET ON MAIN — CORRECTED 2026-09-05

Set on Render `foundation-api-9gpl` and confirmed deployed: `FOUNDATION_API_KEY`, `CONNECTION_BROKER_ENCRYPTION_KEY`, `ALLOWED_ORIGINS`.

**Item A's code already exists** — it was written in an earlier session that worked from a different local clone (`C:\Users\jjces\OneDrive\Desktop\Claude Foundation`) and never got pushed, so it was invisible to the session that wrote this document originally. It's real now: `CORSMiddleware` + `ALLOWED_ORIGINS` env with localhost fallback, a `require_api_key` dependency (`X-Foundation-API-Key`, fail-closed 503 if unconfigured, 403 on mismatch) in `app/app/main.py`, and `app/app/services/connection_broker.py` (Fernet encrypt/decrypt, fail-closed `RuntimeError` if `CONNECTION_BROKER_ENCRYPTION_KEY` is unset) plus the `foundation.client_connections` table. All on branch `batch1-expansion` (pushed to origin), not yet merged to `main`, so **not yet what's deployed on Render**. Not wired to any router yet — no `/ops` or `/admin` routes exist to gate, and no `/connections/callback` endpoint exists yet (that's item C, Connections Hub). Item A is effectively a verify-and-land step now, not a from-scratch build.

## 10. A LOOSE END TO CLOSE

`supabase link --project-ref rhtwtoinmiekttvunlzs` was run once from inside `AN-repo` by mistake. If that link is still in place, a future `supabase db push` from AN-repo would write AN's two unpushed migrations into the Foundation database. Check `AN-repo\supabase\.temp\project-ref`; if it reads `rhtwtoinmiekttvunlzs`, re-link that folder to `rzsryxvlaezfvftqpvbx`. This is in the checklist as item 0.2.

## 11. MODEL LANDSCAPE AS OF SEPTEMBER 2026

| Model | String | Price (in/out per MTok) | Note |
|---|---|---|---|
| Fable 5.1 | `claude-fable-5-1` | $10 / $50 | Cache reads $0.25 (2.5%) — 75% cheaper than Fable 5. Requires Fallback API config. |
| Opus 4.8 | `claude-opus-4-8` | $5 / $25 | C-suite default (Option A) |
| Sonnet 5 | `claude-sonnet-5` | $2 / $10 | Now permanent; cheaper than Sonnet 4.6 ($3/$15). Move department heads here. |
| Haiku 4.5 | `claude-haiku-4-5-20251001` | — | Triage tier, unchanged |

Fable 5.1 and Opus 4.7+ use a tokenizer producing ~30% more tokens for the same text; caching is mandatory on every C-suite prompt.
