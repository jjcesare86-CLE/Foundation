# SWITCHBOARD — ADDENDUM E: WORK ROOMS

> **DATABASE (Oct 22, decided by John):** every `sb_*`, `ptt_*`, `work_room*` and `connected_agent*` table in this document lives in the **dedicated Switchboard Supabase project**, not Foundation. `workspace_id`/`client_id` references point to `sb_workspaces(id)` (mirror of Foundation `clients.id`). See `SWITCHBOARD_ADDENDUM_F_SEPARATE_DATABASE.md`.

**Live rooms for 2+ people — talk, share a screen, share documents — so the office, warehouse and field can handle one thing together, at the same time.**
v1.0 · Oct 13, 2026 · Extends `SWITCHBOARD_BUILD.md`, `SWITCHBOARD_ADDENDUM_A_LIVE_PTT.md` (shares its media infrastructure), Addenda B, C, D
Runs as item **P** in `02_BUILD_ORDER.md`. **Scheduled before launch (decision Oct 13).** Reference UI: `demo/switchboard-demo-v13.html`.

---

## E.1 WHAT IT IS

A **Work Room** is a live session inside Switchboard. Two or more teammates join one room and can see and hear each other, share a screen, put a document in front of everyone, and chat alongside. It exists for the moment a job needs *several departments looking at the same thing together* — the office has the quote, the warehouse has the stock, the field has the roof, and none of them can resolve it by trading messages.

Three things already in Switchboard make this better than a generic video call:
1. **It's already on the board.** One click from any conversation or Team; no link-pasting, no separate app, no meeting ID. Everyone's already authenticated and workspace-scoped.
2. **It speaks every language.** Live captions render in each person's own language using the existing translation layer (E.5).
3. **It leaves a record.** The room ends with a transcript, a summary, the documents shown, and action items posted back into the thread — through the same approval and receipt rules as everything else.

**Naming.** Existing violet **Teams** (`RM-##`) are persistent *chat* rooms. A **Work Room** is a *live session*. Chip `WR-##`, hue **teal** (`#1B9AAA` day / `#4FC3D1` night), shown in the Teams group with a **LIVE** badge and a head-count while active ("Hanson fascia job · 3 in the room"). A Work Room can be started from a Team (it then links to that Team's thread) or from a 1:1 conversation.

---

## E.2 V1 FEATURES (what ships) AND WHAT DOESN'T

| In v1 | Notes |
|---|---|
| Voice + video, 2–12 people | Adaptive quality; **audio-first low-bandwidth mode** for the field (video off, voice stays clear on weak LTE). |
| Screen share (desktop web) | Whole screen or one window. One presenter at a time; host can hand off. |
| Camera share on mobile ("show the roof") | Rear camera with a flip button. **Screen share from phones is view-only in v1** — iOS broadcast extensions and Android MediaProjection are their own work (v2). |
| Document sharing | Upload or drag in PDF / images / Office files → rendered as pages for everyone, presenter-synced page turns, a shared pointer, download for those with permission. Documents shown are saved with the room. |
| In-room chat | Same message system; saved to the room's record and, optionally, the linked Team's thread. |
| Host controls | Mute, remove, lock room, end for all, hand presenter role. Host = starter; owner/admin can always end a room. |
| Join from board / phone / email invite | Members: one click. **Guests** (an outside supplier or customer): single-use invite link, expiry (default 24 h), no board access, no history, and a banner telling every participant a guest is present. |
| Live translated captions | Phase P3 (E.5). |
| AI note-taker | Phase P3 (E.6). |
| Optional recording | Phase P4; off by default, consent banner (E.7). |

**Not in v1:** co-editing documents in the room (view/annotate-by-pointer only), a whiteboard, breakout rooms, webinars/large events (>12), AI teammates *speaking* in a room, calendar scheduling (rooms are ad-hoc and "start now"; scheduling comes through Naomi in v2), PSTN dial-in (phone number to join audio — v2; clients with VAPI could get it cheaply later), connected agents (Addendum D) inside rooms.

---

## E.3 BUILD, DON'T REVERSE-ENGINEER — INFRASTRUCTURE DECISION

**Recommendation: build Work Rooms on LiveKit** — the same open-source (Apache-2.0) WebRTC SFU already being evaluated for live PTT (item L). One media infrastructure serves PTT channels, Work Rooms and mobile; it provides rooms, tracks, screen share, data channels, adaptive streaming, server SDKs and client SDKs for web, iOS and Android. Run LiveKit Cloud first (zero ops), self-host on a VM when volume justifies it.

**About the repository you're planning to download.** Before any code from it enters Foundation:
- **Do not use anything that reverse-engineers Zoom's (or any vendor's) proprietary client, protocol or SDK internals.** It is a terms-of-service and copyright problem (and in some jurisdictions anti-circumvention law), it breaks whenever the vendor ships an update, and a customer-facing product built on it can be shut down or sued over. A product we resell cannot rest on that.
- **Using a repo to learn *how Zoom-style rooms are organized* (UI layout, features, call flow) is fine.** Rebuilding the behavior on WebRTC/LiveKit is also fine — that is what every competitor does.
- **Checked: `morluto/rea` ("Reverse Engineer Anything", MIT).** It is a general-purpose reverse-engineering toolkit (an MCP/CLI that decompiles binaries, Electron/JS apps, APKs, WASM and so on). It is **not** a meeting app and contains nothing about WebRTC or screen sharing, so it gives us no code to build rooms from. The MIT license covers the tool itself; it does not make it acceptable to point it at Zoom's (or anyone's) proprietary client to copy how it works. Use it, if at all, for legitimate analysis of software we own or have rights to. Work Rooms are built on LiveKit.
- Any repo that's an **independent open-source meeting app** (WebRTC-based) is fair game as a reference *if* its license is permissive (MIT / Apache-2.0 / BSD). Check the license file first; AGPL/GPL code cannot be copied into a closed product. Send me the repo URL and I'll review its license and structure before you pull anything in.
- Alternatives worth comparing against LiveKit: Jitsi Meet (Apache-2.0; heavier, opinionated UI), mediasoup (build-it-yourself SFU; more engineering), and hosted APIs such as Daily or Twilio Video (fastest, per-minute cost, vendor dependency). LiveKit wins on fit with PTT, mobile SDKs, and cost control.
- **Marketing never says "Zoom."** Describe the capability ("video rooms, screen share, documents"), not the competitor.

