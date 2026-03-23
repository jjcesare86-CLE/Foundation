-- Row Level Security policies
-- Enable RLS on all tables, allow authenticated access

ALTER TABLE foundation.skills ENABLE ROW LEVEL SECURITY;
ALTER TABLE foundation.agents ENABLE ROW LEVEL SECURITY;
ALTER TABLE foundation.brand_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE foundation.templates ENABLE ROW LEVEL SECURITY;
ALTER TABLE foundation.client_profiles ENABLE ROW LEVEL SECURITY;

-- Read access for authenticated users (anon key can read)
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

-- Write access for service role only (server-side API)
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
