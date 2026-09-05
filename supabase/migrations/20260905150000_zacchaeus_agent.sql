-- zacchaeus_agent
-- Batch 1 Phase 3, Agent 27: ZACCHAEUS — Tax & Bookkeeping Specialist.
-- Seed clients: Delivered Fireworks, LUTS.

INSERT INTO foundation.client_profiles (business_name, industry, onboarding_platform, status)
SELECT 'Delivered Fireworks', 'fireworks', 'automation-nation', 'active'
WHERE NOT EXISTS (SELECT 1 FROM foundation.client_profiles WHERE business_name = 'Delivered Fireworks');

INSERT INTO foundation.client_profiles (business_name, industry, onboarding_platform, status)
SELECT 'LUTS', 'fireworks', 'automation-nation', 'active'
WHERE NOT EXISTS (SELECT 1 FROM foundation.client_profiles WHERE business_name = 'LUTS');

INSERT INTO foundation.ai_employees (
  id, name, biblical_name, product_name, role, department, department_label,
  model_tier, tier_access, is_csuite, is_confidential, style, helps,
  outside_scope, handoff_to, covers_for, covered_by, reports_to, supervises,
  color, bg, config, is_active, system_prompt
) VALUES (
  'zacchaeus-books', 'ZACH', 'Zacchaeus', 'Zacchaeus', 'Tax & Bookkeeping Specialist',
  'finance', 'Finance', 'standard', 'Professional+', FALSE, FALSE,
  'Meticulous & redemptive',
  'Receipt/expense categorization, monthly reconciliation summaries, quarterly estimated-tax calculations and deadline reminders, sales-tax nexus tracking, 1099 contractor threshold tracking, mileage log summaries, year-end CPA handoff packages, anomaly flagging',
  'Invoicing or AR — redirect to JOANNA; financial modeling or forecasting — redirect to MIRIAM; legal tax disputes — redirect to ABIGAIL',
  ARRAY['joanna-finance','miriam-cfo','abigail-clo'], ARRAY[]::text[], ARRAY[]::text[],
  'miriam-cfo', ARRAY[]::text[],
  '#D85A30', '#FAECE7', '{}'::jsonb, TRUE,
$prompt$You are Zacchaeus, the Tax & Bookkeeping Specialist for {business_name}. Once a tax
collector, now redeemed — your whole purpose is making sure {business_name} keeps every
dollar it's legally entitled to and never gets surprised by a tax deadline.

PERSONALITY: Meticulous, warm, lightly self-deprecating about your past profession.
Plain English always — say "money you owe the IRS in September" not "Q3 estimated
liability." Numbers are always exact; never round silently.

YOUR JOB:
1. Categorize every expense and receipt into the chart of accounts for a
   {industry} business. When unsure, ask ONE short question rather than guessing.
2. Track quarterly estimated-tax deadlines (Apr 15, Jun 15, Sep 15, Jan 15) and
   compute estimates from YTD profit. Remind at T-30, T-7, T-1 days.
3. Watch 1099 contractor payments; flag anyone crossing $600 YTD.
4. Track sales-tax nexus: flag when revenue into any state approaches economic
   nexus thresholds.
5. Produce a monthly books summary: income, expenses by category, profit, anomalies,
   and one plain-English insight.
6. Build the year-end CPA package: clean ledger, P&L, categorized totals, open items.

HARD RULES:
- You PREPARE and ORGANIZE. You never file, and you never present anything as formal
  tax or legal advice. Every deliverable ends with: "Have your CPA review before filing."
- Never invent a number. If data is missing, list exactly what you need.
- Anomalies get flagged, never silently 'fixed'.
- If asked about tax strategy or disputes, give the factual lay of the land, then
  route: strategy → Miriam (CFO), disputes → Abigail (CLO).

DATA ACCESS: via connection_broker only (Stripe read, bank feed read, receipt uploads).
If a needed connection is missing, say: "I need access to your {service} first — tap
Connect Your Accounts in your dashboard and I'm ready in 3 minutes."

HANDOFFS: invoicing/AR → Joanna, forecasting → Miriam, legal → Abigail.$prompt$
)
ON CONFLICT (id) DO UPDATE SET
  role = EXCLUDED.role, helps = EXCLUDED.helps, outside_scope = EXCLUDED.outside_scope,
  handoff_to = EXCLUDED.handoff_to, system_prompt = EXCLUDED.system_prompt,
  updated_at = NOW();

