# SWITCHBOARD — NATIVE MOBILE VOICE SPEC
**Uninterrupted push-to-talk when the app isn't in front**
v1.0 · Drop into docs/specs/ · Extends SWITCHBOARD_BUILD.md + v1.1

---

## 1. THE PROBLEM, STATED PRECISELY

In a mobile browser, holding the mic and then switching to the calendar kills the recording. This is not a bug we can code around — mobile browsers suspend media capture when the page loses focus, and no amount of JavaScript changes that. The web Switchboard stays as-is and degrades honestly; uninterrupted talk requires a native shell.

**What "uninterrupted" has to mean for a roofer on a ladder:**
1. Hold the mic, start talking, switch to email mid-sentence → still recording.
2. Screen locks in your pocket → still recording (this is the harder tier).
3. Press a Bluetooth headset button without pulling the phone out → starts talking.
4. Signal drops behind a hill → the message doesn't evaporate.

Items 1 and 4 are straightforward. Items 2 and 3 need an Apple entitlement with an approval gate. Plan accordingly.

---

## 2. PLATFORM REALITY

### 2.1 iOS — the framework is mandatory, not optional
This is the wrinkle. <cite index="6-1">Apple requires all push-to-talk apps on iOS to use the PushToTalk framework</cite>, and <cite index="4-1">as of the iOS 26 SDK the last unrestricted PushKit entitlement for PTT has been disabled</cite>. So we cannot ship walkie-talkie behavior on iOS by rolling our own background audio and hoping review doesn't notice — if the app behaves like PTT, Apple expects the framework.

Two tiers, and we should be clear-eyed about which one we're buying:

**Tier A — background audio mode.** Standard `UIBackgroundModes: audio` with an AVAudioSession configured for record. Recording survives app-switching (requirement 1). Does not survive a locked screen reliably and gives no system PTT affordances. Ships fast, no special entitlement.

**Tier B — PushToTalk framework.** Requires the `com.apple.developer.push-to-talk` entitlement, requested through the Apple developer account and subject to Apple's approval. What it buys: transmission works with the app backgrounded and the screen locked, the system shows PTT status in the Dynamic Island, and — the part that matters most for field crews — <cite index="6-1">it supports Bluetooth PTT buttons, Bluetooth remote speaker microphones, and headsets</cite>. It also uses its own APNs channel-based model, so the server side is real work, not a flag flip.

**Recommendation:** build Tier A first so the app ships and requirement 1 is solved. Submit the Tier B entitlement request the same week, because the approval wait is the long pole, and treat Tier B as a follow-on release. Do not promise crews a locked-screen radio until the entitlement is in hand.

### 2.2 Android — simpler, but with one ordering rule that will bite
A `microphone`-typed foreground service does the job. The requirements, in the order they must happen:
- Manifest: `android:foregroundServiceType="microphone"` on the service.
- Permissions: `FOREGROUND_SERVICE`, plus <cite index="19-1">`FOREGROUND_SERVICE_MICROPHONE` for apps targeting SDK 34</cite>, plus the `RECORD_AUDIO` runtime permission.
- <cite index="13-1">RECORD_AUDIO is a while-in-use permission, so a microphone foreground service cannot be started while the app is in the background</cite>.

That last rule is fine for our case and worth understanding: the user presses the mic *while looking at the app*, which starts the service in the foreground; the capture then continues when they switch away. Starting a recording from a background trigger is off the table, which is the correct privacy outcome anyway. <cite index="16-1">A foreground service also shows a persistent notification</cite> — don't fight it, design it: "Foundation is listening — tap to stop."

Permissions must be granted *before* `startForeground()` is called, or the system throws a SecurityException. Get the ordering right once, in a helper, and never think about it again.

### 2.3 Hardware buttons
The real unlock for field crews. iOS gets Bluetooth PTT button support through the Tier B framework. On Android, rugged handsets used in trades (Sonim, Kyocera DuraForce and similar) expose a dedicated PTT key as a standard key event — map it in the activity. Support both, and a Bluetooth headset's media button as the universal fallback.

---

## 3. ARCHITECTURE: WRAP, DON'T REBUILD

Switchboard is already a self-contained web app. Rebuilding it natively for iOS and Android would triple the surface area and guarantee three versions drifting apart.

**Use Capacitor.** The existing Switchboard UI loads as-is inside a native shell; the only native code is a small `VoiceBridge` plugin. One UI, three platforms, and every future Switchboard feature ships everywhere at once.

```
Switchboard (existing web app)
        │
        ├── browser  → Web Speech API, foreground only, honest degradation
        └── Capacitor shell
                 └── VoiceBridge plugin
                        ├── iOS:     AVAudioSession + background audio  (Tier A)
                        │            PushToTalk framework               (Tier B)
                        └── Android: microphone foreground service + PTT key events
```

### 3.1 Capability detection — one function, honest fallback
```js
// Switchboard asks what it's running on and adapts. No feature flags in the UI.
const voice = {
  native: !!window.Capacitor?.isNativePlatform?.(),
  backgroundCapture: false,   // set by VoiceBridge.capabilities() at boot
  lockScreenPTT: false,       // Tier B only
  hardwareButton: false,
};
```
When `backgroundCapture` is false, the voice settings sheet shows one line under the hands-free toggle: *"In a browser, recording stops when you switch apps. The app keeps listening."* That's a truthful limitation and a soft install prompt in the same sentence — no dark pattern, no broken promise.

