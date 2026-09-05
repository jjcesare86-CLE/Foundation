-- tabitha_agent
-- Batch 3, Agent 34: TABITHA — Nonprofit & Donor Relations.

INSERT INTO foundation.ai_employees (
  id, name, biblical_name, product_name, role, department, department_label,
  model_tier, tier_access, is_csuite, is_confidential, style, helps,
  outside_scope, handoff_to, covers_for, covered_by, reports_to, supervises,
  color, bg, config, is_active, system_prompt
) VALUES (
  'tabitha-donors', 'TAB', 'Tabitha', 'Tabitha', 'Nonprofit & Donor Relations',
  'sales', 'Sales', 'standard', 'Professional+', FALSE, FALSE,
  'Warm & mission-driven',
  'Donor CRM management, grant-deadline tracking and draft writing, donation-receipt automation, campaign appeals, board-report generation',
  'General marketing copy — redirect to CLARA; financial reporting beyond donor/grant tracking — redirect to JOANNA or ELIJAH',
  ARRAY['clara','joanna-finance','dean'], ARRAY[]::text[], ARRAY[]::text[],
  'rex', ARRAY[]::text[],
  '#378ADD', '#E6F1FB', '{}'::jsonb, TRUE,
$prompt$You are Tabitha, the Nonprofit & Donor Relations specialist for {business_name}.
"Full of good works and acts of charity" — you keep the relationships that keep the
mission funded, and you never let a donor feel like a transaction.

PERSONALITY: Warm, genuinely mission-driven, organized underneath the warmth. You
remember what a donor cares about, not just what they gave last time.

YOUR JOB:
1. Donor CRM: track giving history, communication preferences, what they care about
   within the mission — never generic form-letter energy.
2. Grant deadline tracking: flag upcoming grant application windows with enough lead
   time to write a real application, not a rushed one; draft first passes for review.
3. Donation-receipt automation: every gift gets a prompt, accurate, IRS-compliant
   thank-you and receipt.
4. Campaign appeals: write asks that lead with impact and story, not guilt.
5. Board reports: turn the numbers into a narrative a board member actually reads.

HARD RULES:
- Every receipt is accurate to the cent and IRS-compliant — never approximate a
  donation amount.
- Never misrepresent how a gift will be used.
- A donor's giving history and personal details never leave donor CRM context —
  no casual mentions in unrelated communications.

HANDOFFS: general marketing copy → Esther, financial reporting beyond donor/grant
tracking → Joanna or Elijah.$prompt$
)
ON CONFLICT (id) DO UPDATE SET
  role = EXCLUDED.role, helps = EXCLUDED.helps, outside_scope = EXCLUDED.outside_scope,
  handoff_to = EXCLUDED.handoff_to, system_prompt = EXCLUDED.system_prompt,
  updated_at = NOW();

INSERT INTO foundation.employee_platform_subscriptions (platform_slug, employee_id, is_active)
SELECT DISTINCT platform_slug, 'tabitha-donors', TRUE
FROM foundation.employee_platform_subscriptions
ON CONFLICT (platform_slug, employee_id) DO NOTHING;

-- No required_capabilities: donor CRM tracked in Foundation's own tables for v1,
-- not yet wired to an external CRM.

CREATE TABLE IF NOT EXISTS foundation.tb_donors (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  client_id       UUID NOT NULL REFERENCES foundation.client_profiles(id),
  donor_name      TEXT NOT NULL,
  contact_email   TEXT,
  ytd_given       NUMERIC(12,2) DEFAULT 0,
  lifetime_given  NUMERIC(12,2) DEFAULT 0,
  interests       TEXT[] DEFAULT '{}',
  last_contact_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS foundation.tb_grants (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  client_id     UUID NOT NULL REFERENCES foundation.client_profiles(id),
  grant_name    TEXT NOT NULL,
  funder        TEXT,
  amount        NUMERIC(12,2),
  deadline      DATE NOT NULL,
  status        TEXT DEFAULT 'upcoming' CHECK (status IN ('upcoming','drafting','submitted','awarded','declined'))
);

CREATE TABLE IF NOT EXISTS foundation.tb_appeals (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  client_id     UUID NOT NULL REFERENCES foundation.client_profiles(id),
  campaign_name TEXT NOT NULL,
  appeal_text   TEXT,
  sent_at       TIMESTAMPTZ,
  raised_amount NUMERIC(12,2) DEFAULT 0
);

ALTER TABLE foundation.tb_donors ENABLE ROW LEVEL SECURITY;
ALTER TABLE foundation.tb_grants ENABLE ROW LEVEL SECURITY;
ALTER TABLE foundation.tb_appeals ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "service_role_all_tb_donors" ON foundation.tb_donors;
CREATE POLICY "service_role_all_tb_donors" ON foundation.tb_donors FOR ALL USING (auth.role() = 'service_role');
DROP POLICY IF EXISTS "service_role_all_tb_grants" ON foundation.tb_grants;
CREATE POLICY "service_role_all_tb_grants" ON foundation.tb_grants FOR ALL USING (auth.role() = 'service_role');
DROP POLICY IF EXISTS "service_role_all_tb_appeals" ON foundation.tb_appeals;
CREATE POLICY "service_role_all_tb_appeals" ON foundation.tb_appeals FOR ALL USING (auth.role() = 'service_role');
