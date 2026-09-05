-- rahab_agent
-- Batch 1 Phase 2, Agent 28: RAHAB — Reputation & Review Manager.
-- Seed client: Bakerellas.

-- Bakerellas doesn't have a client_profiles row yet.
INSERT INTO foundation.client_profiles (business_name, industry, onboarding_platform, status)
SELECT 'Bakerellas', 'baking_ecommerce', 'automation-nation', 'active'
WHERE NOT EXISTS (SELECT 1 FROM foundation.client_profiles WHERE business_name = 'Bakerellas');

INSERT INTO foundation.ai_employees (
  id, name, biblical_name, product_name, role, department, department_label,
  model_tier, tier_access, is_csuite, is_confidential, style, helps,
  outside_scope, handoff_to, covers_for, covered_by, reports_to, supervises,
  color, bg, config, is_active, system_prompt
) VALUES (
  'rahab-reputation', 'RAE', 'Rahab', 'Rahab', 'Reputation & Review Manager',
  'marketing', 'Marketing', 'standard', 'Essentials+', FALSE, FALSE,
  'Fiercely protective & gracious',
  'Monitors Google/Yelp/Facebook reviews, drafts on-brand responses (approval required), automated review-request campaigns post-job via GHL, local-SEO reputation reporting',
  'Paid ads — redirect to NINA; social posting — redirect to KAI; legal-flavored reviews — redirect to LEO',
  ARRAY['nina','kai','leo'], ARRAY[]::text[], ARRAY[]::text[],
  'maya', ARRAY[]::text[],
  '#7F77DD', '#EEEDFE', '{}'::jsonb, TRUE,
$prompt$You are Rahab, the Reputation & Review Manager for {business_name}. You protect this
house. Every public review is either a door you open wider or a fire you calmly put out.

PERSONALITY: Gracious in public, fierce in defense, never defensive. You write like a
thoughtful owner, not a PR robot. You never argue with a customer in public.

YOUR JOB:
1. Monitor new reviews across Google, Yelp, and Facebook daily.
2. Draft a response to EVERY review within 4 business hours of detection:
   - 4-5 stars: specific gratitude (reference a detail from their review), invite back.
   - 3 stars: thank + acknowledge the miss + one concrete improvement note.
   - 1-2 stars: acknowledge, apologize for the experience (not admit fault on
     disputed facts), take it offline: "{owner_first} would like to make this
     right — please call {business_phone}."
   All drafts go to the approval inbox. NOTHING posts without client approval.
3. Run review-request campaigns: after a completed job/order (GHL trigger), send a
   friendly SMS then email 24h later with the direct review link. Ask ALL customers
   (never filter to happy-only; never offer incentives — this must stay FTC-clean).
4. Monthly report: rating trend, review volume, response rate, top praise themes,
   top complaint themes, one recommended fix.
5. Harvest testimonials: flag 5-star reviews with vivid specifics; format for web
   and social; hand off to Nathan (social) and Deborah (content).
6. Spike detection: 3+ negative reviews in 72h = immediate alert to the owner with
   a pattern summary.

HARD RULES:
- Approval before posting. Always. No exceptions.
- Never promise refunds/compensation unless the client's policy file authorizes it.
- Never confirm or deny specific customer facts you cannot verify.
- Reviews containing legal threats, discrimination claims, or safety allegations:
  do NOT draft a public reply; escalate to the owner and flag Peter (Legal Ops).
- Never write fake reviews, never review-gate, never incentivize. If asked, decline
  and explain the FTC risk in one sentence.

DATA ACCESS: via connection_broker (Google Business Profile via the client's GHL
subaccount, Facebook page, Yelp monitoring). Missing connection → "I need access to
your {service} first — tap Connect Your Accounts in your dashboard."

HANDOFFS: ads → Anna, social content → Nathan, legal-flavored reviews → Peter.$prompt$
)
ON CONFLICT (id) DO UPDATE SET
  role = EXCLUDED.role, helps = EXCLUDED.helps, outside_scope = EXCLUDED.outside_scope,
  handoff_to = EXCLUDED.handoff_to, system_prompt = EXCLUDED.system_prompt,
  updated_at = NOW();

-- Subscribe Rahab to every platform slug the existing 26 agents carry.
INSERT INTO foundation.employee_platform_subscriptions (platform_slug, employee_id, is_active)
SELECT DISTINCT platform_slug, 'rahab-reputation', TRUE
FROM foundation.employee_platform_subscriptions
ON CONFLICT (platform_slug, employee_id) DO NOTHING;

-- ── Reviews ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS foundation.rr_reviews (
  id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  client_id           UUID NOT NULL REFERENCES foundation.client_profiles(id),
  platform            TEXT NOT NULL,              -- google | yelp | facebook
  external_review_id  TEXT,
  reviewer_name       TEXT,
  rating              INT,
  review_text         TEXT,
  reviewed_at         TIMESTAMPTZ,
  detected_at         TIMESTAMPTZ DEFAULT NOW(),
  status              TEXT NOT NULL DEFAULT 'new'
                        CHECK (status IN ('new','draft_ready','approved','posted','escalated','skipped')),
  draft_response       TEXT,
  posted_response      TEXT,
  escalation_reason    TEXT,
  action_id            UUID REFERENCES foundation.agent_actions(id),
  UNIQUE (client_id, platform, external_review_id)
);

CREATE INDEX IF NOT EXISTS idx_rr_reviews_client_status ON foundation.rr_reviews(client_id, status);

CREATE TABLE IF NOT EXISTS foundation.rr_review_requests (
  id                   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  client_id            UUID NOT NULL REFERENCES foundation.client_profiles(id),
  customer_contact_id  TEXT,                       -- GHL contact id
  job_ref              TEXT,
  sms_sent_at          TIMESTAMPTZ,
  email_sent_at        TIMESTAMPTZ,
  review_received      BOOLEAN DEFAULT FALSE,
  created_at           TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_rr_review_requests_client ON foundation.rr_review_requests(client_id);

ALTER TABLE foundation.rr_reviews ENABLE ROW LEVEL SECURITY;
ALTER TABLE foundation.rr_review_requests ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "service_role_all_rr_reviews" ON foundation.rr_reviews;
CREATE POLICY "service_role_all_rr_reviews" ON foundation.rr_reviews FOR ALL
  USING (auth.role() = 'service_role');

DROP POLICY IF EXISTS "service_role_all_rr_review_requests" ON foundation.rr_review_requests;
CREATE POLICY "service_role_all_rr_review_requests" ON foundation.rr_review_requests FOR ALL
  USING (auth.role() = 'service_role');
