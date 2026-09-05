-- connections_fallback_lines
-- Item C, Part 4: "add the missing-connection fallback line to Nathan,
-- Esther, Naomi, and Joanna's system prompts." All four currently have
-- system_prompt = NULL (see docs/state/OPS_AUDIT.md -- 27 of 30 agents do)
-- so there's no prompt text to append a line to yet. Recording the exact
-- required copy in config->>'connection_fallback' instead, so whoever
-- writes these agents' real prompts has the line ready to splice in
-- rather than needing to reconstruct it from this spec later.

UPDATE foundation.ai_employees
SET config = config || jsonb_build_object('connection_fallback', 'I need access to your Gmail first — tap Connect Your Accounts in your dashboard and I''m ready in 3 minutes.')
WHERE id = 'clara';  -- Esther, Email & SMS Marketing

UPDATE foundation.ai_employees
SET config = config || jsonb_build_object('connection_fallback', 'I need access to your Facebook & Instagram first — tap Connect Your Accounts in your dashboard and I''m ready in 3 minutes.')
WHERE id = 'kai';  -- Nathan, Social Media Manager

UPDATE foundation.ai_employees
SET config = config || jsonb_build_object('connection_fallback', 'I need access to your Calendar first — tap Connect Your Accounts in your dashboard and I''m ready in 3 minutes.')
WHERE id = 'sage';  -- Naomi, Scheduling & Appointments

UPDATE foundation.ai_employees
SET config = config || jsonb_build_object('connection_fallback', 'I need access to your Stripe account first — tap Connect Your Accounts in your dashboard and I''m ready in 3 minutes.')
WHERE id = 'joanna-finance';
