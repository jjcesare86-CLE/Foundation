# CONNECTIONS HUB — COMPLETION REPORT
**2026-09-05 · Foundation branch `batch1-expansion` + AN-repo branch `connections-hub`**

## What shipped

**Foundation** (`batch1-expansion`): `client_connections` extended to the spec's shape (kept the app-level Fernet encryption already built rather than the spec's own Vault/pgsodium line, which predates and is superseded by the 2026-07-08 decision). Real Google OAuth2 module (authorize URL, token exchange, refresh — `app/app/connections/google_oauth.py`). `connection_broker.py` extended with the agent-facing layer (`get_valid_token` with auto-refresh, `send_email`, `create_event`, `post_social`) — token resolution is real, the actual Gmail/Calendar/GHL-social API calls are marked TODOs pending real credentials. All 5 `/connections` endpoints, split public-callback vs. gated-admin. Nightly token-health cron. Fallback-line copy for Nathan/Esther/Naomi/Joanna stored in `config` (none of the four have a `system_prompt` yet to append to — see `OPS_AUDIT.md`).

**AN-repo** (`connections-hub`, not pushed): `/dashboard/connections` page — card grid, plain-English copy, popup OAuth, progress banner, human-language failure states. A server-side proxy router (`connections_proxy.py`) so the browser never sees `FOUNDATION_API_KEY`. Replaced the dead `auth.automaitionnation.com` and placeholder-client-id Google stub URLs in `onboarding/teams/social_media.py` and `google_ecosystem.py` with real hub links.

## Real, unresolved gaps (flagged in code, not hidden)
1. **No Google OAuth credentials exist.** `GOOGLE_OAUTH_CLIENT_ID`/`SECRET` aren't set anywhere — every function that needs them raises a clear error rather than attempting a doomed call. Google's app-verification submission for `gmail.send` (1-2 weeks) hasn't started because there's no client to submit yet.
2. **No AN-user → Foundation-client_id mapping.** The hub page and its proxy both take `client_id` from an explicit param (query string / request body) rather than resolving it from the AN session, because nothing establishes that link anywhere in either codebase today. Fine for the onboarding-pipeline and post-purchase-email entry points (both already carry the id per the spec's own URL format); the permanent dashboard-nav entry point still needs this solved for real.
3. **Gmail send / Calendar create / GHL social post are all TODOs.** `connection_broker`'s token resolution (including refresh) is real and tested; the actual outbound API calls after resolving a token are not implemented yet.
4. **Stripe Connect onboarding link and the GHL social deep-link** are "coming soon" placeholders on the hub page — not built this pass.
5. Blast Video's `signInWithOAuth` usage turned out to be a bare Supabase Auth sign-in (no scopes, no callback route) — nothing there was mechanically reusable; the new Google OAuth module was built from scratch against the real spec (authorization-code + offline access) instead.

## Not done from the original kickoff
- QuickBooks card is "Coming soon" only, no integration attempted (matches spec's own v1 scope).
- No Ayrshare/Nango/Composio evaluation (Phase 4, spec's own "only when a paying client needs a platform GHL doesn't cover" — not triggered).
