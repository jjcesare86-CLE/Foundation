-- =============================================================
-- FOUNDATION: Complete Database Setup
-- Run this entire script in Supabase SQL Editor (one shot)
-- =============================================================

-- =============================================================
-- 001: Schema & Extensions
-- =============================================================
CREATE EXTENSION IF NOT EXISTS vector;
CREATE SCHEMA IF NOT EXISTS foundation;

-- =============================================================
-- 002: Skills Table
-- =============================================================
CREATE TABLE IF NOT EXISTS foundation.skills (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    description TEXT,
    prompt TEXT,
    category TEXT,
    tags TEXT[] DEFAULT '{}',
    version INTEGER DEFAULT 1,
    embedding VECTOR(1536),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS skills_embedding_idx
    ON foundation.skills
    USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);

CREATE INDEX IF NOT EXISTS skills_category_idx
    ON foundation.skills (category);

CREATE INDEX IF NOT EXISTS skills_name_description_idx
    ON foundation.skills
    USING gin (to_tsvector('english', coalesce(name, '') || ' ' || coalesce(description, '')));

CREATE OR REPLACE FUNCTION foundation.update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER skills_updated_at
    BEFORE UPDATE ON foundation.skills
    FOR EACH ROW
    EXECUTE FUNCTION foundation.update_updated_at();

-- =============================================================
-- 003: Agents Table
-- =============================================================
CREATE TABLE IF NOT EXISTS foundation.agents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    description TEXT,
    system_prompt TEXT,
    tools TEXT[] DEFAULT '{}',
    model TEXT DEFAULT 'claude-sonnet-4-6',
    platform TEXT,
    agent_type TEXT,
    embedding VECTOR(1536),
    config JSONB DEFAULT '{}',
    metadata JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS agents_embedding_idx
    ON foundation.agents
    USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);

CREATE INDEX IF NOT EXISTS agents_type_platform_idx
    ON foundation.agents (agent_type, platform);

CREATE TRIGGER agents_updated_at
    BEFORE UPDATE ON foundation.agents
    FOR EACH ROW
    EXECUTE FUNCTION foundation.update_updated_at();

-- =============================================================
-- 004: Brand Profiles Table
-- =============================================================
CREATE TABLE IF NOT EXISTS foundation.brand_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_slug TEXT UNIQUE NOT NULL,
    business_name TEXT NOT NULL,
    tagline TEXT,
    tone TEXT,
    colors JSONB DEFAULT '{}',
    fonts JSONB DEFAULT '{}',
    logo_url TEXT,
    industry TEXT,
    description TEXT,
    guidelines TEXT,
    embedding VECTOR(1536),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS brand_profiles_slug_idx
    ON foundation.brand_profiles (business_slug);

CREATE INDEX IF NOT EXISTS brand_profiles_industry_idx
    ON foundation.brand_profiles (industry);

CREATE INDEX IF NOT EXISTS brand_profiles_embedding_idx
    ON foundation.brand_profiles
    USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);

CREATE TRIGGER brand_profiles_updated_at
    BEFORE UPDATE ON foundation.brand_profiles
    FOR EACH ROW
    EXECUTE FUNCTION foundation.update_updated_at();

-- =============================================================
-- 005: Templates Table
-- =============================================================
CREATE TABLE IF NOT EXISTS foundation.templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    description TEXT,
    template_type TEXT NOT NULL,
    industry TEXT,
    content TEXT,
    file_url TEXT,
    tags TEXT[] DEFAULT '{}',
    embedding VECTOR(1536),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS templates_type_industry_idx
    ON foundation.templates (template_type, industry);

CREATE INDEX IF NOT EXISTS templates_embedding_idx
    ON foundation.templates
    USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);

CREATE TRIGGER templates_updated_at
    BEFORE UPDATE ON foundation.templates
    FOR EACH ROW
    EXECUTE FUNCTION foundation.update_updated_at();

-- =============================================================
-- 006: Client Profiles Table
-- =============================================================
CREATE TABLE IF NOT EXISTS foundation.client_profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_name TEXT NOT NULL,
    contact_name TEXT,
    contact_email TEXT,
    contact_phone TEXT,
    industry TEXT,
    website TEXT,
    onboarding_platform TEXT,
    services TEXT[] DEFAULT '{}',
    notes TEXT,
    brand_profile_id UUID REFERENCES foundation.brand_profiles(id),
    embedding VECTOR(1536),
    onboarding_data JSONB DEFAULT '{}',
    metadata JSONB DEFAULT '{}',
    status TEXT DEFAULT 'onboarding',
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS client_profiles_industry_idx
    ON foundation.client_profiles (industry);

CREATE INDEX IF NOT EXISTS client_profiles_status_idx
    ON foundation.client_profiles (status);

CREATE INDEX IF NOT EXISTS client_profiles_embedding_idx
    ON foundation.client_profiles
    USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);

CREATE TRIGGER client_profiles_updated_at
    BEFORE UPDATE ON foundation.client_profiles
    FOR EACH ROW
    EXECUTE FUNCTION foundation.update_updated_at();

