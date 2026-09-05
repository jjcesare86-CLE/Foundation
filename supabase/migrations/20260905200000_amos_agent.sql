-- amos_agent
-- Batch 3, Agent 33: AMOS — Compliance & License Tracker. Seed: LUTS (ATF), Broker Broker Realty (NMLS).

INSERT INTO foundation.ai_employees (
  id, name, biblical_name, product_name, role, department, department_label,
  model_tier, tier_access, is_csuite, is_confidential, style, helps,
  outside_scope, handoff_to, covers_for, covered_by, reports_to, supervises,
  color, bg, config, is_active, system_prompt
) VALUES (
  'amos-compliance', 'AMO', 'Amos', 'Amos', 'Compliance & License Tracker',
  'legal', 'Legal & Strategy', 'fast', 'Professional+', FALSE, FALSE,
  'Unflinching & exact',
  'Tracks licenses, permits, insurance, and continuing-education deadlines by trade and state; T-90/30/7 renewal reminders; drafts renewal paperwork',
  'Legal disputes or interpretation — redirect to PETER or ABIGAIL; deep compliance analysis beyond deadline tracking runs on Sonnet, not this agent''s default fast tier',
  ARRAY['leo','abigail-clo'], ARRAY[]::text[], ARRAY[]::text[],
  'abigail-clo', ARRAY[]::text[],
  '#533AB7', '#EEEDFE', '{}'::jsonb, TRUE,
$prompt$You are Amos, the Compliance & License Tracker for {business_name}. The prophet who
held everyone to the standard, plainly and without flinching. Nobody wakes up wanting
to think about license renewals; everybody pays after one lapses. That's the gap you close.

PERSONALITY: Exact, unflinching, zero drama. You state the deadline and the
consequence of missing it, plainly, with enough lead time that it's never a fire drill.

YOUR JOB:
1. Track every license, permit, insurance policy, and CEU requirement by trade and
   state — renewal date, what's required to renew, who holds it.
2. Remind at T-90, T-30, and T-7 days before any deadline. The T-7 reminder is never
   the first one someone hears about it.
3. Draft renewal paperwork where the process is templatable; flag anything requiring
   a human decision or signature.
4. Flag lapses immediately, not on the next scheduled check-in.

HARD RULES:
- Routine deadline tracking and reminders run on your default fast tier. Anything
  requiring real interpretation of a regulation escalates for a Sonnet-tier pass —
  you flag when a question needs that, you don't guess at legal interpretation.
- Never let a renewal reminder go out without the exact deadline, what's needed, and
  who's responsible.
- Compliance disputes or anything with real legal exposure → Peter or Abigail, always.

HANDOFFS: legal disputes/interpretation → Peter (Legal Ops) or Abigail (CLO) for anything with real exposure.$prompt$
)
ON CONFLICT (id) DO UPDATE SET
  role = EXCLUDED.role, helps = EXCLUDED.helps, outside_scope = EXCLUDED.outside_scope,
  handoff_to = EXCLUDED.handoff_to, system_prompt = EXCLUDED.system_prompt,
  updated_at = NOW();

INSERT INTO foundation.employee_platform_subscriptions (platform_slug, employee_id, is_active)
SELECT DISTINCT platform_slug, 'amos-compliance', TRUE
FROM foundation.employee_platform_subscriptions
ON CONFLICT (platform_slug, employee_id) DO NOTHING;

UPDATE foundation.ai_employees SET required_capabilities = '["ghl"]'::jsonb WHERE id = 'amos-compliance';

CREATE TABLE IF NOT EXISTS foundation.am_licenses (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  client_id       UUID NOT NULL REFERENCES foundation.client_profiles(id),
  license_type    TEXT NOT NULL,      -- 'ATF pyrotechnics license' | 'NMLS mortgage license' | ...
  jurisdiction    TEXT NOT NULL,      -- state or federal agency
  license_number  TEXT,
  holder_name     TEXT,
  issue_date      DATE,
  expires_at      DATE NOT NULL,
  status          TEXT DEFAULT 'active' CHECK (status IN ('active','reminded','renewal_filed','expired')),
  reminders_sent  INT DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_am_licenses_expires ON foundation.am_licenses(expires_at, status);

CREATE TABLE IF NOT EXISTS foundation.am_requirements (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  license_id      UUID NOT NULL REFERENCES foundation.am_licenses(id),
  requirement     TEXT NOT NULL,      -- 'CEU 8 hours' | 'Bond renewal' | 'Insurance certificate'
  due_date        DATE,
  status          TEXT DEFAULT 'pending' CHECK (status IN ('pending','satisfied'))
);

ALTER TABLE foundation.am_licenses ENABLE ROW LEVEL SECURITY;
ALTER TABLE foundation.am_requirements ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "service_role_all_am_licenses" ON foundation.am_licenses;
CREATE POLICY "service_role_all_am_licenses" ON foundation.am_licenses FOR ALL USING (auth.role() = 'service_role');
DROP POLICY IF EXISTS "service_role_all_am_requirements" ON foundation.am_requirements;
CREATE POLICY "service_role_all_am_requirements" ON foundation.am_requirements FOR ALL USING (auth.role() = 'service_role');

-- Seed: LUTS' ATF license, Broker Broker's NMLS license.
DO $$
DECLARE
  v_luts_id UUID;
  v_bb_id UUID;
BEGIN
  SELECT id INTO v_luts_id FROM foundation.client_profiles WHERE business_name = 'LUTS';
  SELECT id INTO v_bb_id FROM foundation.client_profiles WHERE business_name = 'Broker Broker Realty';

  IF v_luts_id IS NOT NULL AND NOT EXISTS (SELECT 1 FROM foundation.am_licenses WHERE client_id = v_luts_id) THEN
    INSERT INTO foundation.am_licenses (client_id, license_type, jurisdiction, expires_at)
    VALUES (v_luts_id, 'ATF Federal Explosives License', 'ATF', CURRENT_DATE + INTERVAL '85 days');
  END IF;

  IF v_bb_id IS NOT NULL AND NOT EXISTS (SELECT 1 FROM foundation.am_licenses WHERE client_id = v_bb_id) THEN
    INSERT INTO foundation.am_licenses (client_id, license_type, jurisdiction, expires_at)
    VALUES (v_bb_id, 'NMLS Mortgage Loan Originator License', 'NMLS', CURRENT_DATE + INTERVAL '25 days');
  END IF;
END $$;
