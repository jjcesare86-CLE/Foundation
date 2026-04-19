-- 009_create_ai_employees.sql
-- Foundation AI Employees — single source of truth for all platforms
-- Safe to run whether or not foundation.ai_employees already exists

-- ── Main employees table ──────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS foundation.ai_employees (
  id               TEXT PRIMARY KEY,
  name             TEXT NOT NULL,
  biblical_name    TEXT,
  product_name     TEXT,
  role             TEXT NOT NULL,
  department       TEXT NOT NULL,
  department_label TEXT NOT NULL,
  model_tier       TEXT NOT NULL DEFAULT 'standard',
  tier_access      TEXT NOT NULL DEFAULT 'All',
  is_csuite        BOOLEAN DEFAULT FALSE,
  is_confidential  BOOLEAN DEFAULT FALSE,
  style            TEXT,
  helps            TEXT,
  outside_scope    TEXT,
  system_prompt    TEXT,
  handoff_to       TEXT[] DEFAULT '{}',
  covers_for       TEXT[] DEFAULT '{}',
  covered_by       TEXT[] DEFAULT '{}',
  reports_to       TEXT,
  supervises       TEXT[] DEFAULT '{}',
  color            TEXT,
  bg               TEXT,
  config           JSONB DEFAULT '{}',
  is_active        BOOLEAN DEFAULT TRUE,
  created_at       TIMESTAMPTZ DEFAULT NOW(),
  updated_at       TIMESTAMPTZ DEFAULT NOW()
);

-- Safe column additions if table already existed with fewer columns
ALTER TABLE foundation.ai_employees
  ADD COLUMN IF NOT EXISTS biblical_name    TEXT,
  ADD COLUMN IF NOT EXISTS product_name     TEXT,
  ADD COLUMN IF NOT EXISTS model_tier       TEXT NOT NULL DEFAULT 'standard',
  ADD COLUMN IF NOT EXISTS tier_access      TEXT NOT NULL DEFAULT 'All',
  ADD COLUMN IF NOT EXISTS is_csuite        BOOLEAN DEFAULT FALSE,
  ADD COLUMN IF NOT EXISTS is_confidential  BOOLEAN DEFAULT FALSE,
  ADD COLUMN IF NOT EXISTS reports_to       TEXT,
  ADD COLUMN IF NOT EXISTS supervises       TEXT[] DEFAULT '{}',
  ADD COLUMN IF NOT EXISTS config           JSONB DEFAULT '{}';

-- ── Platform subscriptions ────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS foundation.employee_platform_subscriptions (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  platform_slug   TEXT NOT NULL,
  employee_id     TEXT NOT NULL REFERENCES foundation.ai_employees(id),
  is_active       BOOLEAN DEFAULT TRUE,
  config_override JSONB DEFAULT '{}',
  created_at      TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE(platform_slug, employee_id)
);

CREATE INDEX IF NOT EXISTS idx_emp_platform_slug
  ON foundation.employee_platform_subscriptions(platform_slug, is_active);

-- ── Eden private sessions ─────────────────────────────────────────────────
-- HARD RULE: NO foreign keys to identity, HR, or performance tables
CREATE TABLE IF NOT EXISTS foundation.eden_sessions (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  session_token   TEXT NOT NULL UNIQUE,
  platform_slug   TEXT NOT NULL,
  started_at      TIMESTAMPTZ DEFAULT NOW(),
  ended_at        TIMESTAMPTZ,
  message_count   INTEGER DEFAULT 0,
  escalation_flag BOOLEAN DEFAULT FALSE
);

COMMENT ON TABLE foundation.eden_sessions IS
  'Headspace Counselor sessions. Fully anonymous. No FK to HR or identity. NEVER JOIN.';

-- ── Sync log ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS foundation.employee_sync_log (
  id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  platform_slug  TEXT NOT NULL,
  synced_at      TIMESTAMPTZ DEFAULT NOW(),
  employee_count INTEGER,
  sync_status    TEXT DEFAULT 'success',
  notes          TEXT
);

-- ── RLS ───────────────────────────────────────────────────────────────────
ALTER TABLE foundation.ai_employees ENABLE ROW LEVEL SECURITY;
ALTER TABLE foundation.employee_platform_subscriptions ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "public_read_employees" ON foundation.ai_employees;
CREATE POLICY "public_read_employees"
  ON foundation.ai_employees FOR SELECT USING (true);

DROP POLICY IF EXISTS "public_read_subscriptions" ON foundation.employee_platform_subscriptions;
CREATE POLICY "public_read_subscriptions"
  ON foundation.employee_platform_subscriptions FOR SELECT USING (true);
