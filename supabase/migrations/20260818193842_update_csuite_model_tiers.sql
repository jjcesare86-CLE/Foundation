-- update_csuite_model_tiers
-- Batch 1 Phase 0: split the C-suite off the single legacy 'orchestrator'
-- model_tier value into the new orchestrator_max / complex tiers.
-- Idempotent: plain UPDATE ... WHERE, safe to re-run.

UPDATE foundation.ai_employees
SET model_tier = 'orchestrator_max', updated_at = NOW()
WHERE id = 'solomon-ceo';

UPDATE foundation.ai_employees
SET model_tier = 'complex', updated_at = NOW()
WHERE id IN ('caleb-coo', 'miriam-cfo', 'isaiah-cso', 'abigail-clo');
