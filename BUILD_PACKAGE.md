# BUILD PACKAGE — Switchboard + Foundation
**September 2, 2026 · prepared for Claude Code**

Everything in here is a plan or a reference build. None of it is deployed. To make any of it real: put this folder in the Foundation repo, open Claude Code there, and work `docs/specs/02_BUILD_ORDER.md` one item at a time.

## Put it in the repo

```powershell
# from the unzipped folder
Copy-Item -Recurse -Force .\docs  "C:\Users\jjces\OneDrive\Desktop\Foundation\"
Copy-Item -Recurse -Force .\demo  "C:\Users\jjces\OneDrive\Desktop\Foundation\"
Copy-Item -Recurse -Force .\assets "C:\Users\jjces\OneDrive\Desktop\Foundation\"
Copy-Item -Force .\BUILD_PACKAGE.md .\RUNBOOK.md .\CHECKLIST.md "C:\Users\jjces\OneDrive\Desktop\Foundation\"
cd "C:\Users\jjces\OneDrive\Desktop\Foundation"
git add docs demo assets BUILD_PACKAGE.md RUNBOOK.md CHECKLIST.md
git commit -m "docs: Switchboard + Foundation build package (specs, state, demo v6)"
git push
```

## Read in this order
0. `RUNBOOK.md` — **start here.** Phase 0 to launch, every paste block inlined, in order.
1. `docs/specs/00_STATE_OF_THE_BUILD.md` — what's actually true (roster, schema, the 500, the router bug)
2. `docs/specs/02_BUILD_ORDER.md` — the sequence
3. `CHECKLIST.md` — tick boxes as you go
4. `docs/specs/01_PROJECT_REF_CORRECTION.md` — paste at the top of every Claude Code session

## First session
```
1. Do the John-side steps in docs/specs/03_PHASE0_RESTORE_API.md §0.1 and §0.2
2. Open Claude Code in the Foundation repo
3. Paste: docs/specs/01_PROJECT_REF_CORRECTION.md (the code block)
4. Paste: docs/specs/03_PHASE0_RESTORE_API.md §0.3 prompt, then §0.4 prompt
5. Confirm /agents returns 26. That's the gate for everything else.
```

## What's in here
| Path | What |
|---|---|
| `docs/specs/00–03_*.md` | State, session header, build order, Phase 0 |
| `docs/specs/FOUNDATION_*.md` | Roster + Fable 5.1 plan, Batch 1 agents, security fixes |
| `docs/specs/CLAUDE_CODE_MASTER_PROMPT_BATCH1.md` | The Batch 1 prompt (item B) |
| `docs/specs/CONNECTIONS_HUB_BUILD.md` | OAuth portal + connection_broker (item C) |
| `docs/specs/AGENT_OPS_AUDIT_ELIJAH_V1_1.md` | Health board (item D) + Elijah calls/traffic (item G) |
| `docs/specs/UNLAZY_AND_PROOF_OF_WORK.md` | Dev skill + receipt standard (item E) |
| `docs/specs/AUTOPILOT_NUANCES_IMPLEMENTATION.md` | Preflight, playbooks, interview, sliders (item F) |
| `docs/specs/ELIJAH_SCOREBOARD_BUILD.md` | Marketing scoreboard (item G) |
| `docs/specs/SWITCHBOARD_*.md` | Switchboard web, tiers + specialization, native mobile, live PTT, naming (items I–M) |
| `docs/state/` | CURRENT / DECISIONS / COSTS — living files Claude Code reads and updates |
| `demo/switchboard-demo-v11.html` | Working front-end reference for Switchboard. Open in Chrome or Edge. |
| `assets/` | Logo (original + trimmed) |

## Demo v11 — what changed from v5
- Color comes from the logo and it's everywhere it should be: copper for AI, cobalt for people, violet for rooms — in avatars, window headers, ID chips, and the bubbles themselves. The page and night mode carry soft copper and cobalt washes instead of flat grey.
- Your bubbles are your color: seven presets plus a custom picker under your name. Text flips to ink or white for contrast automatically.
- Language setting with a working Spanish demo: every incoming message and action button renders in Spanish, with "show original" one tap away. Real translation is a router pass — see SWITCHBOARD_BUILD.md Addendum B.
- AI voice choice (Warm / Crisp / Calm / Bright) in the same sheet; shows in the call bar.
- Day theme default, night toggle; profile with optional title, status, away message, phone; away banners; phone buttons that read at a glance; teammate cards. Everything from v5 kept.
- Pinned is a shortcut, not a move: hover any name for the pin; pinned people also stay in their department or the People list.
- The board is private to one business — a lock line at the bottom names the workspace. Tenancy model: SWITCHBOARD_BUILD.md Addendum C.
- Caleb is Security (CISO) and runs the inbox-quarantine scenario; Ezra is Tech & IT; Nehemiah is Operations. Reflects the Sep 2 roster change.
- Conversation discipline: AI teammates greet and restate an open question instead of dropping it; human teammates show "delivered" rather than scripted replies. Rules + tests in 05_CONVERSATION_DISCIPLINE.md.
- Avatars: real initials (single-name agents show one letter), profile photo upload (cropped to a square, stored per user), and status dots redrawn — yellow busy / red needs-you / green available with a double ring so they read on copper and cobalt tiles alike.
