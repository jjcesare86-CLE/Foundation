# BLOCKED ON JOHN — ordered clicks
_Updated 2026-10-23. Items 1-2 unblock the most work._

## Now
1. **Merge, in this order:** Foundation #1 (preflight docs) -> #2 (S0 API code) -> the docs-sync PR (Foundation) . Switchboard: #1 (CI fix), #2 (migration 001, already applied), the docs-sync PR.
2. **Render `foundation-api-9gpl` env, S0.3** (names in `docs/state/ENV_NEEDED.md`): `SWITCHBOARD_SUPABASE_URL`, `SWITCHBOARD_SUPABASE_SERVICE_ROLE_KEY`, `SWITCHBOARD_SUPABASE_JWT_SECRET`, `SWITCHBOARD_SUPABASE_ANON_KEY`, `SWITCHBOARD_PROJECT_REF=gytuxzlrsgbueabywxhh`, and `SWITCHBOARD_JWT_SECRET` (the Phase 1 API token secret; must be a different value). Leave `SWITCHBOARD_DB_MODE` unset until the live checks pass. Supabase > Settings > JWT: if the project uses asymmetric signing keys, enable and copy the legacy HS256 secret. **Unblocks:** live cross-key check, widget JWT check, the flip (F.9.5), item Q seat sync reads.
3. **Switchboard project: turn on daily backups and PITR** (S0.5).
4. **Stripe test mode** (item Q1): create a restricted test key (Checkout, Customers, Subscriptions, Billing Portal, Prices read), set `STRIPE_SECRET_KEY` and `STRIPE_WEBHOOK_SECRET` on Render. Claude Code creates the test products and prices. **Unblocks:** Q1, Q2 and the G.8 gate. Q0 (seat counting, group chats, seat prompt) is NOT blocked by this.
5. **Answer Addendum G.10 open questions** (defaults are fine): #3 mobile/PTT included in seat price (recommend yes, after G.6), #5 connected-agent add-on fee (amount not set), #6 bundles include 5 seats (assumed yes).

## Before launch, not blocking the build
6. **Margin check G.6** after P1/K load tests. Do not publish prices on getswitchboard.io before it. Live Stripe prices (Q3) are created by you after that.
7. `GOOGLE_MAPS_API_KEY`, `PIPELINE_API_KEY`, `GOOGLE_OAUTH_CLIENT_ID/SECRET`, Render `MODEL_*` Phase 0 vars (confirm), `ALLOWED_ORIGINS` additions.
8. **LiveKit Cloud project** -> `LIVEKIT_URL/KEY/SECRET` (unblocks P1, later L). Speech-to-text provider choice and key (P3).
9. Backfill `client_profiles.contact_email` (or approve the invite flow, Addendum C.3) so real clients can self-provision.
10. Google OAuth verification (gmail.send), domains/DNS, trademark search, branch protection, APNS/FCM, Apple PTT entitlement (K/L/M).
