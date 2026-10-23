# ENV VARS — Render `foundation-api-9gpl` (names only; never put values in git or chat)
Updated Oct 22, 2026. Tick as you set them.

## Set already (confirmed Sep 2)
- [x] FOUNDATION_API_KEY (same value also on an-sales-pipeline, luts-api, delivered-web)
- [x] CONNECTION_BROKER_ENCRYPTION_KEY
- [x] ALLOWED_ORIGINS (add getswitchboard.io, www.getswitchboard.io, switchboard.automaitionnation.com, caleb.automaitionnation.com)
- [x] SUPABASE_URL (Foundation, rhtwtoinmiekttvunlzs)

## Phase 0
- [ ] MODEL_ORCH_MAX=claude-fable-5-1
- [ ] MODEL_COMPLEX=claude-opus-4-8
- [ ] MODEL_STANDARD=claude-sonnet-5
- [ ] MODEL_COMPLEX_ENTERPRISE=claude-fable-5-1

## Item S0 — Switchboard database (Addendum F)
- [ ] SWITCHBOARD_SUPABASE_URL
- [ ] SWITCHBOARD_SUPABASE_SERVICE_ROLE_KEY   (server only)
- [ ] SWITCHBOARD_SUPABASE_JWT_SECRET          (signs workspace JWTs)
- [ ] SWITCHBOARD_SUPABASE_ANON_KEY            (public; needs a JWT to do anything)
- [ ] SWITCHBOARD_PROJECT_REF                  (not secret)
- [ ] SWITCHBOARD_DB_MODE=foundation           (flip to `switchboard` at cutover, F.9)
- [ ] SWITCHBOARD_JWT_SECRET                   (existing Phase 1 API token; keep separate from the Supabase one)

## Item Q — billing (Addendum G)
- [ ] STRIPE_SECRET_KEY                (restricted key; test mode first)
- [ ] STRIPE_WEBHOOK_SECRET
- [ ] STRIPE_PRICE_SWITCHBOARD_PLATFORM, STRIPE_PRICE_SWITCHBOARD_SEAT (+ _ANNUAL versions)

## Feature items
- [ ] GOOGLE_MAPS_API_KEY            (before Silas/Zacchaeus/Rahab; Distance Matrix + Geocoding)
- [ ] PIPELINE_API_KEY               (env audit item)
- [ ] LIVEKIT_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET   (Work Rooms, item P)
- [ ] Speech-to-text provider key    (Work Rooms captions; provider not chosen yet)
- [ ] APNS_* / FCM_*                 (push; with mobile and PTT, items K/L)
- [ ] Google OAuth client id/secret for the Connections Hub (separate GCP OAuth client)

## Confirm in the audit
- [ ] ANTHROPIC_API_KEY (certainly set), Foundation service-role key (server only)

## PHP Shield (merged PR #4) — no new vars of its own
- [ ] ALLOWED_ORIGINS — add https://automaitionnation.com and https://www.automaitionnation.com (browser scan box; default is localhost-only)
- [ ] SUPABASE_SERVICE_ROLE_KEY — lead insert; failures are swallowed, so a missing key silently drops leads
- [ ] FOUNDATION_API_KEY — admin `GET /php-shield/leads/{id}` (already listed above)
- [ ] Apply migration `*_php_shield_schema.sql` + seed `sql/seeds/003_php_shield_agent.sql`

## Defaults that are wrong or insecure in production
- [ ] VOICE_EDIT_HANDOFF_SECRET — code default is the literal "CHANGE-ME-IN-RENDER"
- [ ] SUPABASE_SERVICE_KEY — voice_employee_builder reads this name, not SUPABASE_SERVICE_ROLE_KEY; set both to the same value
- [ ] sql/run_migrations.py hardcodes a Supabase access token as the default for SUPABASE_ACCESS_TOKEN in this PUBLIC repo — revoke it in Supabase and remove the default
