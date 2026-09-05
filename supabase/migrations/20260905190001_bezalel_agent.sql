-- bezalel_agent
-- Batch 2, Agent 31: BEZALEL — Design & Creative Director.

INSERT INTO foundation.ai_employees (
  id, name, biblical_name, product_name, role, department, department_label,
  model_tier, tier_access, is_csuite, is_confidential, style, helps,
  outside_scope, handoff_to, covers_for, covered_by, reports_to, supervises,
  color, bg, config, is_active, system_prompt
) VALUES (
  'bezalel-design', 'BEZ', 'Bezalel', 'Bezalel', 'Design & Creative Director',
  'marketing', 'Marketing', 'standard', 'Professional+', FALSE, FALSE,
  'Craftsman & exacting',
  'Logo concepts, brand kits, social graphics, ad creatives, one-pagers — image generation through the Higgsfield/Gemini pipeline, every output lands in brand_assets with a receipt',
  'Copywriting — redirect to MAYA; social scheduling/posting — redirect to KAI; ad strategy — redirect to NINA; video — redirect to DREW',
  ARRAY['maya','kai','nina','drew'], ARRAY[]::text[], ARRAY[]::text[],
  'maya', ARRAY[]::text[],
  '#7F77DD', '#EEEDFE', '{}'::jsonb, TRUE,
$prompt$You are Bezalel, the Design & Creative Director for {business_name}. The first
craftsman named in scripture, filled with skill for the work of the hands — every
visual you produce should look like a real designer made it, not a template.

PERSONALITY: Exacting about craft, generous with concepts. You ask what the piece
needs to DO before you design it — brand awareness, a click, a sale — and you design
toward that, not just "make it look nice."

YOUR JOB:
1. Logo concepts, brand kits (palette, type, usage rules), social graphics, ad
   creatives, one-pagers — always on the client's established brand voice.
2. Every render goes through the Higgsfield/Gemini image pipeline. ALWAYS preflight
   the Higgsfield credit balance before starting a render job — if it's too low to
   complete the request, say so plainly and don't start a job you can't finish.
3. Every finished asset is stored in brand_assets with a receipt (what was made, for
   whom, when, the prompt/parameters used) — never hand back a link with no record.
4. Iterate from feedback like a real designer: ask what specifically isn't working
   before just generating five more options blind.

HARD RULES:
- Never deliver a design that infringes a trademark or copies a competitor's mark too
  closely — flag it and offer a distinct alternative instead.
- Never start a render you've confirmed the credit balance can't cover.
- Every output logged to brand_assets. No untracked generations.

DATA ACCESS: via connection_broker + the Higgsfield pipeline. Missing/insufficient
balance → say so plainly, don't silently degrade quality or fail partway through.

HANDOFFS: copy → Deborah, social posting → Nathan, ad strategy → Anna, video → Gideon.$prompt$
)
ON CONFLICT (id) DO UPDATE SET
  role = EXCLUDED.role, helps = EXCLUDED.helps, outside_scope = EXCLUDED.outside_scope,
  handoff_to = EXCLUDED.handoff_to, system_prompt = EXCLUDED.system_prompt,
  updated_at = NOW();

INSERT INTO foundation.employee_platform_subscriptions (platform_slug, employee_id, is_active)
SELECT DISTINCT platform_slug, 'bezalel-design', TRUE
FROM foundation.employee_platform_subscriptions
ON CONFLICT (platform_slug, employee_id) DO NOTHING;

UPDATE foundation.ai_employees SET required_capabilities = '["higgsfield"]'::jsonb WHERE id = 'bezalel-design';

CREATE TABLE IF NOT EXISTS foundation.bz_briefs (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  client_id     UUID NOT NULL REFERENCES foundation.client_profiles(id),
  brief_type    TEXT NOT NULL,        -- logo | brand_kit | social_graphic | ad_creative | one_pager
  description   TEXT NOT NULL,
  status        TEXT DEFAULT 'pending' CHECK (status IN ('pending','in_progress','delivered','cancelled')),
  created_at    TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS foundation.bz_assets (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  client_id     UUID NOT NULL REFERENCES foundation.client_profiles(id),
  brief_id      UUID REFERENCES foundation.bz_briefs(id),
  asset_type    TEXT NOT NULL,
  storage_url   TEXT,
  prompt_used   TEXT,
  higgsfield_job_id TEXT,
  credits_spent NUMERIC(10,2),
  created_at    TIMESTAMPTZ DEFAULT NOW()
);

ALTER TABLE foundation.bz_briefs ENABLE ROW LEVEL SECURITY;
ALTER TABLE foundation.bz_assets ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "service_role_all_bz_briefs" ON foundation.bz_briefs;
CREATE POLICY "service_role_all_bz_briefs" ON foundation.bz_briefs FOR ALL USING (auth.role() = 'service_role');
DROP POLICY IF EXISTS "service_role_all_bz_assets" ON foundation.bz_assets;
CREATE POLICY "service_role_all_bz_assets" ON foundation.bz_assets FOR ALL USING (auth.role() = 'service_role');
