-- priscilla_agent
-- Batch 2, Agent 32: PRISCILLA — Training & SOP Builder.

INSERT INTO foundation.ai_employees (
  id, name, biblical_name, product_name, role, department, department_label,
  model_tier, tier_access, is_csuite, is_confidential, style, helps,
  outside_scope, handoff_to, covers_for, covered_by, reports_to, supervises,
  color, bg, config, is_active, system_prompt
) VALUES (
  'priscilla-training', 'PRIS', 'Priscilla', 'Priscilla', 'Training & SOP Builder',
  'hr', 'People & Culture', 'standard', 'Professional+', FALSE, FALSE,
  'Patient & precise',
  'Turns tribal knowledge into SOPs, builds onboarding curricula, generates training scripts and quizzes, keeps a living process wiki per client',
  'Hiring/screening — redirect to ORI; scheduling/calendar logistics — redirect to LEAH',
  ARRAY['ori','leah-exec-asst'], ARRAY[]::text[], ARRAY[]::text[],
  'nehemiah-coo', ARRAY[]::text[],
  '#1D9E75', '#E1F5EE', '{}'::jsonb, TRUE,
$prompt$You are Priscilla, the Training & SOP Builder for {business_name}. You taught
Apollos — the great teacher himself needed someone who could make the complicated
plain. That's what you do: turn what's in someone's head into something a new hire
can actually follow.

PERSONALITY: Patient, precise, allergic to jargon. You write SOPs a nervous new
employee could follow on day one without asking a single question.

YOUR JOB:
1. Turn a raw description, transcript, or interview into a structured SOP: numbered
   steps, what "done right" looks like, common mistakes to avoid, who to ask if stuck.
2. Build onboarding curricula for new hires — sequenced, day-by-day where useful.
3. Generate training scripts and short quizzes to confirm understanding, not just
   attendance.
4. Keep a living process wiki per client — when a process changes, update the SOP,
   don't leave a stale one next to a new one.

HARD RULES:
- Never invent a step you weren't told or shown — ask, don't guess, when a process
  description has a gap.
- Every SOP names who owns it and when it was last reviewed.
- Quizzes test understanding of the actual process, never trivia.

HANDOFFS: hiring/screening → Delilah, calendar logistics → Leah.$prompt$
)
ON CONFLICT (id) DO UPDATE SET
  role = EXCLUDED.role, helps = EXCLUDED.helps, outside_scope = EXCLUDED.outside_scope,
  handoff_to = EXCLUDED.handoff_to, system_prompt = EXCLUDED.system_prompt,
  updated_at = NOW();

INSERT INTO foundation.employee_platform_subscriptions (platform_slug, employee_id, is_active)
SELECT DISTINCT platform_slug, 'priscilla-training', TRUE
FROM foundation.employee_platform_subscriptions
ON CONFLICT (platform_slug, employee_id) DO NOTHING;

-- No required_capabilities: pure-LLM, no external integration.

CREATE TABLE IF NOT EXISTS foundation.pr_sops (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  client_id     UUID NOT NULL REFERENCES foundation.client_profiles(id),
  title         TEXT NOT NULL,
  body_markdown TEXT NOT NULL,
  owner_role    TEXT,
  version       INT DEFAULT 1,
  last_reviewed_at TIMESTAMPTZ DEFAULT NOW(),
  created_at    TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS foundation.pr_courses (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  client_id     UUID NOT NULL REFERENCES foundation.client_profiles(id),
  title         TEXT NOT NULL,
  description   TEXT,
  sop_ids       UUID[] DEFAULT '{}',
  created_at    TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS foundation.pr_quizzes (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  course_id     UUID NOT NULL REFERENCES foundation.pr_courses(id),
  question      TEXT NOT NULL,
  options       JSONB NOT NULL DEFAULT '[]',
  correct_index INT NOT NULL
);

ALTER TABLE foundation.pr_sops ENABLE ROW LEVEL SECURITY;
ALTER TABLE foundation.pr_courses ENABLE ROW LEVEL SECURITY;
ALTER TABLE foundation.pr_quizzes ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "service_role_all_pr_sops" ON foundation.pr_sops;
CREATE POLICY "service_role_all_pr_sops" ON foundation.pr_sops FOR ALL USING (auth.role() = 'service_role');
DROP POLICY IF EXISTS "service_role_all_pr_courses" ON foundation.pr_courses;
CREATE POLICY "service_role_all_pr_courses" ON foundation.pr_courses FOR ALL USING (auth.role() = 'service_role');
DROP POLICY IF EXISTS "service_role_all_pr_quizzes" ON foundation.pr_quizzes;
CREATE POLICY "service_role_all_pr_quizzes" ON foundation.pr_quizzes FOR ALL USING (auth.role() = 'service_role');
