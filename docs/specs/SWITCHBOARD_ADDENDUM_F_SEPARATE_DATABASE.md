# SWITCHBOARD — ADDENDUM F: ITS OWN SUPABASE PROJECT
**Switchboard's customer data lives in a dedicated Supabase project, not in Foundation.**
v1.0 · Oct 22, 2026 · DECIDED by John Oct 22. Overrides every earlier line that puts `sb_*`, `ptt_*`, `work_room*` or `connected_agent*` tables in `rhtwtoinmiekttvunlzs`. Runs as item **S0**, before item I.

---

## F.1 Why
- **Different data.** Foundation holds the agent catalog and shared config for every AN product. Switchboard holds customers' private messages, transcripts, voice audio and room recordings.
- **Blast radius.** A bad migration or a leaked service key in Foundation must not expose customer conversations, and the reverse.
- **The promise.** "Private to your business" is easier to stand behind, and to publish on the security page, with its own database, keys and backups.
- **Safer build.** Foundation is live for every AN product. A fresh project is greenfield, so the autopilot run can build and migrate without risk to production.
- **Optionality.** Switchboard can be scaled, billed, backed up, audited or sold on its own.
- **Cost:** about $25/mo (Pro) plus optional point-in-time recovery.

## F.2 What lives where

| Stays in **Foundation** (`rhtwtoinmiekttvunlzs`) | Lives in **Switchboard** (new project) |
|---|---|
| `foundation.ai_employees` catalog, prompts, model router | `sb_workspaces` (mirror, F.4), `sb_memberships` |
| `clients` (the customer record), plans, entitlements | `sb_threads`, `sb_messages`, `sb_pins`, `sb_settings`, `sb_message_renderings` |
| `connection_broker` (Fernet secrets) | `sb_participants` (kind ai/human/room/external/workroom) |
| Proof of Work receipts, action library, `agent_jobs` | `connected_agents`, `connected_agent_egress_log` |
| `llm_usage` metering (task types `sb_translate`, `work_room_minutes`, provider `external`) | `ptt_channels`, `ptt_members`, `ptt_transmissions` |
| Agent Studio definitions, industries/playbooks (item J) | `work_rooms`, `work_room_participants`, `work_room_guest_invites`, `work_room_artifacts`, `work_room_transcript` |
| Foundation API (Render `foundation-api-9gpl`) | Storage buckets: profile photos, voice audio (30-day sweep), room recordings (30-day expiry), shared documents |

Rule of thumb: **if it is a customer's conversation, it is in Switchboard. If it is how an agent is defined, paid for, authorised or audited, it is in Foundation.**

## F.3 Architecture
- **One server talks to both.** Foundation API keeps its Foundation client and gains a second, `switchboard_db`, using `SWITCHBOARD_SUPABASE_URL` and `SWITCHBOARD_SUPABASE_SERVICE_ROLE_KEY`. Agent runs, receipts, the router and the broker stay in Foundation. The API writes messages to Switchboard.
- **Browsers and phones talk only to the Switchboard project.** The API exchanges the host product's session for a short-lived Switchboard JWT (claims: `workspace_id`, `user_id`, `role`), signed with the **Switchboard** project's signing secret. RLS on every table keys off `workspace_id` in that JWT. The widget uses it for Realtime reads. Writes still go through the API. **No Foundation key or Foundation URL ever reaches a client.**
- **Humans are not Supabase Auth users in the new project.** Identity stays in the host products (AN, AssistMIO, a client dashboard). `sb_memberships.user_id` is a plain UUID.
- **LiveKit, STT and push stay in Foundation API config** (tokens minted there), not in the Switchboard database.

## F.4 Cross-project references (no foreign keys across projects)
1. **Workspace.** `workspace_id` / `client_id` is the Foundation `clients.id`. Every `REFERENCES clients(id)` in the earlier specs now reads `REFERENCES sb_workspaces(id)`:
```sql
CREATE TABLE IF NOT EXISTS sb_workspaces (
  id UUID PRIMARY KEY,                 -- = Foundation clients.id (same value)
  name TEXT NOT NULL,
  plan TEXT,                           -- mirror of entitlement tier, display only
  status TEXT NOT NULL DEFAULT 'active', -- active | suspended | closed
  is_internal_property BOOLEAN DEFAULT FALSE,
  synced_at TIMESTAMPTZ DEFAULT NOW()
);
```
Foundation API upserts a row when a workspace first opens Switchboard and on plan/status changes. If Foundation marks a client suspended, the API sets `status='suspended'` and mints no new JWTs.
2. **Agents.** `sb_participants.kind='ai'` carries the catalog slug (and Agent Studio id) as text. The API validates it against `foundation.ai_employees` on every write. Nothing in this project may copy prompts or model settings.
3. **Broker secrets.** `connected_agents.secret_ref` and `signing_secret_ref` are opaque ids resolved only inside Foundation API. The secret never enters this project.
4. **Receipts.** A message that shows a receipt stores the Foundation receipt id. The widget fetches the receipt body through the API.
5. **Metering.** Usage rows are written to Foundation `llm_usage`. This project stores counts only where the UI needs them.

