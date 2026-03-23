-- Supabase Storage bucket setup
-- Run in the Supabase SQL Editor to create storage buckets

INSERT INTO storage.buckets (id, name, public)
VALUES
    ('skills', 'skills', true),
    ('agent-configs', 'agent-configs', false),
    ('brand-kits', 'brand-kits', true),
    ('legal-templates', 'legal-templates', false),
    ('client-deliverables', 'client-deliverables', false)
ON CONFLICT (id) DO NOTHING;

-- Public read access for public buckets
CREATE POLICY "Public read access for skills"
    ON storage.objects FOR SELECT
    USING (bucket_id = 'skills');

CREATE POLICY "Public read access for brand-kits"
    ON storage.objects FOR SELECT
    USING (bucket_id = 'brand-kits');

-- Service role write access for all buckets
CREATE POLICY "Service role upload to all buckets"
    ON storage.objects FOR INSERT
    WITH CHECK (auth.role() = 'service_role');

CREATE POLICY "Service role update in all buckets"
    ON storage.objects FOR UPDATE
    USING (auth.role() = 'service_role');

CREATE POLICY "Service role delete from all buckets"
    ON storage.objects FOR DELETE
    USING (auth.role() = 'service_role');
