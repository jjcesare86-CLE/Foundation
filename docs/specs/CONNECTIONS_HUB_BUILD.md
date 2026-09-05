# CONNECTIONS HUB — BUILD SPEC v1.0
**One page. One button per service. A fifth grader can do it.**
Scope: AN client dashboard + AssistMIO (shared Foundation backend) · July 6, 2026

---

## 1. AUDIT FINDINGS

| What | Status | Reality |
|---|---|---|
| `connect_social_accounts` task in an-sales-pipeline onboarding | ⚠️ STUB | Generates URLs to `auth.automaitionnation.com/oauth/{platform}` — that service was never built. Clicking = dead end. |
| Social Brand Launcher | ✅ Real | Done-for-you intake form → you build the accounts. Not self-serve connection. |
| GHL subaccount social integrations | ✅ Real, hidden | GHL natively OAuths FB, IG, TikTok, LinkedIn, GMB inside Social Planner. Clients never find it. |
| Google OAuth (Supabase auth) | ✅ Proven | Working pattern already shipped in Blast Video (`signInWithOAuth`). Reusable. |
| Email/calendar/Stripe connection UI | ❌ None | No interface anywhere. |

**Verdict:** Nathan (Social Media Manager) and Esther (Email/SMS) currently have no clean way for a CLIENT to hand them the keys. Fix below.

---

## 2. ARCHITECTURE DECISION

Three ways to get OAuth connections. Recommendation: **Hybrid A+C.**

**Option A — Ride GHL (social, reviews, GMB).** Every client already has a GHL subaccount. GHL's LeadConnector OAuth already has approved Meta/TikTok/LinkedIn apps — meaning ZERO app-review wait (Meta app review alone takes 2–6 weeks if you build your own). The Connections Hub card deep-links (or iframes, if your white-label plan allows) straight into that subaccount's social integration flow. Cost: $0 — already paying for GHL.

**Option B — Build our own OAuth apps per platform.** Full control, full pain: Meta app review, TikTok audit, LinkedIn partner program, token refresh infrastructure, compliance re-reviews annually. **Rejected for v1.** Revisit only if GHL becomes a constraint.

**Option C — Direct OAuth where it's easy + an aggregator where it's not.**
- **Google (Gmail, Calendar, Business Profile) and Microsoft (Outlook/365):** direct OAuth — you've already done Google in Blast Video. 1–2 days each.
- **Anything exotic (Pinterest, Threads, Substack, podcast platforms for the 33-platform Launcher):** use a unified social API service (evaluate Ayrshare — it ships a hosted, white-labelable "connect your accounts" page which is literally the fifth-grader experience, ~$149+/mo agency plans; alternatives: Nango, Composio). Only add when a paying client needs a platform GHL doesn't cover.

**Decision for v1:** GHL handles FB/IG/TikTok/LinkedIn/GMB/reviews. Direct OAuth handles Google + Microsoft email/calendar. Stripe uses Stripe Connect onboarding link (hosted by Stripe, already dead simple). Everything else = "Coming soon" cards until demanded.

---

## 3. UX SPEC — THE FIFTH-GRADER TEST

**Route:** `/dashboard/connections` (AN client portal + AssistMIO). Nav label: **"Connect Your Accounts"** — never "Integrations," never "OAuth."

**Layout:** grid of big cards, one per service. Each card:
- Platform logo (big)
- Plain-English line — not tech-speak:
  - Facebook & Instagram: *"Let Nathan post and reply for you"*
  - Google Business: *"Let Rahab answer your Google reviews"*
  - Gmail / Outlook: *"Let Esther send emails from your address"*
  - Calendar: *"Let Naomi book appointments on your calendar"*
  - Stripe: *"Let Lydia send invoices and take payments"*
  - QuickBooks: *"Let Zacchaeus keep your books"* (Coming soon)
- ONE button: **Connect** (brand gold). That's the whole card.
- States: `Not connected` (gold button) → `Connecting…` (spinner) → `✅ Connected as @handle` (green, with tiny "Disconnect" text link) → `⚠️ Reconnect needed` (amber — token expired; one click fixes).

**Rules that make it fifth-grader proof:**
1. Clicking Connect NEVER asks the client to type anything except their normal login on the platform's own official page. Zero API keys, zero copy-paste, zero settings.
2. Every OAuth flow opens in a popup and returns to the same page with the checkmark lit. No dead-end redirects.
3. A progress banner up top: "3 of 6 connected — you're almost there!" (completion gamification).
4. **Voice-guided option:** a "Need help? Ask Mia/Celeste" button on the page — VAPI web call where the agent walks them through it out loud. You already have the orb pattern.
5. Empty-state education: if nothing is connected, show a 30-second Gideon-produced explainer video (Blast Video dogfood).
6. Failure states in human words: "Facebook said no. This usually means you're not an admin of your business page. Want Mia to walk you through fixing it?"

**Where it appears:**
- Client dashboard nav (permanent)
- Onboarding step 2 (right after Business Profile form in the pipeline bridge) — replace the stub task's dead URLs with real hub links
- Post-purchase email: "One last step — connect your accounts (takes 3 minutes)"

---

