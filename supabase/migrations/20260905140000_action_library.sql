-- action_library
-- Batch 1 Phase 2: the shared typed action library. First consumer is
-- Rahab (post_review_response); Zacchaeus, Silas, and GABRIEL (when
-- reactivated) reuse this same table and approval flow.

CREATE TABLE IF NOT EXISTS foundation.agent_actions (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  agent_id      TEXT REFERENCES foundation.ai_employees(id),
  client_id     UUID REFERENCES foundation.client_profiles(id),
  action_type   TEXT NOT NULL,
  status        TEXT NOT NULL DEFAULT 'pending'
                  CHECK (status IN ('pending','approved','rejected','executed','simulated','failed')),
  draft         JSONB NOT NULL DEFAULT '{}',   -- the human-editable proposed content
  payload       JSONB NOT NULL DEFAULT '{}',   -- structured params the executor needs (ids, refs)
  result        JSONB,                         -- executor's return value
  error         TEXT,
  requested_by  TEXT,                          -- 'cron' | 'agent' | a user identifier
  approved_by   TEXT,
  approved_at   TIMESTAMPTZ,
  executed_at   TIMESTAMPTZ,
  created_at    TIMESTAMPTZ DEFAULT NOW(),
  updated_at    TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_agent_actions_status ON foundation.agent_actions(status, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_agent_actions_agent ON foundation.agent_actions(agent_id, status);
CREATE INDEX IF NOT EXISTS idx_agent_actions_client ON foundation.agent_actions(client_id);

ALTER TABLE foundation.agent_actions ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "service_role_all_agent_actions" ON foundation.agent_actions;
CREATE POLICY "service_role_all_agent_actions"
  ON foundation.agent_actions FOR ALL
  USING (auth.role() = 'service_role');