---

## E.4 DATA MODEL (migration `0xx_work_rooms.sql`, idempotent, RLS on every table)

```sql
CREATE TABLE IF NOT EXISTS work_rooms (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  workspace_id UUID NOT NULL REFERENCES sb_workspaces(id),
  code TEXT NOT NULL,                       -- WR-## per workspace
  title TEXT NOT NULL,                      -- "Hanson fascia job"
  started_by UUID NOT NULL,
  linked_thread_id UUID,                    -- the Team / conversation it was started from
  livekit_room TEXT NOT NULL UNIQUE,        -- opaque, never user-visible
  status TEXT NOT NULL DEFAULT 'live' CHECK (status IN ('live','ended')),
  allow_guests BOOLEAN DEFAULT FALSE,
  recording_state TEXT DEFAULT 'off' CHECK (recording_state IN ('off','on')),
  started_at TIMESTAMPTZ DEFAULT NOW(),
  ended_at TIMESTAMPTZ,
  summary_message_id UUID                   -- the post-room summary in the thread
);
CREATE TABLE IF NOT EXISTS work_room_participants (
  room_id UUID NOT NULL REFERENCES work_rooms(id),
  workspace_id UUID NOT NULL,
  user_id UUID,                             -- null for guests
  guest_label TEXT,                         -- "Supplier rep — Dave" (host-entered, shown to all)
  role TEXT NOT NULL DEFAULT 'member' CHECK (role IN ('host','member','guest')),
  joined_at TIMESTAMPTZ DEFAULT NOW(), left_at TIMESTAMPTZ,
  device TEXT,                              -- web | ios | android
  PRIMARY KEY (room_id, workspace_id, joined_at)
);
CREATE TABLE IF NOT EXISTS work_room_guest_invites (
  token_hash TEXT PRIMARY KEY, room_id UUID NOT NULL REFERENCES work_rooms(id),
  workspace_id UUID NOT NULL, label TEXT, expires_at TIMESTAMPTZ NOT NULL, used_at TIMESTAMPTZ
);
CREATE TABLE IF NOT EXISTS work_room_artifacts (       -- documents shown in the room
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY, room_id UUID NOT NULL REFERENCES work_rooms(id),
  workspace_id UUID NOT NULL, uploaded_by UUID, filename TEXT, mime TEXT, storage_path TEXT,
  downloadable BOOLEAN DEFAULT TRUE, created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS work_room_transcript (       -- text only; audio is not stored unless recording is on
  id BIGSERIAL PRIMARY KEY, room_id UUID NOT NULL REFERENCES work_rooms(id), workspace_id UUID NOT NULL,
  speaker_user_id UUID, lang TEXT, text TEXT, t_offset_ms INT, created_at TIMESTAMPTZ DEFAULT NOW()
);
-- RLS: workspace_id = auth.jwt()->>'workspace_id' on all five. Guest tokens are a separate role that can
-- read/write ONLY their own room's live channel, never any workspace table.
-- Eden threads cannot spawn a Work Room. A Work Room never exposes any thread other than its own linked one.
```

Recordings (P4) go in the workspace storage bucket with `expires_at = now() + 30 days` (matches the standing audio retention decision; transcripts persist).