## 4. BACKEND SPEC (Foundation)

### Supabase — new table
```sql
CREATE TABLE client_connections (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  client_id UUID NOT NULL REFERENCES clients(id),
  provider TEXT NOT NULL,            -- 'meta' | 'google' | 'microsoft' | 'ghl_social' | 'stripe' | ...
  provider_scope TEXT,               -- 'gmail' | 'calendar' | 'business_profile' | 'pages' ...
  external_account_id TEXT,          -- page ID, email address, GHL location id, etc.
  display_name TEXT,                 -- "@bakerellas" / "john@bakerellas.com"
  status TEXT DEFAULT 'pending',     -- pending | connected | expired | revoked | error
  access_token_encrypted TEXT,       -- pgsodium/Vault encrypted — NEVER plaintext
  refresh_token_encrypted TEXT,
  token_expires_at TIMESTAMPTZ,
  last_verified_at TIMESTAMPTZ,
  error_detail TEXT,
  UNIQUE (client_id, provider, provider_scope, external_account_id)
);
ALTER TABLE client_connections ENABLE ROW LEVEL SECURITY;
-- RLS: clients see only their own rows; service role full access.
```

### Foundation API endpoints
```
GET  /connections/{client_id}            → card states for the hub (no tokens ever returned)
POST /connections/{provider}/initiate    → returns official OAuth authorize URL (with state nonce)
GET  /connections/callback/{provider}    → token exchange, encrypt, store, close popup
POST /connections/{id}/disconnect        → revoke + mark revoked
POST /connections/{id}/verify            → live token health check (used by nightly cron)
```

### Agent access layer
Agents NEVER read tokens directly. New Foundation module `connection_broker.py`:
`broker.send_email(client_id, ...)`, `broker.post_social(client_id, platform, ...)`, `broker.create_event(client_id, ...)` — the broker resolves the token, refreshes if needed, executes, and logs to `agent_actions`. If a required connection is missing, the agent's reply to the client is scripted: *"I need access to your [Gmail] first — tap Connect Your Accounts in your dashboard and I'm ready in 3 minutes."* Every agent (Nathan, Esther, Naomi, Rahab, Silas, Lydia) gets this fallback line added to its system prompt.

### Nightly health cron (Render)
Verify all `connected` tokens; flip broken ones to `expired`; fire a GHL SMS/email: "Quick fix needed — reconnect your Facebook (1 click)."

---

## 5. ROLLOUT PHASES

| Phase | Ships | Effort |
|---|---|---|
| 1 | Hub page UI + `client_connections` table + Google OAuth (Gmail + Calendar) + GHL social deep-link cards + Stripe Connect link | 2–3 days |
| 2 | Microsoft OAuth, popup polish, health cron, agent fallback lines, voice-guided helper | 2 days |
| 3 | Reconnect flows, Rahab review-platform cards, onboarding-pipeline stub replacement | 1–2 days |
| 4 | Aggregator (Ayrshare or similar) for long-tail platforms — only when a client demands one | on demand |

---

## 6. CLAUDE CODE KICKOFF PROMPT

```
Repos: Foundation (jjcesare86-CLE/Foundation) + the AN client dashboard frontend.

Build the "Connections Hub" per CONNECTIONS_HUB_BUILD.md:

1. Supabase: create client_connections table exactly as specced (Part 4),
   with RLS and encrypted token columns via Supabase Vault/pgsodium. Read the
   live schema first to reference the correct clients table PK.

2. Foundation API: implement the five /connections endpoints. Google OAuth
   first (reuse the working signInWithOAuth pattern from Blast Video, but as
   a standard authorization-code flow with offline access for refresh
   tokens; scopes: gmail.send, calendar.events). Encrypt tokens at rest.
   NEVER return tokens in any API response.

3. Frontend: /dashboard/connections page per the UX spec in Part 3 — card
   grid, one Connect button per card, popup OAuth, live status states,
   progress banner, plain-English copy exactly as written. GHL social cards
   deep-link into the client's GHL subaccount social integration page
   (location ID lives on the client record from the pipeline bridge).
   Stripe card links to a Stripe Connect onboarding session.

4. connection_broker.py: agent-facing access layer per Part 4. Add the
   missing-connection fallback line to Nathan, Esther, Naomi, and Lydia
   system prompts.

5. Replace the dead auth.automaitionnation.com stub URLs in
   an-sales-pipeline/onboarding/teams/social_media.py with real hub links:
   {dashboard_url}/dashboard/connections?client={id}.

6. Render cron: nightly token health check per Part 4.

Do not build custom Meta/TikTok OAuth apps — GHL carries those in v1.
```

---

**Open items for John:**
1. Confirm your GHL agency plan's white-label level — determines whether GHL social connect can be iframed/branded or must open in a new tab.
2. Google Cloud Console: the Connections Hub needs its own OAuth client (separate from Blast Video's) with gmail.send + calendar scopes; sending email on clients' behalf will require Google's app verification for sensitive scopes — start that submission early, it can take 1–2 weeks.
3. Phase 4 aggregator: want me to do a proper Ayrshare vs. Nango vs. Composio comparison when we get there, or park it?
