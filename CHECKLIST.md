# CHECKLIST
_Follow RUNBOOK.md top to bottom; tick here as each gate turns green._
_Tick as you go. Each item's VERIFY gate is in its spec. Never start the next item on a red gate._

## Phase 0 — Restore the API (`docs/specs/03_PHASE0_RESTORE_API.md`)
- [ ] 0.1 Expose `foundation` schema in Supabase API settings + run GRANT block
- [ ] 0.1 `/agents` returns 200 with 26 rows (if not, check `employee_platform_subscriptions` has rows)
- [ ] 0.2 AN-repo re-linked to `rzsryxvlaezfvftqpvbx`; `Foundation_Scaffold` renamed
- [ ] 0.3 Migration drift reconciled — `supabase migration list` Local = Remote
- [ ] 0.4 Router tier map fixed; Render env `MODEL_ORCH_MAX`, `MODEL_COMPLEX`, `MODEL_STANDARD`, `MODEL_COMPLEX_ENTERPRISE` set
- [ ] 0.5 Roster change: Caleb → CISO, Nehemiah → COO, Ezra reports to Caleb (`04_ROSTER_CHANGE_CALEB_SECURITY.md`); `/agents` = 27
- [ ] 0.5 Decide the AN "Ask Caleb" button: keep, or move to Nehemiah
- [ ] 0.6 Gate: dry-run Solomon logs `claude-fable-5-1`; dry-run Nehemiah logs `claude-opus-4-8`

## A — Security foundations (`FOUNDATION_FIXES_GUIDE.md`)
- [ ] CORS whitelist reads `ALLOWED_ORIGINS`
- [ ] `X-Foundation-API-Key` gate on `/ops/*` and `/admin/*`
- [ ] `connection_broker.py` Fernet encrypt/decrypt; refuses to boot without key
- [ ] Same `FOUNDATION_API_KEY` set on an-sales-pipeline, luts-api, delivered-web
- [ ] Curl checks pass (public open, internal 403, with-key 200)

## B — Batch 1 (`CLAUDE_CODE_MASTER_PROMPT_BATCH1.md`)
- [ ] Phase 0 Option A/B router + Fallback API + cost table
- [ ] Phase 1 Joanna verify-only sweep
- [ ] Phase 2 Rahab + typed action library + approval inbox
- [ ] Phase 3 Zacchaeus (Delivered Fireworks + LUTS seeded)
- [ ] Phase 4 Silas (PostGIS, `claim_slot()`, Google Maps key set)
- [ ] Phase 5 roster integrity — 30 active, subscriptions seeded
- [ ] Phase 6 merged, Render green, `BATCH1_COMPLETION_REPORT.md` written

## D — Ops audit, Part A (`AGENT_OPS_AUDIT_ELIJAH_V1_1.md`)
- [ ] `required_capabilities` + `agent_jobs` registry; all crons heartbeat
- [ ] `/ops/agent-health` + nightly audit + admin grid
- [ ] `docs/state/OPS_AUDIT.md` produced; John's red-list actioned
- [ ] Known items: `PIPELINE_API_KEY`, `gemini_voice_proxy.py` deploy

## C — Connections Hub (`CONNECTIONS_HUB_BUILD.md`)
- [ ] Google OAuth app verification submitted (gmail.send) — start day one
- [ ] `client_connections` table, five endpoints, tokens encrypted
- [ ] Hub page: cards, popup OAuth, GHL deep-links, Stripe Connect
- [ ] Onboarding stub URLs replaced; nightly token health cron

## E — Proof of Work + Unlazy (`UNLAZY_AND_PROOF_OF_WORK.md`)
- [ ] Unlazy installed per-project on Foundation; commit pinned in DECISIONS
- [ ] Receipt columns + `agent_task_receipts`; broker returns receipts
- [ ] PROOF OF WORK block in all agent prompts (Eden exempt)
- [ ] CONVERSATION DISCIPLINE block in all agent prompts (Eden included); six §4 tests green
- [ ] Ops audit L5 asserts verified receipts

## H — Batches 2 + 3 (spec to be written when B is green)
- [ ] Obadiah, Bezalel, Priscilla
- [ ] Amos, Tabitha

## H+ — Gabriel reactivation (RUNBOOK.md)
- [ ] Decision: Gabriel in the launch roster?
- [ ] Row + subscriptions + typed actions on the shared action library
- [ ] Seeded transcript → pending actions → approve → verified receipt

## F — Autopilot nuances (`AUTOPILOT_NUANCES_IMPLEMENTATION.md`)
- [ ] M3 preflight (Blast Video first)
- [ ] M2 brand voice + platform playbooks + validator
- [ ] M1 interview engine
- [ ] M4 behavioral sliders (hard floors enforced)
- [ ] M5 state dirs in each repo · M6 nightly repo scout

## G — Elijah scoreboard (`ELIJAH_SCOREBOARD_BUILD.md` + Ops Audit Part B)
- [ ] Metrics warehouse + GHL ingestion + in-house CTA logging
- [ ] Scoreboard UI per approved mockup; recommendation → action library
- [ ] v1.1: calls (VAPI + tracking numbers) and web traffic (GA4 card + beacon)

## I — Switchboard web (`SWITCHBOARD_BUILD.md`)
- [ ] P1 widget core (Shadow DOM), bootstrap/threads, AN embed, `sb_*` tables incl. `open_items`
- [ ] P2 proactive DMs from action library; presence from `agent_jobs`; handoffs
- [ ] P3 voice call button (VAPI); summaries into thread
- [ ] P4 embeds: AssistMIO, VoiceMIO, Blast Video, MRLIN, then Exterior Rescue
- [ ] P5 locked-agent upsell flow
- [ ] Domains + trademark knockout search for "Switchboard" (`SWITCHBOARD_NAMING.md`)

## J — Specialization engine (`SWITCHBOARD_V1_1_TIERS_AND_SPECIALIZATION.md`)
- [ ] Read live `industries` / `industry_playbooks` columns; extend, don't recreate
- [ ] Two-tier bootstrap (internal properties vs clients)
- [ ] Generate Wave 1 (7 industries); John reviews fireworks + roofing

## N — Launch pages (RUNBOOK.md — runs in the AN repo)
- [ ] `caleb.automaitionnation.com` — Caleb as CISO (decided)
- [ ] `switchboard.automaitionnation.com` live, HTTPS, Lighthouse ≥ 90
- [ ] Security page live; both subdomains in `ALLOWED_ORIGINS`

## K — Native mobile, phases 1–4 (`SWITCHBOARD_NATIVE_MOBILE_VOICE.md`)
- [ ] Apple PTT entitlement request FILED (day one of K)
- [ ] Capacitor shell + capability detection
- [ ] Android mic foreground service · iOS Tier A background audio
- [ ] Offline queue; queued never renders as sent

## L — Live PTT (`SWITCHBOARD_ADDENDUM_A_LIVE_PTT.md`)
- [ ] Channel tables + SFU + transcripts into threads + `ptt_usage` metering
- [ ] Android receive + hardware buttons
- [ ] Agent transmission with rate limits + quiet mode
- [ ] Retention sweep: audio 30 days, transcripts forever

## M — iOS PushToTalk framework
- [ ] Entitlement approved → framework integration, BT buttons, locked-screen
- [ ] If denied → live-audio-room fallback on the same channels
- [ ] App Store readiness: privacy labels, crash reporting, version gate, support runbook
