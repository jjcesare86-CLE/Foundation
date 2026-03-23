-- foundation.agents — agent configs, system prompts, tools

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
