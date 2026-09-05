-- obadiah_agent
-- Batch 2, Agent 30: OBADIAH — Property & Tenant Manager. Seed: Broker Broker Realty.

INSERT INTO foundation.client_profiles (business_name, industry, onboarding_platform, status)
SELECT 'Broker Broker Realty', 'real_estate', 'automation-nation', 'active'
WHERE NOT EXISTS (SELECT 1 FROM foundation.client_profiles WHERE business_name = 'Broker Broker Realty');

INSERT INTO foundation.ai_employees (
  id, name, biblical_name, product_name, role, department, department_label,
  model_tier, tier_access, is_csuite, is_confidential, style, helps,
  outside_scope, handoff_to, covers_for, covered_by, reports_to, supervises,
  color, bg, config, is_active, system_prompt
) VALUES (
  'obadiah-property', 'OBI', 'Obadiah', 'Obadiah', 'Property & Tenant Manager',
  'operations', 'Operations', 'standard', 'Professional+', FALSE, FALSE,
  'Steady & thorough',
  'Rent reminders, maintenance-ticket intake and vendor/Silas dispatch, lease renewal tracking, tenant communication, owner statements',
  'Field crew scheduling itself — redirect to SILAS; invoicing — redirect to JOANNA; review requests are automatic (handoff to RAE)',
  ARRAY['silas-dispatch','joanna-finance','rahab-reputation'], ARRAY[]::text[], ARRAY[]::text[],
  'nehemiah-coo', ARRAY[]::text[],
  '#D85A30', '#FAECE7', '{}'::jsonb, TRUE,
$prompt$You are Obadiah, the Property & Tenant Manager for {business_name}. Steward of the
king's house — you keep units filled, rent on time, and tenants heard.

PERSONALITY: Steady, thorough, fair to both owner and tenant. You document everything;
you never let a verbal promise become a dispute later.

YOUR JOB:
1. Rent reminders: T-5 days before due, on due date, and a firm-but-fair late notice at
   T+3 if unpaid — always in plain language, always with the exact amount and how to pay.
2. Maintenance intake: log every request with unit, issue, urgency, and photos if sent.
   Route anything requiring a field visit to Silas as a dispatch job with the unit
   address and access notes. Safety-critical issues (gas smell, no heat in winter,
   flooding) escalate to the owner immediately, never queued normally.
3. Lease renewal tracking: flag leases expiring in 90/60/30 days; draft the renewal
   offer for owner approval before it goes to the tenant.
4. Owner statements: monthly summary per property — rent collected, vacancies,
   maintenance spend, upcoming renewals.
5. Tenant communication: professional, empathetic, never legal-sounding threats —
   that's the owner's or an attorney's call, not yours.

HARD RULES:
- Never promise a repair timeline you can't confirm with Silas or a vendor first.
- Never discuss one tenant's situation with another tenant.
- Fair housing: never let any recommendation reference a protected class. If a request
  brushes against fair-housing territory, flag it to the owner instead of acting.
- Rent amounts and lease terms are set by the owner; you enforce and remind, you don't renegotiate.

DATA ACCESS: via connection_broker (GHL contacts/SMS for tenant comms). Missing →
"I need {service} connected first — Connect Your Accounts in your dashboard."

HANDOFFS: field dispatch → Silas, invoicing → Joanna, review requests → Rahab (auto
on completed maintenance visits).$prompt$
)
ON CONFLICT (id) DO UPDATE SET
  role = EXCLUDED.role, helps = EXCLUDED.helps, outside_scope = EXCLUDED.outside_scope,
  handoff_to = EXCLUDED.handoff_to, system_prompt = EXCLUDED.system_prompt,
  updated_at = NOW();

INSERT INTO foundation.employee_platform_subscriptions (platform_slug, employee_id, is_active)
SELECT DISTINCT platform_slug, 'obadiah-property', TRUE
FROM foundation.employee_platform_subscriptions
ON CONFLICT (platform_slug, employee_id) DO NOTHING;

UPDATE foundation.ai_employees SET required_capabilities = '["ghl"]'::jsonb WHERE id = 'obadiah-property';

CREATE TABLE IF NOT EXISTS foundation.ob_units (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  client_id     UUID NOT NULL REFERENCES foundation.client_profiles(id),
  unit_label    TEXT NOT NULL,       -- "123 Main St, Unit 2B"
  bedrooms      INT,
  monthly_rent  NUMERIC(10,2),
  status        TEXT DEFAULT 'occupied' CHECK (status IN ('occupied','vacant','maintenance_hold'))
);

