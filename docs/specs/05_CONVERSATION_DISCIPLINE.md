# CONVERSATION DISCIPLINE — HARD RULES FOR EVERY AGENT
**Added Sep 4, 2026 after this exchange in the demo:**

> Marcus: Want me to price the repair while I'm up here or come back Thursday?
> me: hi
> Marcus: Copy that.

Two facts about that exchange. Marcus is a human teammate and the reply was a scripted placeholder — the demo has no model behind it. But the failure it *looks like* is the single most damaging thing a real AI employee can do: treat a greeting as an answer, drop the open question, and leave the person believing something was decided. If the agents do that, nobody trusts them, and the whole product is a chat toy. So this is now a hard rule with a schema, a prompt block, and tests.

---

## 1. The rule

Every thread carries **open items** — questions the agent has asked or decisions it is waiting on. Any inbound message is classified before anything else:

| Inbound is… | Agent must |
|---|---|
| A clear answer to an open item | Resolve it, confirm in one line, act, receipt. |
| A greeting, acknowledgment, or small talk ("hi", "ok", "thanks", "sounds good") | Return the greeting in a few words, then **restate the open item in one sentence with the choices intact.** Never resolve anything. |
| A new request unrelated to the open item | Handle it *or* say it's noted — then restate the open item so it doesn't get lost. The open item stays open. |
| A partial answer (resolves one of two open items) | Confirm the one resolved; restate the other. |
| Ambiguous — could be an answer, could be an aside | Ask **one** clarifying question that includes the open item's choices. Never guess. |

"Copy that," "Got it," "Understood" are **only** valid replies to an actual instruction. As a response to a greeting they are a bug.

## 2. Schema

```sql
ALTER TABLE sb_threads ADD COLUMN IF NOT EXISTS open_items JSONB DEFAULT '[]';
-- [{id, asked_at, question, choices:[...], resolves_action_id, resolved_at}]
```
- The agent appends an open item whenever it asks the user something or presents action buttons.
- `resolved_at` is set only when an inbound is classified as an answer to *that* item.
- Open items older than 72h surface once in the daily digest ("still waiting on you for: …") and never nag more than that.
- `prompt_composer` always injects the current open items **above** the recent-messages window, so the agent cannot lose them to context pressure.

## 3. Prompt block — append to ALL agents (same sweep as PROOF OF WORK, item E)

```
CONVERSATION DISCIPLINE (non-negotiable):
1. Before replying, read OPEN ITEMS. If any exist, decide whether this message
   answers one. If it does not, you are not done until you have restated it.
2. A greeting, "ok", "thanks", or small talk is never an answer. Reply in kind
   briefly, then put the open question back in one sentence with the choices.
   Example — open item: "price the repair now or come back Thursday?"
   User: "hi"  →  You: "Hi John. Still need your call on the Central gutter:
   price the fascia repair while the crew's up there, or come back Thursday?"
3. "Copy that" / "Got it" / "Understood" are only for actual instructions.
4. If a message could be an answer or could be an aside, ask one clarifying
   question that includes the choices. Never guess which one they meant.
5. When a new topic arrives mid-decision, handle it and then restate the
   open item. Nothing gets dropped silently.
6. When you resolve an open item, say what you understood in one line before
   acting: "Pricing it now — I'll have a number in twenty minutes."
7. If a human teammate is the one being asked (not you), never answer on their
   behalf. Say the message was delivered and when they're likely to see it.
```

## 4. Tests that must pass (add to the ops audit L5 smoke set and to CI)

Seed a thread with the Central-gutter open item, then send each of these and assert on the reply:
1. `"hi"` → contains a greeting AND the words "price" and "Thursday"; open item still open.
2. `"ok"` → same; nothing resolved.
3. `"Thursday"` → open item resolved; reply confirms "Thursday" in one line; an action row exists.
4. `"can you also send the Hanson invoice"` → Hanson request handled or noted; reply still restates the gutter choice; open item still open.
5. `"do it"` (ambiguous) → exactly one clarifying question containing both choices.
6. Human-addressed thread: `"hi"` to Marcus → no synthesized reply from Marcus; system line shows delivered.

A build in which any of these six fails does not ship. These belong in the Unlazy gates file for items E and I.

## 5. Where it lives
- Prompt block: every agent, appended in item E's sweep (Eden included — this is not receipt logging, it's conversational care).
- Schema + composer injection: item I, Phase 1.
- Tests: item D's smoke layer and item E's gates.
- The demo (`demo/switchboard-demo-v11.html`) now shows the *correct* behavior for AI teammates and shows human teammates as "delivered" rather than faking their replies.
