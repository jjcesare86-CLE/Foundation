-- php_shield_schema
-- PHP Shield: free scan -> report -> paid fix -> maintenance funnel.
-- One row per lead captured when /php-shield/report is called with a contact_email.

CREATE TABLE IF NOT EXISTS foundation.php_shield_leads (
  id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  url                 TEXT NOT NULL,
  site_name           TEXT,
  contact_email       TEXT,
  php_version         TEXT,
  risk_level          TEXT,
  confidence          TEXT,
  status              TEXT NOT NULL DEFAULT 'new',
  quoted_price_cents  INTEGER,
  created_at          TIMESTAMPTZ DEFAULT NOW(),
  updated_at          TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_php_shield_leads_status
  ON foundation.php_shield_leads(status, created_at DESC);

ALTER TABLE foundation.php_shield_leads ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "service_role_all_php_shield_leads" ON foundation.php_shield_leads;
CREATE POLICY "service_role_all_php_shield_leads"
  ON foundation.php_shield_leads FOR ALL
  USING (auth.role() = 'service_role');
