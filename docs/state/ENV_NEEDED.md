# ENV_NEEDED — names only, never values
_Reconciled 2026-10-23 against `docs/state/ENV_VARS.md` (the package's list) and `grep os.getenv/os.environ` over `app/`. Render state cannot be read from the repo, so "Render" below means: confirmed set per the docs, or `unverified`/`MISSING` until John ticks it in `ENV_VARS.md`. Service: `foundation-api-9gpl`._

Legend. **read** = code reads it today. **planned** = no code reads it yet.

## Already confirmed set (ENV_VARS.md, Sep 2)
| Name | Code | Note |
|---|---|---|
| FOUNDATION_API_KEY | read | same value also on an-sales-pipeline, luts-api, delivered-web |
| CONNECTION_BROKER_ENCRYPTION_KEY | read | app refuses to boot without it |
| ALLOWED_ORIGINS | read | must also list getswitchboard.io, www.getswitchboard.io, switchboard.automaitionnation.com, caleb.automaitionnation.com |
| SUPABASE_URL | read | Foundation (rhtwtoinmiekttvunlzs) |
| SUPABASE_SERVICE_ROLE_KEY, SUPABASE_ANON_KEY | read | Foundation; never reuse for Switchboard (startup guard enforces) |

## Phase 0 (unticked in ENV_VARS.md)
| Name | Code | Status |
|---|---|---|
| MODEL_ORCH_MAX (`claude-fable-5-1`), MODEL_COMPLEX (`claude-opus-4-8`), MODEL_STANDARD (`claude-sonnet-5`) | read | unverified |
| MODEL_COMPLEX_ENTERPRISE (`claude-fable-5-1`) | planned | not read by any code yet (the router has MODEL_FABLE_FALLBACK, MODEL_FAST, MODEL_LONGCTX, MODEL_VOICE; set or retire per John) |

## Item S0, Switchboard database (Addendum F.5 / F.9)
| Name | Code | Status |
|---|---|---|
| SWITCHBOARD_SUPABASE_URL | read (S0.4) | MISSING |
| SWITCHBOARD_SUPABASE_SERVICE_ROLE_KEY | read (S0.4) | MISSING (server only) |
| SWITCHBOARD_SUPABASE_JWT_SECRET | read (S0.4) | MISSING (signs workspace JWTs; if the project uses asymmetric signing keys, see DECISIONS 2026-10-22) |
| SWITCHBOARD_SUPABASE_ANON_KEY | read (S0.4) | MISSING (public; useless without a JWT) |
| SWITCHBOARD_PROJECT_REF | read (S0.4) | MISSING (not secret: `gytuxzlrsgbueabywxhh`) |
| SWITCHBOARD_DB_MODE | read (S0.4) | leave unset (= `foundation`) until the live checks pass, then `switchboard` at cutover (F.9.5) |
| SWITCHBOARD_JWT_SECRET | read (Phase 1 auth) | MISSING per CURRENT.md (router 503s without it). Must differ from SWITCHBOARD_SUPABASE_JWT_SECRET; the startup guard refuses to boot if they match |

## Item Q, billing (Addendum G.7). Stripe TEST MODE ONLY
| Name | Code | Status |
|---|---|---|
| STRIPE_SECRET_KEY | planned (Q1) | MISSING. Restricted test key: Checkout, Customers, Subscriptions, Billing Portal, Prices read |
| STRIPE_WEBHOOK_SECRET | planned (Q1) | MISSING |
| STRIPE_PRICE_SWITCHBOARD_PLATFORM, STRIPE_PRICE_SWITCHBOARD_SEAT | planned (Q1) | created by Claude Code in test mode, then John records the ids on Render |
| STRIPE_PRICE_SWITCHBOARD_PLATFORM_ANNUAL, STRIPE_PRICE_SWITCHBOARD_SEAT_ANNUAL | planned (Q1/Q3) | same |
| (publishable key) | n/a | lives only on the checkout page, not on this service |
No Work Rooms price variable exists, by decision.

## Feature items
| Name | Code | Status |
|---|---|---|
| GOOGLE_MAPS_API_KEY | read | MISSING (Silas/Zacchaeus/Rahab; Distance Matrix + Geocoding) |
| PIPELINE_API_KEY | read | MISSING |
| GOOGLE_OAUTH_CLIENT_ID, GOOGLE_OAUTH_CLIENT_SECRET | read | MISSING (separate GCP OAuth client for the Connections Hub) |
| LIVEKIT_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET | planned (P, later L) | MISSING |
| Speech-to-text provider key | planned (P3) | MISSING; provider not chosen |
| APNS_* / FCM_* | planned (K/L) | MISSING |

## Read by code but not in ENV_VARS.md (add or confirm)
ANTHROPIC_API_KEY (certainly set), VAPI_API_KEY, GHL_API_KEY (found set 2026-09-05), GEMINI_API_KEY, GOOGLE_API_KEY, AN_SUPABASE_URL, AN_SUPABASE_ANON_KEY (public default in code), VOICE_EDIT_HANDOFF_SECRET, VOICE_EDIT_PUBLIC_BASE_URL, MODEL_FABLE_FALLBACK, MODEL_FAST, MODEL_LONGCTX, MODEL_VOICE, FOUNDATION_API_URL and FOUNDATION_API_BASE_URL (two names for one concept; consolidate), ACTION_LIBRARY_DEMO_MODE (optional flag). All `unverified`.
