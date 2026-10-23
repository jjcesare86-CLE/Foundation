# BLOCKED ON JOHN — ordered clicks
1. **Addendum F is not in the package or the repo** (searched both for "Addendum F", "ADDENDUM_F", "F.8", "SWITCHBOARD_SUPABASE"). S0 ("do F.8 exactly as written") and the separate-project table layout depend on it. Add `SWITCHBOARD_ADDENDUM_F_*.md` to `docs/specs/` (or paste it). Unblocks: S0, and the DB side of I phases 2-5, P, O.
2. Merge switchboard PR #1 (fixes the CI test script so CI is green).
3. Render `foundation-api-9gpl` env: `SWITCHBOARD_JWT_SECRET` (router 503s without it), the five `SWITCHBOARD_SUPABASE_*` / project-ref vars (exact names per Addendum F), `PIPELINE_API_KEY`, `GOOGLE_MAPS_API_KEY`, `GOOGLE_OAUTH_CLIENT_ID/SECRET`. Names only are listed in `docs/state/ENV_NEEDED.md`.
4. LiveKit Cloud project -> `LIVEKIT_URL/KEY/SECRET` (unblocks P, L). Speech-to-text provider key (captions/notes).
5. Switchboard Supabase project `gytuxzlrsgbueabywxhh`: enable backups/PITR.
6. Backfill `client_profiles.contact_email` (or approve building the invite flow, Addendum C.3) so real clients can self-provision.
7. Google OAuth verification (gmail.send), domains/DNS, trademark search, branch protection, Apple PTT entitlement (K/L/M).