---

## E.5 LIVE CAPTIONS IN EVERYONE'S LANGUAGE (the differentiator — P3)

Pipeline per speaker: audio track → streaming speech-to-text (speaker's declared language) → partial/final segments → the existing **Haiku translation pass** (FAST tier; cached by segment+language) → each participant's client shows captions in *their* `lang`, with a "show original" toggle. Final segments land in `work_room_transcript`.

- Cost control: captions are **opt-in per participant** (default on only when a participant's language differs from the speaker's); translate once per target language per segment, not once per viewer.
- Never translate: numbers, addresses, part numbers, names — keep them verbatim (same rule as B.3).
- Honest limits: captions can be wrong on noisy job sites and heavy accents; label them "auto-captions," and keep the original audio authoritative.

---

## E.6 AI TEAMMATES IN A WORK ROOM (P3)

- **Invite an AI as a note-taker** (e.g., Nehemiah, Silas) — a participant `WR`-side bot that **listens to captions only** (it consumes `work_room_transcript`, not raw audio) and never speaks in v1.
- At end of room it posts to the linked thread: summary, decisions, **proposed action items** as action-library cards. Items execute only after a human approves, and carry normal Proof-of-Work receipts. The summary is clearly labeled AI-generated and links the transcript.
- Conversation Discipline applies: items the room left unresolved are written to `open_items` so they are restated later.
- **First-party agents only** in v1. Connected agents (Addendum D) are not allowed in Work Rooms.

---

## E.7 SECURITY, PRIVACY, CONSENT

1. **Workspace-bound tokens.** Foundation mints a short-lived (≤10 min), single-room LiveKit token only after checking membership/role. The LiveKit API secret never leaves the server. Room names are opaque.
2. **Guests are fenced.** Single-use invite, expiry, can't see the board or any history, labeled to all participants, can't present until the host allows it, removed on end. No guest in a room whose linked thread is Eden or marked confidential.
3. **Screen share is a deliberate act.** Browser permission prompt plus an always-visible "You are sharing" bar; host can stop any share. Documents are scanned (type allowlist, size cap, AV scan) before render.
4. **Recording needs consent.** Off by default; starting it shows a banner to everyone and plays a notice; participants who object can leave, and the room records only after the host confirms. Retention 30 days for recordings, transcripts persistent. Some jurisdictions require all-party consent — the banner stays up for the whole recording and the product copy tells the owner to check local rules.
5. **Eden** can never start, join or be summarized by a Work Room. **PTT** and Work Rooms are separate channels; ending a room does not touch PTT.
6. **Rate / abuse limits.** Per-workspace concurrent-room cap and monthly participant-minute cap by plan; auto-end an empty room after 10 minutes; max room age 8 hours.
7. **Audit.** Join/leave/share/record events logged per room for owner/admin export.

**Tests that must exist before ship:**
- Workspace-B member cannot get a token for, list, or see participants of a workspace-A room (3 seeded workspaces).
- An expired or reused guest invite is refused; a guest token cannot read any `sb_*` table.
- Token for room X cannot join room Y; tokens expire within 10 minutes.
- A guest cannot present until promoted; host "stop share" ends a share within 2 s.
- Eden thread: no Work Room can be created from it.
- Recording refuses to start without the host's confirmation; stored object carries a 30-day expiry.
- Caption for a number/address segment is passed through verbatim.
- Empty room auto-ends after 10 minutes.

---

## E.8 UX (matches the board; see `demo/` once v13 exists)

- **Start:** a video icon in every chat window header and Team header → "Start a Work Room" (title prefilled from the thread, invitees prechecked from the thread's people). Also **"Start from a job"** where Silas dispatch data exists.
- **Invite:** selected teammates get a ringing row on their board and a push on mobile; anyone else can be added mid-call by name.
- **Window:** it opens as a docked window like any chat (consistent with the stacked-column behavior), with an **Expand** button to go full-screen: video tiles, a presenter stage, a documents tray, captions, chat. A teal bar on the dock shows you're in a room from anywhere.
- **Field mode (phone):** big Mute / Camera-flip / Leave buttons, audio-first by default, a "Show them" button that switches to the rear camera.
- **End of room:** one card in the thread — who was there, how long, documents shown, summary, proposed action items.

---

## E.9 COST AND PACKAGING (John to confirm)

- Media cost scales with **participant-minutes** (and with recording/transcription minutes). Meter `work_room_minutes` per workspace in `llm_usage`-style usage rows so the plan page can show "212 of 1,000 room-minutes."
- **SUPERSEDED Oct 23 (John): Work Rooms have no separate price; see Addendum G (seats + fair use).** Earlier suggestion, kept for history: **Work Rooms as a Switchboard add-on** (included minutes per seat; overage per participant-minute), with captions and AI note-taker as the premium tier of the add-on because they carry real STT/LLM cost. Final numbers after P1 load tests give actual cost per participant-minute — do not publish pricing before that.
- Cloud first, self-host when monthly media spend passes the cost of one small media-server VM plus an hour of ops a week.

---

## E.10 PHASES

| Phase | Ships | Size |
|---|---|---|
| **P0** (inside I) | `WR` chip + teal hue + LIVE badge in the front-end; `sb_participants.kind` accepts `workroom`; no media yet | S |
| **P1** | LiveKit wiring, token minting, work_rooms tables, voice+video+chat, host controls, screen share (desktop), board integration, concurrency/minute metering, tenancy tests | L |
| **P2** | Document sharing (render, page sync, pointer, save to room), mobile (camera share, audio-first, view-only screen), guest invites, low-bandwidth mode | L |
| **P3** | Live translated captions, transcript table, AI note-taker + action items | L |
| **P4** | Recording with consent + 30-day expiry, export | M |
| **v2** | Co-editing, whiteboard, phone screen-share, PSTN dial-in, scheduling via Naomi, AI speaking in rooms, >12 participants | — |

Dependencies: **P1 stands on its own — it does not wait for L.** Create the LiveKit project at P; item L (PTT) then reuses the same project and server SDK wiring. The mobile parts of P2 need K's Capacitor shell, so build P1 and the web parts of P2 first, then the mobile parts alongside K.

---

## E.11 CLAUDE CODE PROMPT — item P

Paste the session header (`01_PROJECT_REF_CORRECTION.md`) first, then:

```
Foundation repo, branch switchboard-work-rooms. Same GLOBAL RULES as the Batch 1
master prompt (CLI migrations, live-schema introspection, gates, no secrets,
protected areas: Eden isolation, tier gating, public.ai_employees, the AN
database). Read docs/specs/SWITCHBOARD_ADDENDUM_E_WORK_ROOMS.md fully, plus
Addenda A (PTT infra), C (tenancy) and D (connected agents — they are NOT
allowed in rooms).

Infrastructure: LiveKit (Cloud first). Read keys from env (LIVEKIT_URL,
LIVEKIT_API_KEY, LIVEKIT_API_SECRET); refuse to boot the feature if missing;
never log or return the secret. Do not copy code from any third-party repo
without checking its license is MIT/Apache-2.0/BSD; do not use anything that
reverse-engineers a vendor's proprietary client or protocol.

P0 — verify it shipped in item I; if not, add the WR chip/teal hue/LIVE badge
and the 'workroom' participant kind.
P1 — migrations from E.4 (RLS on all); token-mint endpoint (<=10 min, single
room, membership check); create/join/end endpoints; web room UI: video, audio,
chat, host controls, desktop screen share with the "You are sharing" bar;
board integration (start from chat/Team header, ringing row, LIVE badge,
head-count); usage metering; auto-end empty rooms; room age cap.
  Gate: every test in E.7 that applies to P1 passes; two real browsers in one
  room with audio, video and screen share; paste outputs.
P2 — documents (type allowlist, size cap, AV scan, render pages, presenter-
synced page turns, pointer, saved to work_room_artifacts); mobile Capacitor
room (audio-first, rear-camera share, view-only screen); guest invites with
expiry/single-use and the guest fence.
P3 — captions via streaming STT + the existing translation pass (cache per
segment+language, numbers/addresses verbatim); transcript table; AI note-taker
that consumes transcript only and posts a summary + proposed action-library
cards through the normal approval + receipt flow; open_items for unresolved
items.
P4 — recording with host-confirmed consent banner, 30-day expiry, export.

Do NOT: store raw audio unless recording is on; let any guest touch sb_* tables;
allow Eden or connected agents in a room; add any competitor's name or logo to
code, copy or UI; publish pricing.

Finish with a completion report, load-test numbers (cost per participant-minute
at 4, 8 and 12 participants), and a list of anything needing John.
```

---

## E.12 DECISIONS FOR JOHN (defaults chosen so you can proceed)

| # | Decision | Default |
|---|---|---|
| 1 | Infrastructure | LiveKit Cloud now, self-host later. |
| 2 | The repo you're downloading | Send me the URL; I'll check license and what it actually does before anything is used. Default: reference only. |
| 3 | In launch or after? | **DECIDED Oct 13 (John): in launch.** Build P0–P3 (web + mobile + captions + AI note-taker) before launch; P4 recording last but also pre-launch if time allows. LiveKit is set up at P, not L; L reuses it. |
| 4 | Guests allowed? | Yes, host-invited, single-use, 24 h, labeled; off for confidential threads. |
| 5 | Packaging | **DECIDED Oct 23 (John): no separate price.** Included in the seat price with pooled fair use; groups and rooms start inside conversations (Addendum G). |
| 6 | Recording | Ship last (P4), off by default; still inside the launch scope. |