-- =============================================================
-- 007: Row Level Security
-- =============================================================
ALTER TABLE foundation.skills ENABLE ROW LEVEL SECURITY;
ALTER TABLE foundation.agents ENABLE ROW LEVEL SECURITY;
ALTER TABLE foundation.brand_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE foundation.templates ENABLE ROW LEVEL SECURITY;
ALTER TABLE foundation.client_profiles ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow public read on skills"
    ON foundation.skills FOR SELECT
    USING (true);

CREATE POLICY "Allow public read on agents"
    ON foundation.agents FOR SELECT
    USING (true);

CREATE POLICY "Allow public read on brand_profiles"
    ON foundation.brand_profiles FOR SELECT
    USING (true);

CREATE POLICY "Allow public read on templates"
    ON foundation.templates FOR SELECT
    USING (true);

CREATE POLICY "Allow public read on client_profiles"
    ON foundation.client_profiles FOR SELECT
    USING (true);

CREATE POLICY "Allow service role write on skills"
    ON foundation.skills FOR ALL
    USING (auth.role() = 'service_role');

CREATE POLICY "Allow service role write on agents"
    ON foundation.agents FOR ALL
    USING (auth.role() = 'service_role');

CREATE POLICY "Allow service role write on brand_profiles"
    ON foundation.brand_profiles FOR ALL
    USING (auth.role() = 'service_role');

CREATE POLICY "Allow service role write on templates"
    ON foundation.templates FOR ALL
    USING (auth.role() = 'service_role');

CREATE POLICY "Allow service role write on client_profiles"
    ON foundation.client_profiles FOR ALL
    USING (auth.role() = 'service_role');

-- =============================================================
-- 008: Semantic Search Functions
-- =============================================================
CREATE OR REPLACE FUNCTION foundation.search_skills(
    query_embedding VECTOR(1536),
    match_threshold FLOAT DEFAULT 0.7,
    match_count INT DEFAULT 10,
    filter_category TEXT DEFAULT NULL
)
RETURNS TABLE (
    id UUID,
    name TEXT,
    description TEXT,
    prompt TEXT,
    category TEXT,
    tags TEXT[],
    similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        s.id, s.name, s.description, s.prompt, s.category, s.tags,
        1 - (s.embedding <=> query_embedding) AS similarity
    FROM foundation.skills s
    WHERE 1 - (s.embedding <=> query_embedding) > match_threshold
      AND (filter_category IS NULL OR s.category = filter_category)
    ORDER BY s.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

CREATE OR REPLACE FUNCTION foundation.search_agents(
    query_embedding VECTOR(1536),
    match_threshold FLOAT DEFAULT 0.7,
    match_count INT DEFAULT 10,
    filter_type TEXT DEFAULT NULL,
    filter_platform TEXT DEFAULT NULL
)
RETURNS TABLE (
    id UUID,
    name TEXT,
    description TEXT,
    agent_type TEXT,
    platform TEXT,
    similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        a.id, a.name, a.description, a.agent_type, a.platform,
        1 - (a.embedding <=> query_embedding) AS similarity
    FROM foundation.agents a
    WHERE 1 - (a.embedding <=> query_embedding) > match_threshold
      AND (filter_type IS NULL OR a.agent_type = filter_type)
      AND (filter_platform IS NULL OR a.platform = filter_platform)
      AND a.is_active = true
    ORDER BY a.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

CREATE OR REPLACE FUNCTION foundation.search_templates(
    query_embedding VECTOR(1536),
    match_threshold FLOAT DEFAULT 0.7,
    match_count INT DEFAULT 10,
    filter_type TEXT DEFAULT NULL,
    filter_industry TEXT DEFAULT NULL
)
RETURNS TABLE (
    id UUID,
    name TEXT,
    description TEXT,
    template_type TEXT,
    industry TEXT,
    similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        t.id, t.name, t.description, t.template_type, t.industry,
        1 - (t.embedding <=> query_embedding) AS similarity
    FROM foundation.templates t
    WHERE 1 - (t.embedding <=> query_embedding) > match_threshold
      AND (filter_type IS NULL OR t.template_type = filter_type)
      AND (filter_industry IS NULL OR t.industry = filter_industry)
    ORDER BY t.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- =============================================================
-- Storage Buckets
-- =============================================================
INSERT INTO storage.buckets (id, name, public)
VALUES
    ('skills', 'skills', true),
    ('agent-configs', 'agent-configs', false),
    ('brand-kits', 'brand-kits', true),
    ('legal-templates', 'legal-templates', false),
    ('client-deliverables', 'client-deliverables', false)
ON CONFLICT (id) DO NOTHING;

CREATE POLICY "Public read access for skills"
    ON storage.objects FOR SELECT
    USING (bucket_id = 'skills');

CREATE POLICY "Public read access for brand-kits"
    ON storage.objects FOR SELECT
    USING (bucket_id = 'brand-kits');

CREATE POLICY "Service role upload to all buckets"
    ON storage.objects FOR INSERT
    WITH CHECK (auth.role() = 'service_role');

CREATE POLICY "Service role update in all buckets"
    ON storage.objects FOR UPDATE
    USING (auth.role() = 'service_role');

CREATE POLICY "Service role delete from all buckets"
    ON storage.objects FOR DELETE
    USING (auth.role() = 'service_role');

-- =============================================================
-- DONE! All tables, indexes, RLS, functions, and buckets created.
-- =============================================================
