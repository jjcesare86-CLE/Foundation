# SESSION HEADER — PASTE FIRST, EVERY TIME
**Copy the block below into Claude Code at the top of every session before any build prompt.**

```
GROUND TRUTH FOR THIS SESSION — read before any work:

Working repo:   C:\Users\jjces\OneDrive\Desktop\Foundation  (jjcesare86-CLE/Foundation, branch main)
Supabase:       project ref rhtwtoinmiekttvunlzs  (named "Foundation")
Agent catalog:  schema `foundation`, table `foundation.ai_employees` (26 active rows) —
                NOT `public.ai_employees`, and NOT the Automation Nation database.
API:            https://foundation-api-9gpl.onrender.com  (Render service foundation-api-9gpl)
Docker:         NOT installed on this machine. Do not use `supabase db dump` / `db pull`
                / `db reset`; introspect via SQL against the live database instead.

Do NOT touch:   rzsryxvlaezfvftqpvbx (that is Automation Nation's database),
                the AN-repo folder, public.ai_employees anywhere,
                eden_sessions isolation, tier gating (lives in platforms),
                GABRIEL (paused), the LYDIA Shopify agent.

Before any migration: run `supabase projects list` and confirm the LINKED marker
is on rhtwtoinmiekttvunlzs. If not: `supabase link --project-ref rhtwtoinmiekttvunlzs`.

Read docs/specs/00_STATE_OF_THE_BUILD.md before writing code. Where any other
spec disagrees with it, 00_STATE wins. Where 00_STATE disagrees with the live
database, the live database wins — and update 00_STATE.

Full project map (reference only):
  rhtwtoinmiekttvunlzs = Foundation          ← all agent / Switchboard / playbook work goes HERE
  rzsryxvlaezfvftqpvbx = Automation Nation   ← AN sales pipeline + homepage only
  xgaqgqkycckolwfcrmop = VoiceMIO
  qstcxqytmaqkygdiacfd = Blast Video
  lrlspiokmtetbzgdvzep = MRLIN
  nrqhiprzwmgdbsvyzbws = Delivered Fireworks
  dhkspkspelieaesvflvc = Bakerellas
  ohhzkmvekopnheazxbjf = Broker Broker
  mtgionuehdipyhpkiget = Exterior Rescue
  zltppbyjuivsqeolnony = MRLIN NetSuite Wizard
```
