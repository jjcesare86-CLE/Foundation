# DOCK NATIVE MOBILE — ADDENDUM A
**Live two-way PTT channels + shipping as customer-facing software**
v1.0 · Extends SWITCHBOARD_NATIVE_MOBILE_VOICE.md · Drop into docs/specs/

---

## 1. WHAT CHANGED

Two decisions, both of which move this from "a feature in Switchboard" to "a product with its own obligations":

1. **PTT goes two-way.** Not just talking into the app — hearing transmissions come back, live, through a Bluetooth headset. For crews on a roof and equally for someone at a desk with AirPods in.
2. **The app ships to clients.** App Store presence, Apple review on every update, support obligations, and a price that reflects all of it.

---

## 2. TWO DIFFERENT USERS, ONE CHANNEL MODEL

The desk case is not a smaller version of the crew case. They need opposite defaults.

| | Field crew | Desk with headset |
|---|---|---|
| Headset state | On for a job, off after | In their ears most of the day |
| Default listening | Monitor the crew channel all shift | Monitor selectively; silence during focus work |
| Talk trigger | Rugged handset PTT key, BT button, on-screen hold | Keyboard shortcut, BT button |
| Tolerance for chatter | High — it's how a crew works | Low — it's an interruption |
| What they most want to hear | Dispatch changes, weather calls | Their own name, and alerts that need a decision |

**Design consequence: monitoring is per-channel and opt-in, with a "just me" default for desk users.** A desk worker joins the channels they care about; a crew joins the shift channel and leaves it open. Nobody gets dropped into an open mic they didn't choose.

### 2.1 Channel model
```sql
CREATE TABLE ptt_channels (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  client_id UUID NOT NULL REFERENCES clients(id),
  name TEXT NOT NULL,                  -- "Storm response", "Crew 2", "Front office"
  kind TEXT DEFAULT 'team',            -- team | direct | broadcast
  linked_thread_id UUID,               -- Switchboard conversation this channel belongs to
  created_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE TABLE ptt_members (
  channel_id UUID NOT NULL REFERENCES ptt_channels(id),
  member_ref TEXT NOT NULL,            -- user_id for people, agent_slug for AI
  member_kind TEXT NOT NULL,           -- human | agent
  monitoring BOOLEAN DEFAULT FALSE,    -- opt-in listening; desk default false
  can_transmit BOOLEAN DEFAULT TRUE,
  PRIMARY KEY (channel_id, member_ref)
);
CREATE TABLE ptt_transmissions (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  channel_id UUID NOT NULL REFERENCES ptt_channels(id),
  sender_ref TEXT NOT NULL,
  started_at TIMESTAMPTZ DEFAULT NOW(),
  duration_ms INT,
  audio_ref TEXT,                      -- storage key
  transcript TEXT,                     -- posted into Switchboard thread
  delivered_to INT DEFAULT 0,          -- receipt: how many actually received it
  intended_for INT
);
-- RLS: client isolation, plus member-level read on transmissions.
```

**Every transmission posts its transcript into the linked Switchboard conversation.** That's the thing that makes this more than a radio: the voice traffic becomes searchable history sitting in the same thread as the text, and Elijah can report on it. `delivered_to` / `intended_for` is the Proof of Work receipt — "4 of 5 crew received; Ray was out of signal."

### 2.2 AI employees transmit too
This is the part no competitor has. Silas's weather call doesn't have to wait for someone to open an app — it comes through the crew's headsets in his voice while they're on a roof, and the transcript lands in the thread. Guardrails, because an AI that can talk in your ear unprompted needs limits:

- Agents transmit only on channels where they're an explicit member with `can_transmit`.
- Agent transmissions are rate-limited hard: **one unsolicited transmission per agent per channel per hour**, alerts and approvals exempt.
- Anything requiring a decision transmits a short version and drops the full detail plus action buttons into the thread. Nobody approves a budget change by voice on a ladder.
- A per-channel quiet mode a human can set, and agents respect it — with the same exemption for genuine safety items (weather cutoffs, a missed emergency call).

