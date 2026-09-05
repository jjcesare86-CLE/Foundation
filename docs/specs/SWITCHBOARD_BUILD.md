# SWITCHBOARD — FLOATING AI EMPLOYEE MESSENGER
**Build spec v1.0 · The AIM-style buddy list for all 34 employees, embeddable everywhere**
Drop into docs/specs/ · Depends on: llm_router, prompt store, action library (Batch 1), connection_broker; benefits from Modules 2–4 (voice/playbook, interview, sliders)

---

## 1. LOCKED DECISIONS (from John)
1. **Lives everywhere:** AN, AssistMIO, VoiceMIO, Blast Video, MRLIN dashboards AND client sites (Exterior Rescue, Broker Broker, SAS, LUTS, Delivered Fireworks…). → It must be ONE embeddable widget served from Foundation, not five re-implementations.
2. **Buddy list = client-curated pins + full directory with locked agents as upsell.** Locked agents appear grayed with a lock; tapping one runs the standard pricing logic (< $5K shows real pricing/checkout; ≥ $5K routes to the voice sales flow).
3. **v1 = text chat + a voice call button per agent.**

**One assumption to confirm:** Switchboard is for AUTHENTICATED users (the business owner + their staff) — their employee roster, their data. Public site visitors keep the existing public-facing widgets (Mia orb, Sara, Roxy, etc.). If you also want a public-visitor version of Switchboard later, that's a v2 flag, not a v1 redesign.

## 2. UX SPEC

### 2.1 Collapsed state — the FAB
Floating avatar button, bottom-left (configurable corner), draggable, remembers position. Shows the product's default agent (AN → Nehemiah, AssistMIO → Celeste, client sites → their lead agent) with an unread badge counting all agents' unread messages. Long-press/right-click → "Hide Switchboard" (restore path: dashboard toggle). State persists per user.