CREATE TABLE IF NOT EXISTS foundation.ob_leases (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  client_id       UUID NOT NULL REFERENCES foundation.client_profiles(id),
  unit_id         UUID NOT NULL REFERENCES foundation.ob_units(id),
  tenant_name     TEXT NOT NULL,
  tenant_contact_id TEXT,           -- GHL contact
  start_date      DATE NOT NULL,
  end_date        DATE NOT NULL,
  monthly_rent    NUMERIC(10,2) NOT NULL,
  status          TEXT DEFAULT 'active' CHECK (status IN ('active','renewal_pending','expired','terminated')),
  last_rent_reminder_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_ob_leases_end_date ON foundation.ob_leases(end_date, status);

CREATE TABLE IF NOT EXISTS foundation.ob_maintenance_tickets (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  client_id     UUID NOT NULL REFERENCES foundation.client_profiles(id),
  unit_id       UUID NOT NULL REFERENCES foundation.ob_units(id),
  issue         TEXT NOT NULL,
  urgency       TEXT DEFAULT 'normal' CHECK (urgency IN ('normal','urgent','safety_critical')),
  status        TEXT DEFAULT 'open' CHECK (status IN ('open','dispatched','resolved')),
  silas_job_id  UUID,               -- foundation.fs_jobs(id) once dispatched, no hard FK (cross-agent, optional)
  created_at    TIMESTAMPTZ DEFAULT NOW(),
  resolved_at   TIMESTAMPTZ
);

ALTER TABLE foundation.ob_units ENABLE ROW LEVEL SECURITY;
ALTER TABLE foundation.ob_leases ENABLE ROW LEVEL SECURITY;
ALTER TABLE foundation.ob_maintenance_tickets ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "service_role_all_ob_units" ON foundation.ob_units;
CREATE POLICY "service_role_all_ob_units" ON foundation.ob_units FOR ALL USING (auth.role() = 'service_role');
DROP POLICY IF EXISTS "service_role_all_ob_leases" ON foundation.ob_leases;
CREATE POLICY "service_role_all_ob_leases" ON foundation.ob_leases FOR ALL USING (auth.role() = 'service_role');
DROP POLICY IF EXISTS "service_role_all_ob_maintenance_tickets" ON foundation.ob_maintenance_tickets;
CREATE POLICY "service_role_all_ob_maintenance_tickets" ON foundation.ob_maintenance_tickets FOR ALL USING (auth.role() = 'service_role');

-- Seed: 4 units, 3 active leases, 1 vacant, for Broker Broker Realty.
DO $$
DECLARE
  v_client_id UUID;
  v_unit1 UUID; v_unit2 UUID; v_unit3 UUID; v_unit4 UUID;
BEGIN
  SELECT id INTO v_client_id FROM foundation.client_profiles WHERE business_name = 'Broker Broker Realty';
  IF NOT EXISTS (SELECT 1 FROM foundation.ob_units WHERE client_id = v_client_id) THEN
    INSERT INTO foundation.ob_units (client_id, unit_label, bedrooms, monthly_rent, status)
    VALUES (v_client_id, '123 Main St, Unit 1A', 2, 1450, 'occupied') RETURNING id INTO v_unit1;
    INSERT INTO foundation.ob_units (client_id, unit_label, bedrooms, monthly_rent, status)
    VALUES (v_client_id, '123 Main St, Unit 2B', 1, 1100, 'occupied') RETURNING id INTO v_unit2;
    INSERT INTO foundation.ob_units (client_id, unit_label, bedrooms, monthly_rent, status)
    VALUES (v_client_id, '456 Oak Ave, Unit 1', 3, 1800, 'occupied') RETURNING id INTO v_unit3;
    INSERT INTO foundation.ob_units (client_id, unit_label, bedrooms, monthly_rent, status)
    VALUES (v_client_id, '456 Oak Ave, Unit 2', 2, 1500, 'vacant') RETURNING id INTO v_unit4;

    INSERT INTO foundation.ob_leases (client_id, unit_id, tenant_name, start_date, end_date, monthly_rent)
    VALUES
      (v_client_id, v_unit1, 'Jordan Ellis', CURRENT_DATE - INTERVAL '10 months', CURRENT_DATE + INTERVAL '25 days', 1450),
      (v_client_id, v_unit2, 'Priya Nair', CURRENT_DATE - INTERVAL '4 months', CURRENT_DATE + INTERVAL '8 months', 1100),
      (v_client_id, v_unit3, 'The Alvarez Family', CURRENT_DATE - INTERVAL '2 years', CURRENT_DATE + INTERVAL '3 months', 1800);

    INSERT INTO foundation.ob_maintenance_tickets (client_id, unit_id, issue, urgency, status)
    VALUES (v_client_id, v_unit1, 'Kitchen faucet leaking', 'normal', 'open');
  END IF;
END $$;
