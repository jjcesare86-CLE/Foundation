-- proof_of_work_schema
-- Item E, Part 2 §2.2: extend agent_actions (built in Batch 1 Phase 2)
-- rather than duplicating, plus agent_task_receipts for per-item evidence
-- on multi-target tasks (campaigns, batches) that a single action row
-- can't express well.

ALTER TABLE foundation.agent_actions
  ADD COLUMN IF NOT EXISTS claimed_outcome TEXT,
  ADD COLUMN IF NOT EXISTS verify_method TEXT,        -- api_response | db_read | webhook | none
  ADD COLUMN IF NOT EXISTS evidence JSONB,             -- external ids, status codes, counts
  ADD COLUMN IF NOT EXISTS verified_at TIMESTAMPTZ,
  ADD COLUMN IF NOT EXISTS verification_status TEXT DEFAULT 'pending';

DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_constraint
    WHERE conrelid = 'foundation.agent_actions'::regclass AND conname = 'agent_actions_verification_status_check'
  ) THEN
    ALTER TABLE foundation.agent_actions
      ADD CONSTRAINT agent_actions_verification_status_check
      CHECK (verification_status IN ('pending','verified','failed','partial','abandoned'));
  END IF;
END $$;

CREATE TABLE IF NOT EXISTS foundation.agent_task_receipts (
  id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  client_id         UUID NOT NULL REFERENCES foundation.client_profiles(id),
  agent_slug        TEXT NOT NULL REFERENCES foundation.ai_employees(id),
  task_ref          TEXT NOT NULL,          -- job/campaign/dispatch identifier
  intended_count    INT,                    -- what the agent set out to do
  completed_count   INT,                    -- what actually verified
  failed_count      INT DEFAULT 0,
  partial_reason    TEXT,                   -- why the gap exists, in plain English
  evidence          JSONB,                  -- per-item receipts (ids, statuses)
  reported_to_client BOOLEAN DEFAULT FALSE,
  created_at        TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_agent_task_receipts_client ON foundation.agent_task_receipts(client_id, agent_slug);

ALTER TABLE foundation.agent_task_receipts ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "service_role_all_agent_task_receipts" ON foundation.agent_task_receipts;
CREATE POLICY "service_role_all_agent_task_receipts" ON foundation.agent_task_receipts FOR ALL
  USING (auth.role() = 'service_role');