### 2.2 Expanded state — the buddy list (the AIM moment)
Slide-out panel (desktop ~320px; mobile bottom sheet):
- **Pinned** (client-curated, drag-to-reorder): avatar, name, role one-liner, presence line, unread badge.
- **Presence is REAL, not decorative:** green = idle/ready; working = live status from agent_jobs heartbeats ("Silas · building tomorrow's dispatch", "Elijah · crunching this week's numbers"); amber = needs a connection (deep-links Connections Hub). Never fake-offline — employees don't sleep; that's the product.
- **Directory ("All employees")** below, grouped by department: every roster agent. Unlocked = "Add to buddy list." Locked = grayed + lock badge + one-line value prop; tap → pricing logic (Magdalene's negotiation tier rules apply). New-agent releases appear here automatically = perpetual merchandising shelf.
- Search bar ("who handles invoices?" — matches name, role, and handles[] keywords).

### 2.3 Chat window
Opens like a DM (desktop: up to 2 stacked windows; mobile: full-screen sheet):
- Header: avatar, name, role, presence, **call button** (phone icon), minimize/close.
- Persistent history per agent per user (this is a real relationship, not a session).
- **Proactive messages land here as unread DMs** — this is the killer wiring: Rahab's "review response ready — approve?", Elijah's Monday scoreboard, Silas's weather alert, Joanna's "invoice paid." The approval inbox BECOMES the message thread: approve/dismiss buttons render inline as action-library actions. One surface, everything.
- **Handoffs are visible and warm:** when Caleb redirects ("that's Miriam's lane"), the thread shows "Caleb added Miriam" and Miriam's window opens with context carried over (last N messages + a router-generated brief). Feels like a great team, demos like magic.
- Typing indicator during generation; message states (sending/delivered/error+retry).

### 2.4 Voice call button
- v1: launches a VAPI web call scoped to that agent (assistant/squad member per agent, standard voice stack; migrate to the gemini voice proxy when deployed — same button, swapped backend).
- In-call: chat window shows live "on a call" state; post-call, the transcript summary posts INTO the same thread ("Here's what we covered…") so voice and text are one continuous history.
- Locked agents: call button hidden (voice is an unlocked-only privilege).

## 3. ARCHITECTURE

### 3.1 Embed
- Single script tag, served from Foundation:
  `<script src="{foundation}/switchboard/v1.js" data-tenant-key="pk_..." defer></script>`
- **Shadow DOM** container — zero CSS bleed on client sites. Internally React, compiled to one self-contained bundle (no external deps at runtime).
- Auth: the host page passes a short-lived session token (dashboard SDK helper) → Switchboard exchanges for a scoped Switchboard JWT (client_id + user_id + entitlements). No token = Switchboard doesn't render. Entitlements resolve which agents are unlocked (tier gating stays in platforms/pricing engine — Foundation serves the full roster + the entitlement mask).

### 3.2 Backend (Foundation API)
```
GET  /switchboard/bootstrap        → roster + entitlement mask + pins + unread counts + presence
GET  /switchboard/threads/{agent}  → paged history
POST /switchboard/threads/{agent}/messages   → user message; SSE/stream reply
POST /switchboard/pins             → add/remove/reorder
POST /switchboard/calls/{agent}    → mint VAPI web-call session for that agent
WS/SSE /switchboard/events         → presence updates, proactive message pushes, unread deltas
```
Message path: Switchboard message → prompt composer (agent prompt + brand voice + operational params + thread memory window) → llm_router (agent's tier) → reply; actions render from the action library; all logged to llm_usage (per-agent, per-client — the "always billable/accountable" trail, and plan-level metering hooks live here).

### 3.3 Migrations
```sql
CREATE TABLE sb_threads (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  client_id UUID NOT NULL REFERENCES clients(id),
  user_id UUID NOT NULL,
  agent_slug TEXT NOT NULL,
  last_message_at TIMESTAMPTZ,
  unread_count INT DEFAULT 0,
  UNIQUE (client_id, user_id, agent_slug)
);
CREATE TABLE sb_messages (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  thread_id UUID NOT NULL REFERENCES sb_threads(id),
  sender TEXT NOT NULL,            -- user | agent | system
  kind TEXT DEFAULT 'text',        -- text | action_request | action_result | handoff | call_summary
  body TEXT,
  action_id UUID,                  -- links action-library rows for inline approve/dismiss
  created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE TABLE sb_pins (
  client_id UUID NOT NULL REFERENCES clients(id),
  user_id UUID NOT NULL,
  agent_slug TEXT NOT NULL,
  sort_order INT DEFAULT 0,
  PRIMARY KEY (client_id, user_id, agent_slug)
);
CREATE TABLE sb_settings (
  client_id UUID NOT NULL REFERENCES clients(id),
  user_id UUID NOT NULL,
  corner TEXT DEFAULT 'bottom-left',
  hidden BOOLEAN DEFAULT FALSE,
  default_agent TEXT,
  PRIMARY KEY (client_id, user_id)
);
-- RLS: user-level isolation (stricter than client-level — staff don't read the owner's DMs).
-- Eden exception: eden threads get an extra policy — owner/admin roles CANNOT read
-- other users' eden threads under any role. Privacy isolation extends into Switchboard.
```

### 3.4 Guardrails
- Thread memory window per tier (e.g. last 30 messages + rolling summary) — Switchboard chats must not silently become 1M-token bills; long-context synthesis stays Solomon's scheduled job, not casual DMs.
- Rate limits per user per hour by plan; friendly "let me catch my breath" message at cap.
- Locked-agent taps NEVER fake capability: the lock card sells, it doesn't chat.
- Proactive messages: max 1 unsolicited thread-opener per agent per day (alerts/approvals exempt) — Switchboard must never feel like notification spam.

## 4. ROLLOUT
| Phase | Ships |
|---|---|
| 1 | Widget core (FAB, buddy list, pins, directory + lock states), bootstrap/threads/messages endpoints, AN dashboard embed, Nehemiah default |
| 2 | Proactive/unread pipeline (action library → DMs), presence from agent_jobs, handoff windows |
| 3 | Voice call button (VAPI web sessions per agent, call summaries into thread) |
| 4 | Embeds: AssistMIO, VoiceMIO, Blast Video, MRLIN; then client sites (Exterior Rescue first — staff dashboard already exists) |
| 5 | Upsell flow polish: lock-tap → pricing/checkout (<$5K) or sales voice flow (≥$5K), new-agent release announcements in directory |

## 5. CLAUDE CODE PROMPT
```
Foundation repo, branch foundation-dock. Same GLOBAL RULES as the Batch 1
master prompt (CLI migrations, live-schema introspection, gates, no secrets,
protected areas). Read docs/specs/SWITCHBOARD_BUILD.md fully. Execute
Phases 1→5 in order with a verify gate per phase:
- P1 verify: Switchboard renders in AN dashboard inside Shadow DOM with zero style
  bleed; send/receive works for 3 different agents with per-agent history;
  entitlement mask correctly locks a non-plan agent; RLS blocks cross-user
  thread reads (test it).
- P2 verify: an approval-inbox action (Rahab draft) appears as an unread DM
  with working inline approve; agent_jobs heartbeat changes presence line;
  a Caleb→Miriam handoff opens Miriam's window with carried context.
- P3 verify: call button mints a live VAPI session; post-call summary posts
  into the same thread.
- P4 verify: script-tag embed on the Exterior Rescue staff dashboard works
  with their auth and their agent roster.
- P5 verify: locked-agent tap under $5K opens checkout with correct pricing
  engine values; ≥$5K routes to the sales voice flow.
- Eden check at every phase: eden threads unreadable by any other role.
Finish with a completion report + a one-page EMBED_GUIDE.md for adding the
Switchboard to any future product in under 5 minutes.
```

## 6. NAME (John's pick, cosmetic)
Internal: Switchboard. Client-facing label options: **"Your Team"** (safe, clear) · **"The Office"** (fun) · **"Team Chat"** (plain). Recommend "Your Team" — a fifth grader knows exactly what it is.

---

## ADDENDUM B — PERSONALIZATION + LANGUAGE (added Sep 2, 2026; reference: demo/switchboard-demo-v11.html)

### B.1 What each person can set (profile sheet, click your own name)
- Display name, optional title, status (Available / Away / Busy), away message, phone number.
- **Bubble color** — seven presets drawn from the mark plus a custom picker. Applies to their own outgoing bubbles, their avatar, the Send button, and the active-row indicator. Text color auto-flips to ink or white for contrast. Stored per user in `sb_settings` (`bubble_color TEXT`).
- **Language** — the language they read in. Default from the browser; stored in `sb_settings` (`lang TEXT`).
- **AI voice** — which voice AI teammates use when calling or reading to them. Maps to the VAPI/voice-proxy voice id; stored in `sb_settings` (`voice_id TEXT`).
- Day / night.

Nothing here changes what *other* people see except the away message and the phone-reachability state. Bubble color is the AIM-profile nostalgia done honestly: yours is yours, on your screen.

### B.2 Color language across the product (fixed, not user-set)
Copper = AI teammates. Cobalt = people. Violet = rooms. The same mapping carries the ID chips, avatars, window headers, and incoming bubbles, so a person learns it once. Night mode is navy from the lettering, never grey.

### B.3 Translation layer — this is backend work, not a client toggle
The demo shows the behavior; the real thing is a router pass:
- Every message stores `body` (as written) and `lang_src`. On read, if `reader.lang != lang_src`, the API returns `body_rendered` translated via `llm_router` FAST tier (Haiku 4.5), cached per `(message_id, lang)` in a new `sb_message_renderings` table so a message is translated once per language, not once per read.
- The client shows the rendering with a one-tap "show original" link; the original is never hidden. Action buttons are translated by the same pass.
- Outgoing messages are sent as written; the *recipient's* language preference drives their rendering. A Spanish-speaking crew lead and an English-speaking owner each read the same thread in their own language.
- Dictation (`SpeechRecognition.lang`) and the voice stack follow the same `lang` setting.
- Receipts, IDs, timestamps, and numbers are never translated.
- Cost is negligible at FAST-tier rates; still meter it under `llm_usage.task_type='sb_translate'`.

**Migrations (add to Phase 1 of this spec):**
```sql
ALTER TABLE sb_settings ADD COLUMN IF NOT EXISTS bubble_color TEXT DEFAULT '#B4672B';
ALTER TABLE sb_settings ADD COLUMN IF NOT EXISTS lang TEXT DEFAULT 'en';
ALTER TABLE sb_settings ADD COLUMN IF NOT EXISTS voice_id TEXT;
ALTER TABLE sb_messages ADD COLUMN IF NOT EXISTS lang_src TEXT DEFAULT 'en';
CREATE TABLE IF NOT EXISTS sb_message_renderings (
  message_id UUID NOT NULL REFERENCES sb_messages(id),
  lang TEXT NOT NULL,
  body_rendered TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  PRIMARY KEY (message_id, lang)
);
```

---

## ADDENDUM C — TENANCY: ONE BOARD PER BUSINESS, CLOSED BY DEFAULT (added Sep 2, 2026)

### C.1 The rule
A **workspace** is a business. Every Switchboard row — threads, messages, pins, settings, rooms, PTT channels, transmissions, receipts — carries the workspace key (`client_id`, already on every table in this spec) and is isolated by RLS. A person sees only the people, agents, and rooms in the workspace their session is scoped to. **There is no global directory, no cross-workspace search, no way to address a user by email or handle outside your own board.** Marcus at Exterior Rescue cannot see, find, or message anyone at LUTS, and nothing an admin can toggle changes that in v1.

This is stated as a product rule, not just a schema detail, because it's what makes Switchboard sellable to a business owner: their team is *their* team.

### C.2 What "the same agent" means across workspaces
The Foundation catalog (`foundation.ai_employees`) is shared — Silas is one definition. But each workspace gets its **own instance**: its own threads with Silas, its own crews and jobs, its own receipts, its own action-library queue, its own PTT membership. Silas-for-Exterior-Rescue knows nothing about LUTS. Agent memory, playbooks, and brand voice are all keyed by workspace. The catalog answers "who is Silas"; the workspace answers "what has Silas done for us."

### C.3 Membership
```sql
CREATE TABLE IF NOT EXISTS sb_memberships (
  workspace_id UUID NOT NULL REFERENCES clients(id),
  user_id UUID NOT NULL,
  role TEXT NOT NULL DEFAULT 'member',      -- owner | admin | member | guest
  display_title TEXT,                        -- the optional title shown under their name, per workspace
  joined_at TIMESTAMPTZ DEFAULT NOW(),
  PRIMARY KEY (workspace_id, user_id)
);
```
- The Switchboard JWT is minted **per workspace**: `{user_id, workspace_id, role}`. Every query filters on `workspace_id` from the token, never from a request parameter. RLS policies reference `auth.jwt() ->> 'workspace_id'`.
- **One person, several boards.** A user may hold memberships in multiple workspaces (John: AN, LUTS, Delivered Fireworks). The app shows a workspace switcher; switching mints a new token. Notifications carry the workspace name so an alert from LUTS is never mistaken for AN. Threads never merge across boards.
- Invites are issued by an owner/admin of that workspace only; joining requires the invite. No self-serve "find my company."
- Removing a member revokes their token, hides them from the board immediately, and keeps their message history visible to the workspace (it's the business's record, not the individual's).

### C.4 Pins are references
`sb_pins` (already specced) holds `(workspace_id, user_id, target_ref, sort_order)`. A pin never moves anyone out of their department or the People list — the Pinned group is a per-user view rendered from the same rows. Demo v8 shows the behavior: hover a name for the pin, pinned people appear on top *and* in their category.

### C.5 What stays outside the board (v1)
- **Outside parties** — a customer, a subcontractor without an account, a supplier — do not join the board. Agents reach them the way they already do: SMS/email/voice through GHL and the connection broker, with the conversation logged into the workspace's thread. This keeps every external contact inside the receipt system without opening the board.
- **Public visitors** on a client site keep the public-facing widgets (Mia, Sara, etc.). Switchboard renders only for an authenticated member.

### C.6 Cross-workspace — deliberately v2
When two businesses that both use Switchboard need to work together (a roofer and a gutter sub, LUTS and a venue), the right shape is a **shared room**: created by one admin, accepted by the other, badged with both company names, containing only the people each side explicitly adds. AI agents never appear in a shared room unless their owning workspace's admin adds them, and their receipts stay in their home workspace. No DMs across boards; rooms only. Not in v1. Note it in the roadmap and in the sales conversation ("that's coming"), and don't build it until two paying clients ask.

### C.7 Tests that must exist before Switchboard ships
- A member of workspace A calling `/switchboard/bootstrap` with a token for A never receives any row from workspace B — asserted against seeded data for at least three workspaces.
- Attempting `/switchboard/threads/{agent}` with a `workspace_id` query parameter that differs from the token's is rejected (the parameter must not exist at all).
- Eden threads: unreadable by any other member of the same workspace, including the owner.
- Revoking a membership invalidates the token within one request cycle.

### B.4 Avatars and presence (added Sep 4)
- Initials are true initials: first letter of each name word; a single-name agent shows one letter.
- Profile photo upload per user: client-side crop to a square, resized to 96–192px, stored in Supabase Storage under the workspace bucket with the path on `sb_memberships.photo_url`. Photos are per workspace membership, not global. Fallback to initials whenever `photo_url` is null.
- Presence dot: green = available, yellow = busy/working, red = needs you, grey = away. Rendered with a 2.5px ring in the panel color plus a 1px contrasting halo so it stays legible on any tile color, including photos.
