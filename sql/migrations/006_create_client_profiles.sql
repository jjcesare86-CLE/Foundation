-- foundation.client_profiles — reusable client data populated during onboarding

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