---

## 3. PLATFORM SPLIT FOR RECEIVE

Sending was mostly symmetric. Receiving is where iOS and Android diverge, and the plugin has to hide that.

**iOS:** Apple's PushToTalk framework is channel-based by design — join a channel, incoming transmissions play through the system audio path with the Dynamic Island indicator and Bluetooth PTT button support built in. That's exactly our model, which is fortunate, because Apple requires PTT apps to use it anyway.

**Android:** no system equivalent. We build it — the microphone foreground service extends to a persistent connection (WebRTC or a WebSocket audio path), audio playback through the media session, and the ongoing notification doubles as the channel indicator.

So `VoiceBridge` grows:
```
VoiceBridge.joinChannel(channelId, {monitor:boolean})
VoiceBridge.leaveChannel(channelId)
VoiceBridge.transmit(channelId)          // begin outgoing
VoiceBridge.endTransmit()
VoiceBridge.onIncoming(cb)               // {channelId, senderRef, audioStream}
VoiceBridge.setQuiet(channelId, until)
```
Server side this needs an audio relay. Start with a simple SFU (LiveKit or mediasoup) rather than building transport from scratch — PTT is low-bitrate, half-duplex, and forgiving, so the cheap tier is genuinely fine.

### 3.1 Contingency if Apple denies the entitlement
Plan for it. If `com.apple.developer.push-to-talk` is refused, iOS falls back to **live audio rooms** — a call, not a PTT channel, which needs no special entitlement. Worse UX (no hardware button, no locked-screen transmit, must be in the app) but the same underlying channels and relay, so nothing is wasted. Android keeps full PTT either way. Build the relay and channel model first; they're entitlement-independent.

---

## 4. SHIPPING AS CUSTOMER-FACING SOFTWARE

### 4.1 One app, not one per client
The tempting move is a white-labeled app per client. **Don't.** Every client would mean a separate App Store listing, separate review queue, separate crash triage, separate update cycle — and a single Apple policy change would mean resubmitting a dozen apps at once. That burden compounds forever.

Ship **one Foundation app**. Tenant resolves at login; branding (logo, accent color, agent roster) loads from the client record. A client's crew downloads "Foundation" and their world appears. Per-client branding lives in config, not in binaries.

### 4.2 What you're now on the hook for
Honest list, because these are ongoing costs, not one-time:
- **Apple review on every release.** Budget 1–3 days per submission, occasionally longer. Rejections happen; a mic-permission justification and a PTT entitlement make review more attentive, not less.
- **Privacy disclosures.** App Privacy labels, a clear mic-usage string, and a published privacy policy covering voice capture, transcription, and retention. Voice data is sensitive — say plainly what's stored, for how long, and who can hear it. This is also a sales asset if you get it right.
- **Crash reporting and a forced-update path.** When a build breaks PTT for a crew at 6am, you need to know before they call, and you need a way to push them off the bad version.
- **Support.** Someone answers when a crew member's headset button stops working. Define the SLA before you sell it, not after.
- **Version skew.** Old app versions will exist in the field for months. The Foundation API needs versioned endpoints and a minimum-supported-version check.
- **Apple Developer Program**, plus relay bandwidth, APNs volume, storage, and transcription minutes — all per-seat marginal costs.

**Interim distribution:** TestFlight for your own properties and the first pilot client. Real devices, real crews, no App Store review on every iteration. Go public only once PTT survives a full LUTS show night and a week of Exterior Rescue dispatch.

### 4.3 Revised pricing
The earlier $149/mo Switchboard figure assumed a web widget. Native apps with live audio carry real marginal cost per seat, so the structure changes:

| Line | Price | Rationale |
|---|---|---|
| Switchboard platform (web, per client) | $149/mo | unchanged — text, threads, approvals |
| Mobile app + PTT channels | $99/mo base | app access, one channel |
| Per active seat | $12/seat/mo | relay bandwidth, APNs, storage, transcription |
| Additional channels | $19/channel/mo | beyond the first |
| Your properties (Tier A) | $0 | AN, VoiceMIO, Blast Video, MRLIN, LUTS, Delivered |

