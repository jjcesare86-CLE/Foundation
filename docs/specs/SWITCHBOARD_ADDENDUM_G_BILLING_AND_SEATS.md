# SWITCHBOARD — ADDENDUM G: PRICING, SEATS AND BILLING
v1.0 · Oct 23, 2026 · John's decisions are marked **DECIDED**. Everything else is a recommendation he can overrule. Supersedes: Addendum E §E.9 (Work Rooms add-on), Addendum A §4.3 (mobile/PTT line items) and the "5 agent seats" wording in `SWITCHBOARD_V1_1_TIERS_AND_SPECIALIZATION.md`. Runs as item **Q**.

---

## G.1 The price (one plan, one meter)
- **DECIDED:** Work Rooms have **no separate price**. They are part of the product.
- **DECIDED:** **5 seats come with the program.** Extra seats cost less as the team grows.
- **Platform fee: $149/mo**, includes 5 seats. (Existing figure, unchanged.)
- **Extra seats, graduated tiers (RECOMMENDED):** each seat is priced at the tier it falls in.

| Seats | Price per seat / mo |
|---|---|
| 1–5 | included in the $149 |
| 6–25 | **$19** |
| 26–99 | **$17** |
| 100–249 | **$14** |
| 250+ | custom quote (floor stays above measured cost, G.6) |

Worked totals (platform fee + seats):

| Team size | Monthly | Effective per seat |
|---|---|---|
| 5 | $149 | $29.80 |
| 10 | $244 | $24.40 |
| 25 | $529 | $21.16 |
| 50 | $954 | $19.08 |
| 100 | $1,801 | $18.01 |
| 150 | $2,501 | $16.67 |
| 249 | $3,887 | $15.61 |

**Why graduated and not "everyone drops to $14 at 100":** with a whole-order discount a team of 99 pays $1,747 and a team of 100 pays $1,479, so adding people makes the bill smaller. That is a cliff customers will game and you will have to explain. Graduated keeps every added seat adding revenue, and your big accounts still see the effective rate slide toward $14. If you want the flat-drop version anyway, Stripe supports it (`tiers_mode=volume`); the cost is that cliff and about $320/mo less at exactly 100 seats.

**DECIDED Oct 23 (John): annual billing = 2 months free.** Pay for the year, pay for 10 months. Same tiers, billed on a yearly interval:

| | Monthly | Annual (10x monthly) |
|---|---|---|
| Platform (5 seats included) | $149/mo | $1,490/yr |
| Seats 6-25 | $19/mo | $190/seat/yr |
| Seats 26-99 | $17/mo | $170/seat/yr |
| Seats 100-249 | $14/mo | $140/seat/yr |

Seats added mid-year are prorated to the renewal date. Removals take effect at renewal, same as monthly. The pricing page shows a Monthly / Annual toggle with "2 months free" on the annual side.

