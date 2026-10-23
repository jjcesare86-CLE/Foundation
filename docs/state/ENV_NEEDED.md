# ENV_NEEDED — names only, never values
_Generated 2026-10-22 by the autopilot run from `grep os.getenv/os.environ` over `app/`. "Set on Render?" cannot be read from the repo; it is marked `unverified` until John confirms in the Render dashboard (foundation-api-9gpl → Environment)._

## Read by code today
| Name | Read by | Status |
|---|---|---|
| SUPABASE_URL, SUPABASE_SERVICE_KEY / SUPABASE_SERVICE_ROLE_KEY, SUPABASE_ANON_KEY | config, routers | in `.env.example`; Render: confirmed per 00_STATE §1 |
| ANTHROPIC_API_KEY | llm_router | unverified (credits confirmed working 2026-09-09) |
| MODEL_ORCH_MAX, MODEL_COMPLEX, MODEL_STANDARD, MODEL_FAST, MODEL_LONGCTX, MODEL_VOICE, MODEL_FABLE_FALLBACK | llm_router | unverified |
| FOUNDATION_API_KEY, CONNECTION_BROKER_ENCRYPTION_KEY, ALLOWED_ORIGINS | main, broker | confirmed set (00_STATE §9) |
| FOUNDATION_API_URL, FOUNDATION_API_BASE_URL | ops, voice_edit | unverified (two names for one concept: consolidate) |
| SWITCHBOARD_JWT_SECRET | switchboard/auth | MISSING per CURRENT.md blockers (router fails closed, 503) |
| GOOGLE_OAUTH_CLIENT_ID, GOOGLE_OAUTH_CLIENT_SECRET | connections/google_oauth | MISSING per CURRENT.md blockers |
| GOOGLE_MAPS_API_KEY | Silas | MISSING per CURRENT.md blockers |
| PIPELINE_API_KEY | ops audit | MISSING per RUNBOOK (known item) |
| VAPI_API_KEY | voice | unverified |
| GHL_API_KEY | rahab/ghl_client | unverified |
| GEMINI_API_KEY, GOOGLE_API_KEY | gemini_voice_proxy, voice_edit | unverified |
| AN_SUPABASE_URL | pricing | unverified |
| VOICE_EDIT_HANDOFF_SECRET, VOICE_EDIT_PUBLIC_BASE_URL | voice_edit | unverified |
| ACTION_LIBRARY_DEMO_MODE | action_library | optional flag |

## Needed by the Switchboard build, not yet read by any code (name only)
| Name | Needed for | Status |
|---|---|---|
| SWITCHBOARD_SUPABASE_URL, SWITCHBOARD_SUPABASE_SERVICE_ROLE_KEY, SWITCHBOARD_SUPABASE_ANON_KEY, SWITCHBOARD_SUPABASE_JWT_SECRET, SWITCHBOARD_SUPABASE_PROJECT_REF | S0 (separate Switchboard project, Addendum F). **Exact names are a guess from the run prompt ("the five SWITCHBOARD_SUPABASE_*/PROJECT_REF vars"); Addendum F was not in the package, so confirm names.** | MISSING |
| LIVEKIT_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET | Work Rooms (P), PTT (L) | MISSING |
| STT provider key (name TBD) | Work Rooms captions/notes | MISSING |
