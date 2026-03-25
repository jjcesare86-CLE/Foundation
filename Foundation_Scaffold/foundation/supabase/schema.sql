-- ============================================================
-- FOUNDATION SCHEMA — Run in Supabase SQL Editor
-- Shared layer for Automation Nation, VoiceMIO, Jubilant Careers
-- ============================================================

-- Enable pgvector for semantic search
CREATE EXTENSION IF NOT EXISTS vector;

-- Create foundation schema
CREATE SCHEMA IF NOT EXISTS foundation;

-- ============================================================
-- SKILLS TABLE
-- Stores all reusable skill definitions
-- ============================================================
CREATE TABLE IF NOT EXISTS foundation.skills (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            TEXT NOT NULL,
    slug            TEXT NOT NULL UNIQUE,
    description     TEXT,
    category        TEXT NOT NULL,          -- e.g. 'voice-agents', 'social-media', 'legal-docs'
    subcategory     TEXT,
    prompt_template TEXT,                   -- The actual skill prompt/instructions
    config          JSONB DEFAULT '{}',     -- Flexible config (model, temperature, tools, etc.)
    industries      TEXT[] DEFAULT '{}',    -- e.g. ['restaurant', 'dental', 'real-estate']
    platforms       TEXT[] DEFAULT '{}',    -- e.g. ['automation-nation', 'voicemio']
    version         TEXT DEFAULT '1.0.0',
    is_active       BOOLEAN DEFAULT TRUE,
    embedding       vector(1536),           -- For semantic search (OpenAI/Anthropic embeddings)
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- AGENTS TABLE
-- Stores sub-agent / AI employee configurations
-- ============================================================
CREATE TABLE IF NOT EXISTS foundation.agents (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            TEXT NOT NULL,
    slug            TEXT NOT NULL UNIQUE,
    description     TEXT,
    agent_type      TEXT NOT NULL,          -- 'sales', 'onboarding', 'content', 'ops', 'voice'
    system_prompt   TEXT,
    tools           JSONB DEFAULT '[]',     -- List of tool/function definitions
    model           TEXT DEFAULT 'claude-sonnet-4-20250514',
    temperature     FLOAT DEFAULT 0.7,
    max_tokens      INTEGER DEFAULT 2048,
    skills          UUID[] DEFAULT '{}',    -- References to foundation.skills
    config          JSONB DEFAULT '{}',
    platforms       TEXT[] DEFAULT '{}',
    industries      TEXT[] DEFAULT '{}',
    version         TEXT DEFAULT '1.0.0',
    is_active       BOOLEAN DEFAULT TRUE,
    embedding       vector(1536),
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- BRAND PROFILES TABLE
-- Per-business brand identity — used uniformly across all outputs
-- ============================================================
CREATE TABLE IF NOT EXISTS foundation.brand_profiles (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_slug   TEXT NOT NULL UNIQUE,   -- e.g. 'automation-nation', 'voicemio'
    business_name   TEXT NOT NULL,
    tagline         TEXT,
    description     TEXT,
    logo_url        TEXT,
    -- Colors
    primary_color   TEXT,
    secondary_color TEXT,
    accent_color    TEXT,
    bg_color        TEXT,
    text_color      TEXT,
    -- Typography
    heading_font    TEXT,
    body_font       TEXT,
    -- Tone & Voice
    tone_keywords   TEXT[] DEFAULT '{}',    -- e.g. ['professional', 'energetic', 'trustworthy']
    voice_style     TEXT,                   -- e.g. 'conversational', 'authoritative'
    avoid_words     TEXT[] DEFAULT '{}',    -- Words/phrases to never use
    -- Contact & Links
    website_url     TEXT,
    support_email   TEXT,
    phone           TEXT,
    address         JSONB DEFAULT '{}',
    social_links    JSONB DEFAULT '{}',
    -- Extended brand data
    mission         TEXT,
    vision          TEXT,
    values          TEXT[] DEFAULT '{}',
    target_audience TEXT,
    usp             TEXT,                   -- Unique selling proposition
    config          JSONB DEFAULT '{}',
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- TEMPLATES TABLE
-- Reusable output templates (websites, social, legal, SOPs)
-- ============================================================
CREATE TABLE IF NOT EXISTS foundation.templates (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name            TEXT NOT NULL,
    slug            TEXT NOT NULL UNIQUE,
    description     TEXT,
    template_type   TEXT NOT NULL,          -- 'website', 'social-post', 'legal', 'sop', 'email', 'ad'
    industry        TEXT,
    platform        TEXT,
    content         TEXT,                   -- The template body (markdown / HTML / prompt)
    variables       JSONB DEFAULT '[]',     -- List of {name, description, required} objects
    config          JSONB DEFAULT '{}',
    tags            TEXT[] DEFAULT '{}',
    is_active       BOOLEAN DEFAULT TRUE,
    embedding       vector(1536),
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- CLIENT PROFILES TABLE
-- Populated during client onboarding — used across all platforms
-- ============================================================
CREATE TABLE IF NOT EXISTS foundation.client_profiles (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    -- Identity
    client_id           TEXT UNIQUE,        -- Internal reference ID
    business_name       TEXT NOT NULL,
    business_slug       TEXT UNIQUE,
    industry            TEXT,
    sub_industry        TEXT,
    -- Contact
    owner_name          TEXT,
    owner_email         TEXT,
    owner_phone         TEXT,
    business_email      TEXT,
    business_phone      TEXT,
    address             JSONB DEFAULT '{}',
    -- Platform refs
    source_platform     TEXT,               -- 'automation-nation', 'voicemio', etc.
    stripe_customer_id  TEXT,
    ghl_location_id     TEXT,
    vapi_assistant_id   TEXT,
    supabase_user_id    UUID,
    -- Brand
    brand               JSONB DEFAULT '{}', -- Inline brand data (colors, logo, tone, etc.)
    -- Services
    tier                TEXT,               -- 'essentials', 'professional', 'enterprise'
    active_services     TEXT[] DEFAULT '{}',
    -- Onboarding
    onboarding_status   TEXT DEFAULT 'pending',  -- 'pending', 'in_progress', 'complete'
    onboarding_data     JSONB DEFAULT '{}',
    completed_tasks     TEXT[] DEFAULT '{}',
    -- Meta
    notes               TEXT,
    tags                TEXT[] DEFAULT '{}',
    config              JSONB DEFAULT '{}',
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- CLIENT DEPLOYMENTS TABLE
-- Tracks what has been built/deployed for each client
-- ============================================================
CREATE TABLE IF NOT EXISTS foundation.client_deployments (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id       TEXT REFERENCES foundation.client_profiles(client_id),
    deployment_type TEXT NOT NULL,          -- 'website', 'voice-agent', 'social-media', 'automation', etc.
    status          TEXT DEFAULT 'queued',  -- 'queued', 'building', 'live', 'failed'
    config          JSONB DEFAULT '{}',     -- All settings used for this deployment
    output          JSONB DEFAULT '{}',     -- URLs, IDs, credentials created
    agent_used      UUID REFERENCES foundation.agents(id),
    skill_used      UUID REFERENCES foundation.skills(id),
    started_at      TIMESTAMPTZ,
    completed_at    TIMESTAMPTZ,
    error_log       TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW(),
    updated_at      TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- INDEXES
-- ============================================================
CREATE INDEX IF NOT EXISTS idx_skills_category       ON foundation.skills(category);
CREATE INDEX IF NOT EXISTS idx_skills_platforms      ON foundation.skills USING GIN(platforms);
CREATE INDEX IF NOT EXISTS idx_skills_industries     ON foundation.skills USING GIN(industries);
CREATE INDEX IF NOT EXISTS idx_agents_type           ON foundation.agents(agent_type);
CREATE INDEX IF NOT EXISTS idx_agents_platforms      ON foundation.agents USING GIN(platforms);
CREATE INDEX IF NOT EXISTS idx_templates_type        ON foundation.templates(template_type);
CREATE INDEX IF NOT EXISTS idx_templates_industry    ON foundation.templates(industry);
CREATE INDEX IF NOT EXISTS idx_clients_platform      ON foundation.client_profiles(source_platform);
CREATE INDEX IF NOT EXISTS idx_clients_status        ON foundation.client_profiles(onboarding_status);
CREATE INDEX IF NOT EXISTS idx_deployments_client    ON foundation.client_deployments(client_id);
CREATE INDEX IF NOT EXISTS idx_deployments_status    ON foundation.client_deployments(status);

-- Vector similarity indexes (HNSW for fast ANN search)
CREATE INDEX IF NOT EXISTS idx_skills_embedding      ON foundation.skills   USING hnsw (embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS idx_agents_embedding      ON foundation.agents   USING hnsw (embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS idx_templates_embedding   ON foundation.templates USING hnsw (embedding vector_cosine_ops);

-- ============================================================
-- ROW LEVEL SECURITY (Enable after confirming schema works)
-- ============================================================
ALTER TABLE foundation.skills            ENABLE ROW LEVEL SECURITY;
ALTER TABLE foundation.agents            ENABLE ROW LEVEL SECURITY;
ALTER TABLE foundation.brand_profiles    ENABLE ROW LEVEL SECURITY;
ALTER TABLE foundation.templates         ENABLE ROW LEVEL SECURITY;
ALTER TABLE foundation.client_profiles   ENABLE ROW LEVEL SECURITY;
ALTER TABLE foundation.client_deployments ENABLE ROW LEVEL SECURITY;

-- Service role bypass (for foundation-api backend)
CREATE POLICY "service_role_all" ON foundation.skills            FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "service_role_all" ON foundation.agents            FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "service_role_all" ON foundation.brand_profiles    FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "service_role_all" ON foundation.templates         FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "service_role_all" ON foundation.client_profiles   FOR ALL USING (auth.role() = 'service_role');
CREATE POLICY "service_role_all" ON foundation.client_deployments FOR ALL USING (auth.role() = 'service_role');

-- ============================================================
-- AUTO-UPDATE updated_at TRIGGER
-- ============================================================
CREATE OR REPLACE FUNCTION foundation.set_updated_at()
RETURNS TRIGGER AS $$
BEGIN NEW.updated_at = NOW(); RETURN NEW; END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_skills_updated_at        BEFORE UPDATE ON foundation.skills            FOR EACH ROW EXECUTE FUNCTION foundation.set_updated_at();
CREATE TRIGGER trg_agents_updated_at        BEFORE UPDATE ON foundation.agents            FOR EACH ROW EXECUTE FUNCTION foundation.set_updated_at();
CREATE TRIGGER trg_brands_updated_at        BEFORE UPDATE ON foundation.brand_profiles    FOR EACH ROW EXECUTE FUNCTION foundation.set_updated_at();
CREATE TRIGGER trg_templates_updated_at     BEFORE UPDATE ON foundation.templates         FOR EACH ROW EXECUTE FUNCTION foundation.set_updated_at();
CREATE TRIGGER trg_clients_updated_at       BEFORE UPDATE ON foundation.client_profiles   FOR EACH ROW EXECUTE FUNCTION foundation.set_updated_at();
CREATE TRIGGER trg_deployments_updated_at   BEFORE UPDATE ON foundation.client_deployments FOR EACH ROW EXECUTE FUNCTION foundation.set_updated_at();