### 3.2 The plugin surface
```
VoiceBridge.capabilities() → {backgroundCapture, lockScreenPTT, hardwareButton, onDeviceSTT}
VoiceBridge.startCapture({mode:'hold'|'toggle', lang})   // starts FGS / activates audio session
VoiceBridge.stopCapture() → {audioRef, transcript?, durationMs}
VoiceBridge.onHardwareButton(cb)                          // PTT key / BT button down+up
VoiceBridge.onInterruption(cb)                            // incoming phone call, route change
```

### 3.3 Interruptions are not edge cases
A real phone call will arrive mid-transmission. On iOS, handle `AVAudioSession` interruption notifications; on Android, watch audio focus. Behavior: stop capture, keep whatever was transcribed in the composer as a draft, and post a line in the thread — *"Recording stopped when a call came in. Your draft is saved."* Never silently lose the words someone just said.

---

## 4. THE PART NOBODY SPECS AND EVERYONE NEEDS: OFFLINE

Your crews work in rural Chautauqua County. Signal drops. A voice message that vanishes because there was no bar is worse than no feature at all, because the person believes it sent.

- Capture writes audio to a local queue **before** any network attempt.
- Each queued item shows in the thread immediately with a "waiting for signal" state — visible, not hidden.
- A background sync drains the queue when connectivity returns; the message then transitions to sent with its normal receipt.
- Transcription strategy: prefer on-device recognition when available (iOS `SFSpeechRecognizer` with on-device mode, Android `SpeechRecognizer`) so the text exists even offline; fall back to server transcription on drain for accuracy.
- Hard rule, and it belongs in the Proof of Work standard: **a queued message never renders as sent.** The receipt only appears when the server confirms.

---

## 5. WHAT SHIPS WHEN

| Phase | Scope | Gate |
|---|---|---|
| 1 | Capacitor shell wrapping the existing Switchboard; capability detection; browser fallback messaging | none — start now |
| 2 | Android microphone foreground service + notification + app-switch survival | none |
| 3 | iOS Tier A background audio; interruption handling both platforms | none |
| 4 | Offline capture queue + on-device transcription + queued-state UI | none |
| 5 | iOS Tier B PushToTalk framework, locked-screen transmission, Bluetooth PTT buttons | **Apple entitlement approval** |
| 6 | Android hardware PTT key mapping for rugged handsets | needs a test device |

**Start the Apple entitlement request during Phase 1.** It is the only item on this list whose timeline you don't control.

---

## 6. CLAUDE CODE PROMPT

```
New repo: switchboard-mobile. Read docs/specs/SWITCHBOARD_NATIVE_MOBILE_VOICE.md.
Same GLOBAL RULES as the Batch 1 master prompt (no secrets, verify gates
between phases, Supabase project rhtwtoinmiekttvunlzs where relevant).

Phase 1: Scaffold a Capacitor app that loads the existing Switchboard web
build. Implement VoiceBridge.capabilities() returning all-false stubs on web.
Wire Switchboard's voice settings sheet to show the browser-limitation line when
backgroundCapture is false. VERIFY: Switchboard renders identically in the shell and
in a browser; capabilities() returns correct values on each.

Phase 2 (Android): VoiceBridge native module with a microphone-typed foreground
service. Manifest: android:foregroundServiceType="microphone", permissions
FOREGROUND_SERVICE, FOREGROUND_SERVICE_MICROPHONE, RECORD_AUDIO. Enforce the
ordering: request and confirm RECORD_AUDIO BEFORE startForeground(), or the
system throws SecurityException. Persistent notification reads "Foundation is
listening — tap to stop" and stopping from the notification ends capture
cleanly. VERIFY on a real device: hold mic, switch to another app mid-sentence,
return — transcript is complete and unbroken.

Phase 3 (iOS Tier A): UIBackgroundModes audio; AVAudioSession configured for
record with correct category/options. Handle AVAudioSession interruption
notifications on iOS and audio focus loss on Android: stop capture, preserve
the partial transcript as a composer draft, post the "recording stopped" system
line into the thread. VERIFY: app-switch survival on device; incoming phone
call preserves the draft rather than losing it.

Phase 4: Local capture queue (audio written to disk before any network call),
queued-state message rendering, background drain on reconnect, on-device
transcription where available with server fallback. VERIFY in airplane mode:
message records, shows "waiting for signal", and sends with a real receipt on
reconnect — and never shows a receipt while queued.

Phase 5: iOS PushToTalk framework integration behind the
com.apple.developer.push-to-talk entitlement (do not start until John confirms
approval). Channel model, APNs wiring, Bluetooth PTT button support.

Phase 6: Android hardware PTT key event mapping.

Verify each platform API against current Apple and Android developer docs
before implementing — these requirements change between OS versions, and the
spec's citations are a starting point, not gospel.
```

---

## 7. TWO THINGS TO DECIDE

**Does the app need to receive PTT, or only send it?** Everything above assumes your people talk *to* teammates. If you want the true radio experience — Silas's weather alert coming through a crew's speaker unprompted, or one crew member talking live to another — that's the incoming half, and on iOS it's specifically what the Tier B channel model exists for. It roughly doubles the Phase 5 work. Worth it for LUTS show crews on a shoot night; probably overkill for a bookkeeper.

**Who gets the app?** If it's only your properties and your crews, distribution is simple. If Tier B clients' employees install it, the app is customer-facing software with Apple review, support, and update obligations attached — a real commitment beyond a web Switchboard, and one worth pricing into Switchboard add-on.
