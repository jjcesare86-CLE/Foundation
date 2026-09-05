# BUILD ORDER
**What to paste into Claude Code, in what sequence, and why. One item per session.**

---

## THE ONE-LINE VERSION

Phase 0 → A → B → D → C → E → H → F → G → I → J → K → L → M.
Paste the session header (`01_PROJECT_REF_CORRECTION.md`) first, every time.

---

## THE ITEMS

| # | Spec file | What it ships | Needs | Size |
|---|---|---|---|---|
| **0** | `03_PHASE0_RESTORE_API.md` + `04_ROSTER_CHANGE_CALEB_SECURITY.md` | `/agents` answering, router tier map fixed, migrations reconciled, Caleb → CISO + Nehemiah → COO | env vars (done) | S |
| **A** | `FOUNDATION_FIXES_GUIDE.md` | CORS whitelist, API-key gate, Fernet broker | 0 | S |
| **B** | `CLAUDE_CODE_MASTER_PROMPT_BATCH1.md` | Rahab, Zacchaeus, Silas + Option A/B router + **the typed action library** | A | L |
| **D** | `AGENT_OPS_AUDIT_ELIJAH_V1_1.md` (Part A) | Five-layer health board for all 29 agents; heartbeat registry | B | M |
| **C** | `CONNECTIONS_HUB_BUILD.md` | OAuth portal; `connection_broker` | A | M |
| **E** | `UNLAZY_AND_PROOF_OF_WORK.md` | Receipt standard in every agent; Unlazy on Foundation only | B, C | M |
| **H** | (Batch 2 + 3 specs — to be written when B is green) | Obadiah, Bezalel, Priscilla, Amos, Tabitha | B | L |
| **F** | `AUTOPILOT_NUANCES_IMPLEMENTATION.md` | Preflight, brand-voice/playbook engine, interview engine, behavioral sliders | C, E | L |
| **G** | `ELIJAH_SCOREBOARD_BUILD.md` + Ops Audit Part B | Marketing scoreboard, calls + web traffic | C, D | L |
| **I** | `SWITCHBOARD_BUILD.md` | Switchboard, web — the buddy list, threads, receipts as DMs | B, C, E | XL |
| **J** | `SWITCHBOARD_V1_1_TIERS_AND_SPECIALIZATION.md` | Two-tier access; industry playbooks (extend the existing `industries` tables) | F, I | L |
| **K** | `SWITCHBOARD_NATIVE_MOBILE_VOICE.md` phases 1–4 | Capacitor shell, background mic, offline queue | I | XL |
| **L** | `SWITCHBOARD_ADDENDUM_A_LIVE_PTT.md` | Two-way PTT channels, relay, agents transmitting | K | XL |
| **M** | Native mobile phases 5–6 | iOS PushToTalk framework, hardware buttons | L + **Apple entitlement** | L |

S = a session. M = a few days. L = a week or two. XL = a month or more.

---

## SEQUENCE AND REASONING

### Right now
**0 — Restore the API.** A checkbox, four GRANT lines, a tier-map fix, and migration bookkeeping. Until `/agents` returns 26 rows, no later item can be verified.

**A — Security foundations.** Env vars are set; the code that reads them isn't written. Half a session. Internal endpoints are open to anyone with the URL until this lands.

**B — Batch 1.** Ships the typed action library that D, E, I, and G all build on. Rahab first inside it for exactly that reason. Phase 1 (Joanna rename) is already done in the database and is now a verify-only step.

**D — Ops audit.** Immediately after B. Turns "we have 29 agents" into a green/amber/red board you can put on a screen, and it surfaces the `PIPELINE_API_KEY` and voice-proxy gaps as rows with fixes attached.

### Weeks 3–6
**C — Connections Hub.** Every agent that touches the outside world is blocked without it. **File Google's OAuth verification for the gmail.send scope the day you start** — 1–2 weeks and you can't shorten it.

**E — Proof of Work + Unlazy.** Small. Makes every later build honest. Unlazy stays per-project on Foundation, as decided.

**H — Batches 2 and 3.** Five more agents on the Batch 1 pattern. Cheapest roster growth available and it fills the specialization matrix for J.

### Weeks 7–12
**F — Autopilot nuances.** Preflight first inside it; it starts saving Higgsfield credits the day it lands.

**G — Elijah scoreboard.** Now has data because C and D exist. Calls and web traffic (Ops Audit Part B) ride along.

**I — Switchboard (web).** The showpiece. `demo/switchboard-demo-v11.html` is the reference implementation of the front-end behavior — build to it.

### Month 4 onward
**J — Specialization engine.** `industries` and `industry_playbooks` already exist in Foundation; read their live columns and extend. Generate Wave 1, review fireworks and roofing yourself.

**K → L → M.** File the Apple PTT entitlement when you start K, not when you reach M.

---

## CLEANUP ITEMS (not blocking — do when convenient)
- `pricing_config`, `pricing_outcomes`, `pricing_quotes`, `transfer_logs` exist in **both** Foundation and AN databases. Decide which is canonical, point the other product at the API, and drop the duplicate. Probably Foundation, per the architecture.
- `supabase` CLI is on 2.115; current is 2.116. `scoop update supabase` or equivalent.
- Docker Desktop is not installed. Not required for this build order (the specs route around it), but `supabase db diff` and local dev would want it eventually.

---

## RULES FOR EVERY SESSION
1. Paste `01_PROJECT_REF_CORRECTION.md` first.
2. One item per session.
3. Let every VERIFY gate pass before moving on. Red means stop.
4. Update `docs/state/CURRENT.md` before ending the session.
5. When Claude Code discovers something that contradicts `00_STATE_OF_THE_BUILD.md`, it updates that file in the same commit.
