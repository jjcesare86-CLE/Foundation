-- caleb_ops_delegation_and_finance_labels
-- Data fixes: since Phase 0.5 (20260905120000) made Nehemiah COO and kept
-- Caleb as CISO, two prompt-facing text fields still pointed day-to-day
-- ops / tactical execution delegation at Caleb instead of the actual COO.
-- Scanned every row's outside_scope, helps, handoff_to, covers_for,
-- covered_by, supervises, and reports_to for any other CALEB reference in
-- an operations sense before writing this: none found. The other live
-- CALEB references are correct as-is and untouched by this migration --
--   * solomon-ceo.handoff_to / .supervises include caleb-coo: legitimate
--     org-chart entries (Caleb is still Solomon's direct report as CISO).
--   * vince.reports_to = 'caleb-coo': Ezra reporting to Caleb is explicit,
--     unchanged Phase 0.5 policy (00_STATE_OF_THE_BUILD.md §2).
--   * nehemiah-coo.outside_scope ("...security concerns -- redirect to
--     CALEB") and .handoff_to: correct -- security is Caleb's actual
--     domain as CISO, this is not an ops/tactical delegation.

UPDATE foundation.ai_employees
SET outside_scope = 'Day-to-day ops — delegate to NEHEMIAH',
    updated_at = NOW()
WHERE id = 'solomon-ceo'
  AND outside_scope LIKE '%CALEB%';

UPDATE foundation.ai_employees
SET outside_scope = 'Tactical execution — redirect to NEHEMIAH',
    updated_at = NOW()
WHERE id = 'isaiah-cso'
  AND outside_scope LIKE '%CALEB%';

UPDATE foundation.ai_employees
SET department_label = 'Finance',
    updated_at = NOW()
WHERE id IN ('fin', 'joanna-finance')
  AND department_label IS DISTINCT FROM 'Finance';
