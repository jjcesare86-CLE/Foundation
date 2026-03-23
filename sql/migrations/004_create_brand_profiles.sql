-- foundation.brand_profiles — per business: colors, tone, taglines, logos

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
