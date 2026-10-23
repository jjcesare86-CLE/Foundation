# BLOCKED ON JOHN — ordered clicks
1. Addendum F arrived 2026-10-22 (resolved). Merge switchboard PR #2 (migration 001, already applied) and the Foundation S0 PR.
2. Merge switchboard PR #1 (fixes the CI test script so CI is green).
3. Render `foundation-api-9gpl` env (S0.3): `SWITCHBOARD_SUPABASE_URL`, `SWITCHBOARD_SUPABASE_SERVICE_ROLE_KEY`, `SWITCHBOARD_SUPABASE_ANON_KEY`, `SWITCHBOARD_SUPABASE_JWT_SECRET` (Supabase > Settings > JWT: if the project uses asymmetric signing keys, enable and copy the legacy HS256 secret), `SWITCHBOARD_PROJECT_REF=gytuxzlrsgbueabywxhh`. Leave `SWITCHBOARD_DB_MODE` unset until I tell you the live checks passed. Also: `SWITCHBOARD_JWT_SECRET` (router 503s without it), the five `SWITCHBOARD_SUPABASE_*` / project-ref vars (exact names per Addendum F), `PIPELINE_API_KEY`, `GOOGLE_MAPS_API_KEY`, `GOOGLE_OAUTH_CLIENT_ID/SECRET`. Names only are listed in `docs/state/ENV_NEEDED.md`.
4. LiveKit Cloud project -> `LIVEKIT_URL/KEY/SECRET` (unblocks P, L). Speech-to-text provider key (captions/notes).
5. Switchboard Supabase project `gytuxzlrsgbueabywxhh`: enable backups/PITR.
6. Backfill `client_profiles.contact_email` (or approve building the invite flow, Addendum C.3) so real clients can self-provision.
7. Google OAuth verification (gmail.send), domains/DNS, trademark search, branch protection, Apple PTT entitlement (K/L/M).
