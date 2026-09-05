-- ops_audit_schema
-- Ops Audit Part A: required_capabilities column + agent_jobs registry.

ALTER TABLE foundation.ai_employees
  ADD COLUMN IF NOT EXISTS required_capabilities JSONB DEFAULT '[]'::jsonb;

-- Backfill per A.2's examples plus a reasonable inference for the rest of
-- the roster. Pure-LLM agents (no external integration touched by anything
-- built so far) get []. Update as real integrations land.
UPDATE foundation.ai_employees SET required_capabilities = '["ghl"]'::jsonb WHERE id IN ('rahab-reputation', 'dean', 'aria', 'sage');
UPDATE foundation.ai_employees SET required_capabilities = '["ghl_social"]'::jsonb WHERE id = 'kai';
UPDATE foundation.ai_employees SET required_capabilities = '["stripe_read"]'::jsonb WHERE id IN ('zacchaeus-books', 'fin');
UPDATE foundation.ai_employees SET required_capabilities = '["stripe"]'::jsonb WHERE id = 'joanna-finance';
UPDATE foundation.ai_employees SET required_capabilities = '["ghl"]'::jsonb WHERE id = 'clara';
UPDATE foundation.ai_employees SET required_capabilities = '["ghl","maps","gps_feed"]'::jsonb WHERE id = 'silas-dispatch';
-- Everyone else keeps the [] default (solomon-ceo, nehemiah-coo, caleb-coo,
-- miriam-cfo, isaiah-cso, abigail-clo, rex, ace, blake, maya, nina, drew,
-- otto, martha-admin, vince, ori, eden-headspace, leah-exec-asst, leo,
-- rebekah-legal).

CREATE TABLE IF NOT EXISTS foundation.agent_jobs (
  id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  agent_slug          TEXT NOT NULL REFERENCES foundation.ai_employees(id),
  job_name            TEXT NOT NULL,
  schedule_cron       TEXT NOT NULL,
  schedule_interval_minutes INT NOT NULL,   -- parsed once at registration, avoids a cron-parser dependency at read time
  last_run_at         TIMESTAMPTZ,
  last_status         TEXT CHECK (last_status IN ('success','failed') OR last_status IS NULL),
  last_detail         TEXT,
  UNIQUE (agent_slug, job_name)
);

ALTER TABLE foundation.agent_jobs ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "service_role_all_agent_jobs" ON foundation.agent_jobs;
CREATE POLICY "service_role_all_agent_jobs" ON foundation.agent_jobs FOR ALL
  USING (auth.role() = 'service_role');

-- Register the four crons that exist today.
INSERT INTO foundation.agent_jobs (agent_slug, job_name, schedule_cron, schedule_interval_minutes)
VALUES
  ('rahab-reputation', 'rahab-review-ingestion', '0 8-20/2 * * *', 120),
  ('rahab-reputation', 'rahab-spike-check', '0 6 * * *', 1440),
  ('zacchaeus-books', 'zacchaeus-daily', '0 7 * * *', 1440),
  ('silas-dispatch', 'silas-dispatch-builder', '30 5 * * *', 1440)
ON CONFLICT (agent_slug, job_name) DO NOTHING;
