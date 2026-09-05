# PHASE 0 — RESTORE THE API
**Nothing else in this package can be verified until `/agents` returns 26 rows. Do this first.**

Three problems, all found last session, all small. In order:

---

## 0.1 Expose the `foundation` schema (John, dashboard — 2 minutes)

Supabase → project `rhtwtoinmiekttvunlzs` → **Project Settings → API → Exposed schemas** → tick **foundation** → Save. PostgREST reloads within about a minute.

Then run in the **SQL Editor** (same project) — the checkbox exposes the schema, the grants let the API roles read it:

```sql
grant usage on schema foundation to anon, authenticated, service_role;
grant select on all tables in schema foundation to anon, authenticated, service_role;
grant select on all sequences in schema foundation to anon, authenticated, service_role;
alter default privileges in schema foundation grant select on tables to anon, authenticated, service_role;
```

Verify from PowerShell:
```powershell
try { (Invoke-WebRequest "https://foundation-api-9gpl.onrender.com/agents").StatusCode } catch { $_.Exception.Response.StatusCode }
```
Expect `200`. If still 500, the route filters on `employee_platform_subscriptions` before it ever reads employees — confirm that table has rows:
```sql
select platform_slug, count(*) from foundation.employee_platform_subscriptions where is_active group by 1;
```
If it's empty, that's the remaining cause: the route returns early on an empty subscription list. Seed the subscriptions for your platforms (all 26 agents for `an`, `assistmio`, `voicemio`, `blast-video`, `mrlin`, `luts`, `delivered-fireworks` — whatever slugs the platforms use; check the existing rows for the exact slug convention before inserting).

## 0.2 Fix the AN-repo link (John, terminal — 1 minute)

```powershell
Get-Content "C:\Users\jjces\OneDrive\Desktop\AN-repo\supabase\.temp\project-ref"
```
If it prints `rhtwtoinmiekttvunlzs`:
```powershell
cd "C:\Users\jjces\OneDrive\Desktop\AN-repo"
supabase link --project-ref rzsryxvlaezfvftqpvbx
```
Then rename the dead folder so it stops competing for tab-completion:
```powershell
Rename-Item "C:\Users\jjces\OneDrive\Desktop\Foundation_Scaffold" "ZZ_old_scaffold"
```

## 0.3 Reconcile migration drift (Claude Code — first session)

Three remote migrations aren't in the repo, and `db pull` refuses to run until they match. Do **not** run `migration repair --status reverted` blind. Paste into Claude Code in the Foundation repo:

```
Foundation repo. Supabase project rhtwtoinmiekttvunlzs is linked. Docker is NOT
available on this machine, so `supabase db dump` and `db pull` cannot run —
work through the Supabase dashboard SQL or the Postgres connection string
instead.

1. Introspect the live schema without Docker: query information_schema for all
   tables and columns in schemas `public` and `foundation`, plus all functions,
   RLS policies, and the contents of supabase_migrations.schema_migrations.
   Save the result to docs/state/LIVE_SCHEMA_2026-09.md.

2. Read supabase/migrations/. Report which remote migration versions
   (20260818193841, 20260818193842, 20260818195000) have no local file, and
   from the live schema infer what each one created. Write the inference to
   docs/state/MIGRATION_DRIFT.md — do not guess silently.

3. Reconcile: create a baseline migration file
   supabase/migrations/20260818195000_baseline_captured.sql containing the
   CREATE statements for every table/function/policy that exists remotely but
   has no local migration (generated from step 1, idempotent with IF NOT
   EXISTS). Then run the three `supabase migration repair --status applied`
   commands (applied, NOT reverted) so the history table matches the files.
   Verify with `supabase migration list` — Local and Remote columns must
   agree with nothing pending.

4. Commit: "chore: capture live schema baseline, reconcile migration history"
Do not push any schema changes in this session. This is bookkeeping only.
```

## 0.4 Fix the router tier map (Claude Code — same session)

```
In app/app/routers/employees.py, _resolve_model() maps only
'orchestrator' | 'standard' | 'fast'. The database uses 'complex' and
'orchestrator_max'; both currently fall through to STANDARD, so all five
C-suite agents are running on Sonnet.

1. In app/llm_router.py add TaskTier.ORCHESTRATOR_MAX resolving from env
   MODEL_ORCH_MAX (default "claude-fable-5-1"). Set the COMPLEX default to
   "claude-opus-4-8" and STANDARD default to "claude-sonnet-5".
2. In employees.py, make the tier map:
     "orchestrator_max": TaskTier.ORCHESTRATOR_MAX,
     "complex":          TaskTier.COMPLEX,
     "orchestrator":     TaskTier.COMPLEX,   # legacy alias, keep
     "standard":         TaskTier.STANDARD,
     "fast":             TaskTier.FAST,
3. Add the comment block at the top of llm_router.py:
   "# ENTERPRISE FLIP: set MODEL_COMPLEX=claude-fable-5-1 in Render to move
    the full C-suite to Fable 5.1. See docs/specs/FOUNDATION_BATCH1... Part 0.1."
4. Unit test: for each model_tier value present in foundation.ai_employees,
   assert _resolve_model returns the expected model string from env.
5. Do NOT change the cost table or add Fallback API config yet — that is
   Batch 1 Phase 0. This is the minimum to stop Solomon running on Sonnet.
Commit: "fix(router): map complex + orchestrator_max tiers; Sonnet 5 default"
```

Render env vars to set alongside (John): `MODEL_ORCH_MAX=claude-fable-5-1`, `MODEL_COMPLEX=claude-opus-4-8`, `MODEL_STANDARD=claude-sonnet-5`, and the staged placeholder `MODEL_COMPLEX_ENTERPRISE=claude-fable-5-1`.

## 0.5 Roster change — Caleb to CISO, Nehemiah to COO (Claude Code — same session)
Run the migration prompt in `04_ROSTER_CHANGE_CALEB_SECURITY.md`. Batch 1 references the C-suite, so this lands before it.

## 0.6 Gate

Phase 0 is done when all four are true:
- `GET /agents` returns 200 with 26 rows before 0.5, 27 after
- `supabase migration list` shows Local and Remote in agreement
- The unit test in 0.4 passes and a dry-run Solomon call logs `claude-fable-5-1` to `llm_usage`
- AN-repo's project-ref reads `rzsryxvlaezfvftqpvbx`

Then move to item A in `02_BUILD_ORDER.md`.
