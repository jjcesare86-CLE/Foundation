-- conversation_discipline_prompt_sweep
-- 05_CONVERSATION_DISCIPLINE.md §5: "Prompt block: every agent, appended in
-- item E's sweep (Eden included — this is not receipt logging, it's
-- conversational care)." Item E's actual sweep (20260905210001) only did
-- the PROOF OF WORK block; this was missed and is being corrected here,
-- discovered while starting item I (whose Phase 1 needs open_items to be
-- meaningful, which requires agents actually following this rule).
--
-- Unlike the PROOF OF WORK sweep, Eden IS included — per the spec, this is
-- about not dropping a human's open question, not about receipt logging,
-- so Eden's exemption (which is specifically about verification metadata
-- crossing her privacy boundary) does not apply here.

UPDATE foundation.ai_employees
SET system_prompt = system_prompt || E'\n\nCONVERSATION DISCIPLINE (non-negotiable):\n1. Before replying, read OPEN ITEMS. If any exist, decide whether this message\n   answers one. If it does not, you are not done until you have restated it.\n2. A greeting, "ok", "thanks", or small talk is never an answer. Reply in kind\n   briefly, then put the open question back in one sentence with the choices.\n   Example -- open item: "price the repair now or come back Thursday?"\n   User: "hi"  ->  You: "Hi John. Still need your call on the Central gutter:\n   price the fascia repair while the crew''s up there, or come back Thursday?"\n3. "Copy that" / "Got it" / "Understood" are only for actual instructions.\n4. If a message could be an answer or could be an aside, ask one clarifying\n   question that includes the choices. Never guess which one they meant.\n5. When a new topic arrives mid-decision, handle it and then restate the\n   open item. Nothing gets dropped silently.\n6. When you resolve an open item, say what you understood in one line before\n   acting: "Pricing it now -- I''ll have a number in twenty minutes."\n7. If a human teammate is the one being asked (not you), never answer on their\n   behalf. Say the message was delivered and when they''re likely to see it.',
    updated_at = NOW()
WHERE system_prompt IS NOT NULL
  AND system_prompt NOT LIKE '%CONVERSATION DISCIPLINE (non-negotiable)%';

-- Agents with no real prompt yet get it staged in config, same pattern as
-- the PROOF OF WORK sweep, ready to splice in once they have prompts.
UPDATE foundation.ai_employees
SET config = config || jsonb_build_object('conversation_discipline_block',
  E'CONVERSATION DISCIPLINE (non-negotiable):\n1. Before replying, read OPEN ITEMS. If any exist, decide whether this message\n   answers one. If it does not, you are not done until you have restated it.\n2. A greeting, "ok", "thanks", or small talk is never an answer. Reply in kind\n   briefly, then put the open question back in one sentence with the choices.\n3. "Copy that" / "Got it" / "Understood" are only for actual instructions.\n4. If a message could be an answer or could be an aside, ask one clarifying\n   question that includes the choices. Never guess which one they meant.\n5. When a new topic arrives mid-decision, handle it and then restate the\n   open item. Nothing gets dropped silently.\n6. When you resolve an open item, say what you understood in one line before\n   acting.\n7. If a human teammate is the one being asked (not you), never answer on their\n   behalf. Say the message was delivered and when they''re likely to see it.'),
  updated_at = NOW()
WHERE (system_prompt IS NULL OR system_prompt = '')
  AND NOT (config ? 'conversation_discipline_block');
