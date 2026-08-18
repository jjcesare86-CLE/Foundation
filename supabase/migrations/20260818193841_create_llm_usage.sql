-- create_llm_usage
-- Foundation llm_router.py cost/usage log — one row per LLM call.
-- Safe to run whether or not foundation.llm_usage already exists.

CREATE TABLE IF NOT EXISTS foundation.llm_usage (
  id                           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project                      TEXT NOT NULL,          -- 'foundation' | 'AN' | 'VoiceMIO' | 'BlastVideo' | 'MRLIN'
  agent_name                   TEXT,
  model                        TEXT NOT NULL,
  tier                         TEXT NOT NULL,
  input_tokens                 INT NOT NULL DEFAULT 0,
  output_tokens                INT NOT NULL DEFAULT 0,
  cache_read_input_tokens      INT NOT NULL DEFAULT 0,
  cache_creation_input_tokens  INT NOT NULL DEFAULT 0,
  estimated_cost_usd           NUMERIC(12,6) NOT NULL DEFAULT 0,
  task_type                    TEXT,
  fallback_from                TEXT,                   -- set when a fable-5 safeguard reroute occurred
  created_at                   TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_llm_usage_project_agent_created
  ON foundation.llm_usage(project, agent_name, created_at DESC);

-- ── RLS — service-role-only, no public read (cost/usage data) ─────────────
ALTER TABLE foundation.llm_usage ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "service_role_all_llm_usage" ON foundation.llm_usage;
CREATE POLICY "service_role_all_llm_usage"
  ON foundation.llm_usage FOR ALL
  USING (auth.role() = 'service_role');
