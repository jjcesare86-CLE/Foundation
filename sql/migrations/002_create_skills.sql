-- foundation.skills — skill definitions with semantic search support

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

-- Index for semantic similarity search
CREATE INDEX IF NOT EXISTS skills_embedding_idx
    ON foundation.skills
    USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);

-- Index for category filtering
CREATE INDEX IF NOT EXISTS skills_category_idx
    ON foundation.skills (category);

-- Full-text search index
CREATE INDEX IF NOT EXISTS skills_name_description_idx
    ON foundation.skills
    USING gin (to_tsvector('english', coalesce(name, '') || ' ' || coalesce(description, '')));

-- Auto-update updated_at
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