INSERT INTO foundation.employee_platform_subscriptions (platform_slug, employee_id, is_active)
SELECT DISTINCT platform_slug, 'zacchaeus-books', TRUE
FROM foundation.employee_platform_subscriptions
ON CONFLICT (platform_slug, employee_id) DO NOTHING;

-- ── Books ───────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS foundation.zb_transactions (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  client_id       UUID NOT NULL REFERENCES foundation.client_profiles(id),
  occurred_at     DATE NOT NULL,
  amount          NUMERIC(12,2) NOT NULL,
  direction       TEXT NOT NULL CHECK (direction IN ('income','expense')),
  source          TEXT,                              -- stripe | bank | manual | receipt_upload
  raw_description TEXT,
  category        TEXT,                               -- chart-of-accounts key
  categorized_by  TEXT DEFAULT 'uncategorized',        -- uncategorized | zacchaeus | needs_clarification | human_override
  confidence      NUMERIC(3,2),
  anomaly_flag    BOOLEAN DEFAULT FALSE,
  notes           TEXT,
  created_at      TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_zb_transactions_client_cat ON foundation.zb_transactions(client_id, categorized_by);

CREATE TABLE IF NOT EXISTS foundation.zb_tax_deadlines (
  id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  client_id         UUID NOT NULL REFERENCES foundation.client_profiles(id),
  deadline_type     TEXT NOT NULL,                     -- quarterly_est | 1099 | sales_tax | custom
  jurisdiction      TEXT DEFAULT 'federal',
  due_date          DATE NOT NULL,
  estimated_amount  NUMERIC(12,2),
  status            TEXT DEFAULT 'upcoming' CHECK (status IN ('upcoming','reminded','done','missed')),
  reminders_sent    INT DEFAULT 0,
  UNIQUE (client_id, deadline_type, jurisdiction, due_date)
);

CREATE INDEX IF NOT EXISTS idx_zb_tax_deadlines_due ON foundation.zb_tax_deadlines(due_date, status);

CREATE TABLE IF NOT EXISTS foundation.zb_contractors (
  id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  client_id           UUID NOT NULL REFERENCES foundation.client_profiles(id),
  contractor_name     TEXT NOT NULL,
  ytd_paid            NUMERIC(12,2) DEFAULT 0,
  tax_year            INT NOT NULL,
  w9_on_file          BOOLEAN DEFAULT FALSE,
  threshold_flagged   BOOLEAN DEFAULT FALSE,
  UNIQUE (client_id, contractor_name, tax_year)
);

ALTER TABLE foundation.zb_transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE foundation.zb_tax_deadlines ENABLE ROW LEVEL SECURITY;
ALTER TABLE foundation.zb_contractors ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "service_role_all_zb_transactions" ON foundation.zb_transactions;
CREATE POLICY "service_role_all_zb_transactions" ON foundation.zb_transactions FOR ALL
  USING (auth.role() = 'service_role');

DROP POLICY IF EXISTS "service_role_all_zb_tax_deadlines" ON foundation.zb_tax_deadlines;
CREATE POLICY "service_role_all_zb_tax_deadlines" ON foundation.zb_tax_deadlines FOR ALL
  USING (auth.role() = 'service_role');

DROP POLICY IF EXISTS "service_role_all_zb_contractors" ON foundation.zb_contractors;
CREATE POLICY "service_role_all_zb_contractors" ON foundation.zb_contractors FOR ALL
  USING (auth.role() = 'service_role');

-- Seed the four federal quarterly estimated-tax deadlines for the current
-- tax year, per client. Idempotent via the UNIQUE constraint above.
INSERT INTO foundation.zb_tax_deadlines (client_id, deadline_type, jurisdiction, due_date)
SELECT cp.id, 'quarterly_est', 'federal', d.due_date
FROM foundation.client_profiles cp
CROSS JOIN (VALUES ('2026-04-15'::date), ('2026-06-15'::date), ('2026-09-15'::date), ('2027-01-15'::date)) AS d(due_date)
WHERE cp.business_name IN ('Delivered Fireworks', 'LUTS')
ON CONFLICT (client_id, deadline_type, jurisdiction, due_date) DO NOTHING;
