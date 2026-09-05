# SWITCHBOARD — NAMING DECISION
**The AI + human team messenger, formerly specced as "Foundation Dock"**
Decision date: recorded this session · Drop into docs/specs/ and log in docs/state/DECISIONS.md

---

## THE NAME

**Switchboard.** The operator that connects everyone to everyone — AI employees and human teammates on one board.

Considered and rejected: **AIM**. The mark is registered and renewed (Yahoo IP Holdings, with AOL brands now under Bending Spoons as of 2026), the product category is identical, and the UI is a deliberate homage — the highest-risk combination available. Direct precedent exists: Aimster renamed to Madster over AOL's AIM mark. Not registrable, not defensible, and exposed to Apple's IP complaint process which can pull an app with no hearing. Decision made with full knowledge of the above, which is precisely why it's a no.

**The nostalgia stays — in the marketing, not the trademark.** Presence dots, tear-off windows, the buddy-list column, a door-open chime when someone comes online. Positioning line: *"If you ever had a buddy list, you already know how to use this."* Everyone over 35 gets it instantly and we own the name outright.

---

## NAMING CONVENTIONS

| Context | Use |
|---|---|
| Product name | Switchboard |
| Full/formal | Switchboard by Automation Nation |
| Client-facing nav label | "Your Team" (unchanged — plainer than the product name for daily use) |
| Internal repo | `switchboard` (web), `switchboard-mobile` (native) |
| API prefix | `/switchboard/*` (was `/dock/*`) |
| DB tables | `sb_threads`, `sb_messages`, `sb_pins`, `sb_settings` (were `dock_*`) |
| PTT tables | `ptt_channels`, `ptt_members`, `ptt_transmissions` (unchanged) |
| Embed script | `switchboard/v1.js` |
| Voice channels | "Switchboard channels" — a crew is "on the board" |

Everyday language to use in copy: *on the board*, *open a line*, *patch me through*. Avoid *Switchboard*, *buddy list* as a formal product term (fine as a nostalgic aside in marketing), and anything AIM-adjacent.

---

## RENAME STATUS

**Done.** Every spec in this package already carries the Switchboard name, `sb_*` table prefixes, `/switchboard/*` routes, and the `switchboard-mobile` repo name. Nothing is built yet, so this cost nothing. If any older copies of the "Foundation Dock" documents exist elsewhere on disk, delete them — this package is the only current set.

---

## PROTECT IT

Since the whole point of choosing this name is that you can own it, actually own it:

1. **Domains** — check and grab `switchboard.ai`, `getswitchboard.com`, `switchboard.automaitionnation.com` at minimum. Do this today; a name you've decided on and haven't registered is a name someone else can take.
2. **Clearance search** before filing — "switchboard" is a real word and there will be other marks. What matters is whether any exist in software/communications (Nice classes 9 and 42). A knockout search is cheap.
3. **File the trademark** in classes 9 and 42 once cleared, and file before public launch rather than after.
4. **Social handles** — grab them even if unused.

A word of realism: "Switchboard" is descriptive-adjacent for a communications product, which can make registration harder. A distinctive logo and consistent stylization strengthen the application, and so does using it as a proper noun in all copy ("Switchboard connects…" not "the switchboard connects…"). Worth raising with counsel when you file.

---

## ONE LINE FOR THE PITCH

> Switchboard puts your whole team — the people and the AI — in one place. Open a line to any of them.