## F.5 Environment variables (Render, on `foundation-api-9gpl`)
| Var | Purpose |
|---|---|
| `SWITCHBOARD_SUPABASE_URL` | Switchboard project URL |
| `SWITCHBOARD_SUPABASE_SERVICE_ROLE_KEY` | Server-only. Never in a client, repo or log |
| `SWITCHBOARD_SUPABASE_JWT_SECRET` | Signs workspace JWTs (use the project's current signing method per Supabase docs) |
| `SWITCHBOARD_SUPABASE_ANON_KEY` | Public key the widget needs for Realtime. Safe to ship, useless without a JWT |
| `SWITCHBOARD_PROJECT_REF` | Project ref (not secret). Used by migrations and checks |
Existing `SUPABASE_URL` and keys keep pointing at Foundation. The two sets must never be swapped. The API refuses to start if both URLs are identical.

## F.6 Safety rules
1. Switchboard migrations live in the **switchboard repo** (`supabase/` there), linked to the new project only. Foundation migrations stay in the Foundation repo, linked to `rhtwtoinmiekttvunlzs`. Check `supabase projects list` for the LINKED marker before every migration in either repo.
2. RLS on **every** table, deny by default. The Addendum C cross-workspace tests, the Addendum D security tests, and the Addendum E room tests all run against this project.
3. Backups: turn on daily backups and point-in-time recovery (John, dashboard). Retention sweeps for audio (30 days) and recordings (30 days) run as a scheduled job and are tested.
4. Never run `db dump/pull/reset` (no Docker). Introspect with SQL.
5. Never reuse a Foundation key, JWT secret or anon key in this project.

## F.7 Item S0 — ship order
| Step | Who | What |
|---|---|---|
| S0.1 | **John** | Create the project in the Supabase dashboard (name `switchboard`, Pro plan, region matching the Render service). Give Claude Code the **project ref** only. Save the DB password in your password manager |
| S0.2 | Claude Code | In the switchboard repo: `supabase link --project-ref <ref>`; migration 001 creates `sb_workspaces` and the core `sb_*` tables with RLS; verify with live queries |
| S0.3 | **John** | Render env: the five vars in F.5 |
| S0.4 | Claude Code (Foundation repo) | Add `switchboard_db` client, the startup guard, the workspace-JWT mint endpoint, the `sb_workspaces` sync; tests incl. cross-workspace RLS |
| S0.5 | **John** | Turn on PITR and daily backups |
| S0.6 | Claude Code + **John** | Cut over per F.9: inventory, dual-mode, copy if needed, flip, retire after 14 days |
Gate: three seeded workspaces; user A cannot read workspace B's rows with any JWT; a Foundation key does not work on the Switchboard project and vice versa; the API refuses to boot with identical URLs.

## F.8 CLAUDE CODE PROMPT — item S0
```
Same session header as the RUNBOOK, with ONE change: Switchboard data lives in its
own Supabase project (docs/specs/SWITCHBOARD_ADDENDUM_F_SEPARATE_DATABASE.md). Read it
fully. The project ref is <SWITCHBOARD_PROJECT_REF> (John provides it; it is not a
secret). Never touch rhtwtoinmiekttvunlzs from the switchboard repo, and never run
Switchboard migrations from the Foundation repo.

1. switchboard repo: supabase link; confirm LINKED marker; write migration 001
   (sb_workspaces, sb_memberships, sb_threads, sb_messages, sb_pins, sb_settings,
   sb_message_renderings, sb_participants, plus the columns from Addenda B/C/D and
   05_CONVERSATION_DISCIPLINE open_items). Replace every `REFERENCES clients(id)`
   with `REFERENCES sb_workspaces(id)`. RLS on all tables keyed on the JWT claim
   workspace_id. Show me the SQL, apply after approval, verify with live queries.
2. Foundation repo: add switchboard_db.py (second client from SWITCHBOARD_* env),
   startup guard (refuse to boot if URLs match), POST /switchboard/token (exchange
   host session for workspace JWT), sb_workspaces upsert on first open and on
   status change.
3. Tests: cross-workspace read/write denied for every table; Foundation keys fail on
   the Switchboard project and vice versa; suspended workspace gets no JWT.
Do not print or log any key. Report which env vars John still needs to set.
```

## F.9 Moving what is already live (Phase 1 shipped in Foundation before this addendum)
Switchboard Phase 1 (`20260905220000_switchboard_phase1_schema.sql`) and its `/switchboard/*` endpoints already run against the Foundation database. S0 therefore has two jobs: build the new project, then cut over. **Never drop or rewrite the Foundation tables in this item.**
1. **Inventory (read-only).** In Foundation, list every `sb_*` table with row counts and the endpoints and modules that read or write them. Report it. If every table holds only test or seed data, say so.
2. **Build the new project.** Migration 001 in the switchboard repo recreates the Phase 1 schema (same table and column names, so API code changes are minimal) plus `sb_workspaces`, the F.4 foreign-key changes and RLS. Apply after John approves the SQL.
3. **Dual-mode API.** Add `SWITCHBOARD_DB_MODE` (`foundation` default, `switchboard`). All `/switchboard/*` data access goes through one repository layer that picks the client by mode. Tests must pass in both modes.
4. **Copy data if any is real.** One-off script, service role to service role, no secrets printed: copy rows in dependency order, then verify counts and a per-table checksum. Test or seed data is re-seeded instead of copied.
5. **Flip.** Set `SWITCHBOARD_DB_MODE=switchboard` on Render (John), watch for errors, run the cross-workspace RLS tests against the new project, and keep Foundation tables untouched as the rollback.
6. **Retire (separate approval, no sooner than 14 days after the flip).** Rename the Foundation `sb_*` tables to `sb_*_legacy_YYYYMMDD`. Dropping them is a separate destructive step and needs John's explicit yes.
7. **JWTs.** The existing Phase 1 token (`SWITCHBOARD_JWT_SECRET`) authenticates calls to the Foundation API and stays as is. The new `SWITCHBOARD_SUPABASE_JWT_SECRET` token is a second, separate token that lets the widget read the Switchboard project directly with RLS. Do not reuse one secret for both.
Add to F.5: `SWITCHBOARD_DB_MODE` (not secret, default `foundation`).