A ten-person roofing crew lands around $368/mo for the full Switchboard plus radio. Compare to what a ServiceTitan seat or a dedicated PTT service costs them — and neither of those has an AI dispatcher talking in their ear.

**Watch the seat margin.** Transcription and relay minutes are the variable cost; meter them from day one in `llm_usage` and a new `ptt_usage` table, so if a crew talks 400 minutes a day you find out from a dashboard rather than a bill.

---

## 5. REVISED PHASE PLAN

| Phase | Scope | Gate |
|---|---|---|
| 1 | Capacitor shell, capability detection, browser fallback | none |
| 2 | Android mic foreground service, app-switch survival | none |
| 3 | iOS Tier A background audio, interruption handling | none |
| 4 | Offline capture queue, on-device transcription | none |
| 5 | **Channel model + relay (SFU) + transcripts into threads** | none — entitlement-independent, build early |
| 6 | Android receive: persistent connection, playback, BT + hardware buttons | test device |
| 7 | iOS PushToTalk framework, two-way channels, BT buttons, locked screen | **Apple entitlement** |
| 8 | Agent transmission with rate limits and quiet mode | after 5–7 |
| 9 | App Store readiness: privacy labels, crash reporting, version gate, support runbook | before public launch |

Phase 5 moved earlier deliberately — the channel model and relay are needed regardless of how Apple rules, so they should not sit behind an approval you don't control.

---

## 6. CLAUDE CODE PROMPT (Phases 5–8)

```
Repo switchboard-mobile + Foundation API. Read
docs/specs/SWITCHBOARD_NATIVE_MOBILE_VOICE.md and SWITCHBOARD_ADDENDUM_A_LIVE_PTT.md.
Same GLOBAL RULES (Supabase rhtwtoinmiekttvunlzs, CLI migrations, verify
gates, no secrets).

P5: Migrations for ptt_channels, ptt_members, ptt_transmissions with RLS.
Stand up an SFU (evaluate LiveKit self-hosted on Render vs managed; document
the choice and cost in docs/state/DECISIONS.md). Foundation endpoints for
join/leave/transmit and a transcript webhook that posts each transmission
into its linked Switchboard thread with delivered_to/intended_for as the receipt.
VERIFY: two browser clients on one channel, one talks, the other hears it,
transcript lands in the thread with a correct delivery count.

P6 (Android): extend VoiceBridge to hold a persistent channel connection in
the existing microphone foreground service; audio playback via media session;
notification doubles as channel indicator; map Bluetooth media-button and
rugged-handset PTT key events to transmit start/stop. VERIFY on device:
receive a transmission with the app backgrounded and screen off.

P7 (iOS): PushToTalk framework — only after John confirms the entitlement.
Channel join, incoming playback, Bluetooth PTT button, Dynamic Island state.
If the entitlement is denied, implement the live-audio-room fallback against
the same P5 channels instead.

P8: Agent transmission. Agents transmit only where ptt_members grants
can_transmit. Enforce one unsolicited transmission per agent per channel per
hour (alerts/approvals exempt). Decision-requiring content transmits a short
form and posts full detail plus action buttons to the thread. Honor per-channel
quiet mode, with an exception path for safety items only.
VERIFY: Silas's weather reschedule transmits once, the thread receives the full
detail with approve buttons, and a second unsolicited transmit in the same hour
is blocked and logged.

Add a ptt_usage table metering per-client relay minutes and transcription
minutes from P5 onward — cost visibility is not optional on this one.
```

---

## 7. ONE THING TO SETTLE EARLY

**Voice retention.** How long do you keep the audio? Transcripts are cheap and useful forever; raw audio is heavy, sensitive, and a liability. My recommendation: keep transcripts indefinitely, keep audio 30 days, and let a client set a shorter window. Whatever you choose, it goes in the privacy policy and the App Store labels — so decide before Phase 9, not during it.
