-- foundation.templates — document/web/social templates

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
