-- caleb_ciso_nehemiah_coo
-- Batch 1 Phase 0.5: Caleb becomes CISO, Nehemiah joins as COO.
-- Keeps caleb-coo's id unchanged (nothing referencing it breaks) even
-- though the role is no longer COO — per spec, safer than a PK rename.

-- Caleb: COO -> CISO
UPDATE foundation.ai_employees
SET role = 'Chief Information Security Officer',
    style = 'Vigilant & systematic',
    helps = 'Inbound mail/message triage (hold-and-ask on suspicious senders, look-alike domains, disguised executables), credential and token hygiene across the Connections Hub, access reviews on Switchboard workspace membership changes, security-weighted compliance escalations from Amos, plain-English incident write-ups',
    outside_scope = 'Operational strategy or KPI tracking — redirect to NEHEMIAH; financial modeling — redirect to MIRIAM',
    handoff_to = ARRAY['vince','leo','abigail-clo','nehemiah-coo','solomon-ceo'],
    supervises = ARRAY['vince'],
    updated_at = NOW()
WHERE id = 'caleb-coo';

-- Nehemiah: new COO row
INSERT INTO foundation.ai_employees (
  id, name, biblical_name, product_name, role, department, department_label,
  model_tier, tier_access, is_csuite, is_confidential, style, helps,
  outside_scope, handoff_to, covers_for, covered_by, reports_to, supervises,
  color, bg, config, is_active
) VALUES (
  'nehemiah-coo', 'NEHEMIAH', 'Nehemiah', 'Nehemiah', 'Chief Operating Officer',
  'csuite', 'C-Suite', 'complex', 'Enterprise', TRUE, FALSE,
  'Organized & mobilizing',
  'Strategy-to-execution translation, KPI tracking, blocker removal, operational oversight, department coordination',
  'Financial modeling — redirect to MIRIAM; security concerns — redirect to CALEB',
  ARRAY['miriam-cfo','caleb-coo','solomon-ceo','otto'],
  ARRAY[]::text[], ARRAY[]::text[],
  'solomon-ceo',
  ARRAY['otto','ori','leah-exec-asst','martha-admin'],
  '#7F77DD', '#EEEDFE', '{}'::jsonb, TRUE
)
ON CONFLICT (id) DO UPDATE SET
  role = EXCLUDED.role,
  helps = EXCLUDED.helps,
  outside_scope = EXCLUDED.outside_scope,
  handoff_to = EXCLUDED.handoff_to,
  reports_to = EXCLUDED.reports_to,
  supervises = EXCLUDED.supervises,
  updated_at = NOW();

-- Reassign Caleb's former COO-line direct reports to Nehemiah.
-- Ezra (id 'vince') explicitly stays under Caleb per spec — not touched here.
UPDATE foundation.ai_employees
SET reports_to = 'nehemiah-coo', updated_at = NOW()
WHERE id IN ('otto', 'ori', 'leah-exec-asst', 'martha-admin')
  AND reports_to = 'caleb-coo';

-- Leah's handoff previously pointed at Caleb for operational matters; she
-- now reports to Nehemiah, so redirect that handoff accordingly.
UPDATE foundation.ai_employees
SET handoff_to = array_replace(handoff_to, 'caleb-coo', 'nehemiah-coo'),
    updated_at = NOW()
WHERE id = 'leah-exec-asst'
  AND 'caleb-coo' = ANY(handoff_to);

-- Solomon: add Nehemiah alongside the existing C-suite handoffs/reports.
-- The WHERE guard means handoff_to/supervises are known not to contain it
-- yet, so a plain append preserves existing order without a dedupe dance.
UPDATE foundation.ai_employees
SET handoff_to = handoff_to || ARRAY['nehemiah-coo'],
    supervises = supervises || ARRAY['nehemiah-coo'],
    updated_at = NOW()
WHERE id = 'solomon-ceo'
  AND NOT ('nehemiah-coo' = ANY(handoff_to));

-- Nehemiah gets the same platform subscriptions Caleb has.
INSERT INTO foundation.employee_platform_subscriptions (platform_slug, employee_id, is_active, config_override)
SELECT platform_slug, 'nehemiah-coo', is_active, config_override
FROM foundation.employee_platform_subscriptions
WHERE employee_id = 'caleb-coo'
ON CONFLICT (platform_slug, employee_id) DO NOTHING;
