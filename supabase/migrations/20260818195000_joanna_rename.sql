-- joanna_rename
-- Batch 1 Phase 1: rename Foundation #17 (Finance & Invoicing) from Lydia to
-- Joanna. The Shopify LYDIA commerce agent is untouched by this migration —
-- it lives outside foundation.ai_employees entirely.

ALTER TABLE foundation.ai_employees ADD COLUMN IF NOT EXISTS legacy_slug TEXT;

-- Repoint the employee_platform_subscriptions FK to cascade on id rename,
-- so renaming the ai_employees primary key doesn't orphan its subscription
-- rows. Looked up dynamically since the constraint name was never set
-- explicitly in migration 009 (Postgres auto-generated it).
DO $$
DECLARE
  fk_name TEXT;
BEGIN
  SELECT conname INTO fk_name
  FROM pg_constraint
  WHERE conrelid = 'foundation.employee_platform_subscriptions'::regclass
    AND contype = 'f'
    AND confrelid = 'foundation.ai_employees'::regclass;

  IF fk_name IS NOT NULL THEN
    EXECUTE format('ALTER TABLE foundation.employee_platform_subscriptions DROP CONSTRAINT %I', fk_name);
  END IF;

  ALTER TABLE foundation.employee_platform_subscriptions
    ADD CONSTRAINT employee_platform_subscriptions_employee_id_fkey
    FOREIGN KEY (employee_id) REFERENCES foundation.ai_employees(id) ON UPDATE CASCADE;
END $$;

-- The rename itself. legacy_slug preserves 'lydia-finance' for API-level
-- alias resolution (see app/app/routers/employees.py). Cascades to
-- employee_platform_subscriptions.employee_id automatically.
UPDATE foundation.ai_employees
SET id = 'joanna-finance',
    name = 'JOANNA',
    biblical_name = 'Joanna',
    legacy_slug = 'lydia-finance',
    updated_at = NOW()
WHERE id = 'lydia-finance';

-- Fix up the two agents that redirect to Lydia by name in their
-- outside_scope copy and handoff/coverage arrays.
UPDATE foundation.ai_employees
SET outside_scope = replace(outside_scope, 'redirect to LYDIA', 'redirect to JOANNA'),
    updated_at = NOW()
WHERE id IN ('fin', 'miriam-cfo')
  AND outside_scope LIKE '%redirect to LYDIA%';

UPDATE foundation.ai_employees
SET handoff_to = array_replace(handoff_to, 'lydia-finance', 'joanna-finance'),
    covers_for = array_replace(covers_for, 'lydia-finance', 'joanna-finance'),
    covered_by = array_replace(covered_by, 'lydia-finance', 'joanna-finance'),
    supervises = array_replace(supervises, 'lydia-finance', 'joanna-finance'),
    updated_at = NOW()
WHERE 'lydia-finance' = ANY(handoff_to)
   OR 'lydia-finance' = ANY(covers_for)
   OR 'lydia-finance' = ANY(covered_by)
   OR 'lydia-finance' = ANY(supervises);
