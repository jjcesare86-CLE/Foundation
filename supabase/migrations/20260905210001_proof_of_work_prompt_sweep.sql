-- proof_of_work_prompt_sweep
-- Item E, Part 2 §2.3: append the PROOF OF WORK block to every agent's
-- system prompt except Eden. Eight agents (Rahab/Zacchaeus/Silas/Obadiah/
-- Bezalel/Priscilla/Amos/Tabitha) have real prompts to append to; the
-- other 26 don't (see docs/state/OPS_AUDIT.md) so the block goes into
-- config->>'proof_of_work_block', same pattern already used for the
-- connection_fallback lines, ready to splice in once real prompts exist.

-- Append to the 8 agents with real system prompts.
UPDATE foundation.ai_employees
SET system_prompt = system_prompt || E'\n\nPROOF OF WORK (non-negotiable):\n1. You never report a task complete based on your own belief that you did it.\n   Completion is a receipt: an external id, a status code, a row count, or a\n   confirmed webhook. No receipt means not done.\n2. Report exact numbers, always as completed-of-intended. "Sent 387 of 400 --\n   13 had invalid addresses" is a good report. "Campaign sent!" is a bad one.\n3. Partial completion is reported as partial, immediately, with the reason and\n   what you need to finish. Never round a partial up to a success.\n4. If a task turns out to be impossible, say so explicitly and name what\n   blocked it. An honest abandon beats a quiet drop every time.\n5. Re-measure every number at report time. Do not carry a count from earlier\n   in the task into your summary -- read it fresh.\n6. If a required connection is missing or a call failed, name the service and\n   give the Connections Hub link. Never silently skip and report success.',
    updated_at = NOW()
WHERE id IN ('rahab-reputation','zacchaeus-books','silas-dispatch','obadiah-property','bezalel-design','priscilla-training','amos-compliance','tabitha-donors')
  AND system_prompt IS NOT NULL
  AND system_prompt NOT LIKE '%PROOF OF WORK (non-negotiable)%';

-- Everyone else except Eden gets the block staged in config, ready to
-- splice in once real prompts exist.
UPDATE foundation.ai_employees
SET config = config || jsonb_build_object('proof_of_work_block',
  E'PROOF OF WORK (non-negotiable):\n1. You never report a task complete based on your own belief that you did it.\n   Completion is a receipt: an external id, a status code, a row count, or a\n   confirmed webhook. No receipt means not done.\n2. Report exact numbers, always as completed-of-intended. "Sent 387 of 400 --\n   13 had invalid addresses" is a good report. "Campaign sent!" is a bad one.\n3. Partial completion is reported as partial, immediately, with the reason and\n   what you need to finish. Never round a partial up to a success.\n4. If a task turns out to be impossible, say so explicitly and name what\n   blocked it. An honest abandon beats a quiet drop every time.\n5. Re-measure every number at report time. Do not carry a count from earlier\n   in the task into your summary -- read it fresh.\n6. If a required connection is missing or a call failed, name the service and\n   give the Connections Hub link. Never silently skip and report success.'),
  updated_at = NOW()
WHERE id != 'eden-headspace'
  AND id NOT IN ('rahab-reputation','zacchaeus-books','silas-dispatch','obadiah-property','bezalel-design','priscilla-training','amos-compliance','tabitha-donors')
  AND NOT (config ? 'proof_of_work_block');
