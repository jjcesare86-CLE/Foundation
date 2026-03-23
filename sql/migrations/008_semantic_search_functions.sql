-- Semantic search functions for pgvector
-- These allow agents to search by meaning, not just keywords

-- Search skills by embedding similarity
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

-- Search agents by embedding similarity
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

-- Search templates by embedding similarity
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
