-- =====================================================================
-- Foundation Layer · voice_edit module
-- 20260429_voice_edit_foundation.sql
--
-- Adds three tables that power voice-editable onboarding across AN,
-- VoiceMIO, Blast Video, and any future product mounted on Foundation.
--
-- Assumes business_profiles already exists (from earlier AN migration).
-- Idempotent: safe to re-run.
-- =====================================================================

-- ---------------------------------------------------------------------
-- 1. editable_surfaces
--    A registry of "places" voice-edit can be mounted (brand portfolio,
--    website builder, voice agent prompt, etc.). New product = INSERT a
--    row; the API picks it up automatically.
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS editable_surfaces (
    id              TEXT PRIMARY KEY,           -- 'brand_portfolio', 'website', etc.
    display_name    TEXT NOT NULL,
    product         TEXT NOT NULL,              -- 'AN' | 'VoiceMIO' | 'BlastVideo' | 'shared'
    schema_version  INT  NOT NULL DEFAULT 1,
    config_path     TEXT NOT NULL,              -- path to YAML in editable_fields.yaml
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

INSERT INTO editable_surfaces (id, display_name, product, config_path) VALUES
    ('brand_portfolio',     'Brand Portfolio',     'shared',     'surfaces.brand_portfolio'),
    ('website',             'Website Builder',     'AN',         'surfaces.website'),
    ('voice_agent_prompt',  'Voice Agent Prompt',  'VoiceMIO',   'surfaces.voice_agent_prompt'),
    ('social_brand_launcher','Social Brand Launcher','AN',       'surfaces.social_brand_launcher')
ON CONFLICT (id) DO NOTHING;

-- ---------------------------------------------------------------------
-- 2. edit_sessions
--    Unifies a customer's edit activity across channels (phone call,
--    web form, email link). One row per active session per business.
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS edit_sessions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id     UUID NOT NULL REFERENCES business_profiles(id) ON DELETE CASCADE,
    surface_id      TEXT NOT NULL REFERENCES editable_surfaces(id),

    -- Channels currently attached to this session
    channels        JSONB NOT NULL DEFAULT '[]'::jsonb,
    -- e.g. [{"type":"voice","vapi_call_id":"..."},{"type":"web","client_id":"..."}]

    -- Session state
    status          TEXT NOT NULL DEFAULT 'active'
                    CHECK (status IN ('active','paused','expired','completed')),
    pending_edit    JSONB,    -- edit awaiting user confirmation, if any
    last_activity_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    expires_at      TIMESTAMPTZ NOT NULL DEFAULT (NOW() + INTERVAL '24 hours'),

    -- JWT for email-link continuity
    handoff_token   TEXT UNIQUE,

    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_edit_sessions_business
    ON edit_sessions(business_id) WHERE status = 'active';
CREATE INDEX IF NOT EXISTS idx_edit_sessions_handoff
    ON edit_sessions(handoff_token) WHERE handoff_token IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_edit_sessions_expires
    ON edit_sessions(expires_at) WHERE status = 'active';

-- ---------------------------------------------------------------------
-- 3. edit_events
--    Append-only audit log. Every patch applied is one row. Powers the
--    "undo that" command and gives us a forensic trail.
-- ---------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS edit_events (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id      UUID NOT NULL REFERENCES edit_sessions(id) ON DELETE CASCADE,
    business_id     UUID NOT NULL REFERENCES business_profiles(id) ON DELETE CASCADE,
    surface_id      TEXT NOT NULL REFERENCES editable_surfaces(id),

    -- What happened
    source          TEXT NOT NULL CHECK (source IN ('voice','text','upload','undo','system')),
    transcript      TEXT,                       -- raw voice utterance, if applicable
    patch           JSONB NOT NULL,             -- RFC 6902 JSON Patch operations applied
    inverse_patch   JSONB NOT NULL,             -- ops that reverse `patch` — powers undo
    state_before    JSONB,                      -- snapshot of the edited subtree before
    state_after     JSONB,                      -- snapshot after

    -- Optional uploaded asset reference
    asset_id        UUID,
    asset_path      TEXT,                       -- supabase storage path

    -- Provenance
    actor_type      TEXT NOT NULL DEFAULT 'customer'
                    CHECK (actor_type IN ('customer','agent','system')),
    intent_model    TEXT,                       -- which LLM parsed the intent
    intent_confidence NUMERIC(4,3),             -- 0.000 - 1.000

    -- Reversal tracking
    reversed_by     UUID REFERENCES edit_events(id),
    reversed_at     TIMESTAMPTZ,

    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_edit_events_session_time
    ON edit_events(session_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_edit_events_business_time
    ON edit_events(business_id, created_at DESC);

-- ---------------------------------------------------------------------
-- 4. RLS — businesses can only see their own sessions / events.
--    Service role (Foundation API) bypasses RLS via service key.
-- ---------------------------------------------------------------------
ALTER TABLE edit_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE edit_events   ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "edit_sessions_owner" ON edit_sessions;
CREATE POLICY "edit_sessions_owner" ON edit_sessions
    FOR ALL
    USING (business_id IN (
        SELECT id FROM business_profiles WHERE owner_user_id = auth.uid()
    ));

DROP POLICY IF EXISTS "edit_events_owner" ON edit_events;
CREATE POLICY "edit_events_owner" ON edit_events
    FOR ALL
    USING (business_id IN (
        SELECT id FROM business_profiles WHERE owner_user_id = auth.uid()
    ));

-- ---------------------------------------------------------------------
-- 5. Realtime publication — frontend subscribes to live profile changes
-- ---------------------------------------------------------------------
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_publication WHERE pubname = 'supabase_realtime'
    ) THEN
        CREATE PUBLICATION supabase_realtime;
    END IF;
END $$;

ALTER PUBLICATION supabase_realtime ADD TABLE business_profiles;
ALTER PUBLICATION supabase_realtime ADD TABLE edit_events;
ALTER PUBLICATION supabase_realtime ADD TABLE edit_sessions;

-- ---------------------------------------------------------------------
-- 6. Storage bucket for drag-drop assets
--    Run via Supabase Dashboard or supabase CLI separately:
--    supabase storage buckets create voice-edit-assets --public=false
-- ---------------------------------------------------------------------
-- (storage bucket creation is a control-plane action, not pure SQL)

-- ---------------------------------------------------------------------
-- 7. Auto-update trigger for edit_sessions.updated_at
-- ---------------------------------------------------------------------
CREATE OR REPLACE FUNCTION touch_edit_session() RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    NEW.last_activity_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trg_touch_edit_session ON edit_sessions;
CREATE TRIGGER trg_touch_edit_session
    BEFORE UPDATE ON edit_sessions
    FOR EACH ROW EXECUTE FUNCTION touch_edit_session();

-- =====================================================================
-- End of migration
-- =====================================================================