## G.2 What a seat is
- **DECIDED Oct 23 (John): seats are human employees only.** The 5 included seats are 5 people.
- **A seat is a human with a login** in a workspace (`sb_memberships`, roles owner / admin / member).
- **No double charge:** every AI employee a customer pays for through the pricing engine (bundle or a la carte) is automatically on Switchboard as part of that fee. Being on the board costs nothing extra and uses no seat. The $149 platform fee and the seats pay for the human side of the board.
- **Not seats:** AI employees, connected agents (EX-##), Work Room guests (single-use invites), and your own properties (Tier A, always $0).
- **Bundles unchanged:** Professional ($499/mo, 10 agents) and Enterprise ($1,499/mo) include Switchboard with no separate platform fee. Confirm they also include the 5 seats (assumed yes); seats beyond 5 follow the same tiers.
- **AI employee pricing is untouched** and still comes from the existing pricing engine. This addendum prices people.
- **Resolved:** earlier docs said "5 agent seats". That wording is retired. Seats are people.

## G.3 Everything starts in a conversation (no add-on, no setup screen)
Work Rooms and group chats are created from the conversation you are already in:
1. **Bring someone in.** In any 1:1 chat header: "Add person". It becomes a group conversation (a violet `RM-##` room). The new person sees messages **from the moment they join**, not the earlier history, unless the adder ticks "Include earlier messages" (default off). Everyone sees "Maria was added by John."
2. **Group chat.** "New group" from the board, or by adding people to a thread as above.
3. **Group call (Work Room).** The video icon in any 1:1 or group chat opens a Work Room with that conversation's people prechecked; "Add someone" works mid-call; the end-of-room card posts back into the same thread (Addendum E.8).
4. **Guests** stay one-time invites into a room only, never into the thread's history, and never count as seats.
5. **Seat prompt at the moment of need.** Adding a 6th human shows: "Adding Maria adds $19/mo (prorated today). Add and continue?" for owners and admins; members can request. No visit to a billing page.
6. AI employees can be added to group conversations the same way. Eden, connected agents and PTT rules from earlier addenda are unchanged.

## G.4 Fair use (protects margin without a price tag)
Rooms, voice and captions have real per-minute cost, so "included" needs a ceiling you control without surprising customers:
- **Pooled per workspace, not per person.** Starting value to tune: **600 room participant-minutes per seat per month**, pooled (a 10-seat team shares 6,000). Recording, live captions and the AI note-taker count at the same rate until P1 load tests give real numbers.
- **Never cut a live call.** At 80% the owner gets a notice, at 100% a banner. Overage is **not billed at launch**; we contact the heavy workspace. Change this only after 60 days of data.
- Meter in usage rows (`work_room_minutes`, `ptt_minutes`, `stt_minutes`, `sb_translate`) in Foundation `llm_usage`.

## G.5 Stripe design
- **Objects:** one Product "Switchboard". Price A: flat $149/mo (`STRIPE_PRICE_SWITCHBOARD_PLATFORM`). Price B: per-unit, **graduated tiers**, quantity = `max(0, active_seats − 5)` (`STRIPE_PRICE_SWITCHBOARD_SEAT`). Annual versions of both. Test mode first; live prices created by John after approval.
- **Seat quantity** is computed by the API from `sb_memberships` (active humans), pushed to Stripe on every add/remove, idempotently. Adds prorate immediately; removals take effect at renewal (no mid-cycle refunds).
- **Where it runs:** existing AN checkout creates the Checkout Session with these price ids; the **Billing Portal** handles card and invoice changes. Foundation API owns one endpoint, `POST /billing/stripe/webhook`: verify the signature, dedupe by event id, then update `clients` plan fields and mirror `plan`, `seat_limit`, `status` into `sb_workspaces` (Addendum F).
- **Events handled:** `checkout.session.completed`, `customer.subscription.created|updated|deleted`, `invoice.paid`, `invoice.payment_failed`.
- **Failed payment (RECOMMENDED):** Stripe retries about 14 days. Day 0: owner banner and email. Day 7: owner-only warning in every window. Day 14 unpaid: workspace `status='suspended'` = read-only for humans, AI replies paused, history kept 30 days, no new JWTs. Paying restores instantly.
- **No card data** ever touches Foundation or the Switchboard database.

## G.6 Margin check (do before publishing prices)
An earlier doc estimated roughly **$12 per seat per month** of marginal cost for relay, push, storage and transcription. That was an estimate, not a measurement. At $14 (seats 100+) it leaves little room, and rooms, captions and the AI note-taker are the heavy users. Gate: after P1 and K load tests, compute cost per seat and per participant-minute from real usage. If measured cost exceeds $9 per seat, raise the 100+ tier before launch or tighten G.4. Do not publish the tiers on getswitchboard.io until this is done.

## G.7 Env vars (Render, on the service that owns the webhook)
`STRIPE_SECRET_KEY` (restricted key: Checkout, Customers, Subscriptions, Billing Portal, Prices read), `STRIPE_WEBHOOK_SECRET`, `STRIPE_PRICE_SWITCHBOARD_PLATFORM`, `STRIPE_PRICE_SWITCHBOARD_SEAT`, `STRIPE_PRICE_SWITCHBOARD_PLATFORM_ANNUAL`, `STRIPE_PRICE_SWITCHBOARD_SEAT_ANNUAL`. No Work Rooms price variable exists. The publishable key lives only on the checkout page.

## G.8 Phases
| Phase | What | Needs |
|---|---|---|
| Q0 | Seat counting from `sb_memberships`; `plan`, `seat_limit`, `status` on `sb_workspaces`; seat-prompt UI (G.3.5); group-chat conversion and "Add person" (G.3) | I, S0 |
| Q1 | Stripe products/prices in **test mode** via script; webhook; seat sync; Billing Portal; failed-payment states | Q0, John's Stripe test keys |
| Q2 | Fair-use meters and owner notices (G.4); plan/usage page | Q1 |
| Q3 | Live prices, annual plans, publish pricing (after G.6) | John |
Gate: in test mode, adding a 6th, 26th and 100th human changes the next invoice by exactly $19, $17 and $14; removing a seat lowers the next renewal; a replayed webhook changes nothing; an unpaid test subscription walks through the G.5 states; a guest never changes the bill.

## G.9 CLAUDE CODE PROMPT — item Q
```
Same session header and GLOBAL RULES as the RUNBOOK. Read
docs/specs/SWITCHBOARD_ADDENDUM_G_BILLING_AND_SEATS.md fully, plus Addenda F and C.
Migrations go in the switchboard repo; the webhook and Stripe code go in Foundation.
Build Q0 to Q2 in order with a verify gate each. Stripe TEST MODE ONLY; never
create live prices, never print or log any Stripe key or webhook secret. Seats
are active human memberships only (not AI employees, connected agents, guests or
Tier A internal properties). Graduated tiers: seats 1-5 included, 6-25 $19,
26-99 $17, 100-249 $14, 250+ manual quote. Webhook must be signature-verified
and idempotent by event id. Add the group-chat conversion ("Add person", history
hidden by default) and the seat prompt. Report which Stripe env vars John must set.
```

## G.10 Decisions still open
| # | Question | Recommendation |
|---|---|---|
| 1 | "5 seats" = people (not AI employees)? | **DECIDED: people only; paid AI employees are covered by their own fee** |
| 2 | Graduated tiers or flat drop at 100? | Graduated (G.1) |
| 3 | Mobile app and PTT included in the seat price (replacing the $99 base + $12/seat from Addendum A)? | Included, protected by G.4 fair use; confirm after G.6 |
| 4 | Annual discount? | **DECIDED: two months free** |
| 5 | Connected agents (Addendum D.10): still an add-on with a flat fee per extra agent? | Keep; amount not set yet |
| 6 | Bundles include the 5 seats? | Yes |
