-- switchboard_phase1_schema
-- Item I, Phase 1. Base tables from SWITCHBOARD_BUILD.md §3.3, Addendum B
-- (personalization/language, §B.3/B.4), Addendum C (tenancy, §C.3), and the
-- open_items column from 05_CONVERSATION_DISCIPLINE.md §2 (schema piece of
-- that spec is explicitly item I Phase 1's job, not item E's).
--
-- FK note: the spec's SQL references a bare `clients` table. Live-schema
-- introspection (2026-09-05) found no such table in this project — the real
-- table is foundation.client_profiles. Every `client_id`/`workspace_id`
-- below references that instead.
--
-- RLS note: every other Foundation table built this session uses
-- `service_role_all_X` policies because the FastAPI backend always talks to
-- Postgres with the service-role key — nothing in this codebase has browser
-- clients holding real Supabase-issued JWTs against this project, so
-- `auth.jwt() ->> 'workspace_id'`-style policies (as literally written in
-- the spec) would never fire for real traffic. Workspace/user isolation for
-- Switchboard is enforced in the FastAPI layer instead (every query filtered
-- by the verified Switchboard-JWT's workspace_id/user_id — see
-- app/app/switchboard/auth.py). RLS here is the same service-role-only
-- backstop as everywhere else, not a false promise of a control that
-- doesn't apply to how this backend actually talks to Postgres.

CREATE TABLE IF NOT EXISTS foundation.sb_memberships (
  workspace_id    UUID NOT NULL REFERENCES foundation.client_profiles(id),
  user_id         UUID NOT NULL,           -- opaque id from the host product's own auth (e.g. AN's Supabase Auth); no FK, different project
  role            TEXT NOT NULL DEFAULT 'member',   -- owner | admin | member | guest
  display_title   TEXT,
  photo_url       TEXT,                    -- Addendum B.4: per-membership, not global
  joined_at       TIMESTAMPTZ DEFAULT NOW(),
  revoked_at      TIMESTAMPTZ,
  PRIMARY KEY (workspace_id, user_id)
);

CREATE TABLE IF NOT EXISTS foundation.sb_threads (
  id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  client_id         UUID NOT NULL REFERENCES foundation.client_profiles(id),
  user_id           UUID NOT NULL,
  agent_slug        TEXT NOT NULL REFERENCES foundation.ai_employees(id),
  last_message_at   TIMESTAMPTZ,
  unread_count      INT DEFAULT 0,
  open_items        JSONB DEFAULT '[]',    -- [{id, asked_at, question, choices:[...], resolves_action_id, resolved_at}]
  UNIQUE (client_id, user_id, agent_slug)
);

CREATE TABLE IF NOT EXISTS foundation.sb_messages (
  id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  thread_id     UUID NOT NULL REFERENCES foundation.sb_threads(id),
  sender        TEXT NOT NULL CHECK (sender IN ('user','agent','system')),
  kind          TEXT DEFAULT 'text' CHECK (kind IN ('text','action_request','action_result','handoff','call_summary')),
  body          TEXT,
  lang_src      TEXT DEFAULT 'en',         -- Addendum B.3
  action_id     UUID REFERENCES foundation.agent_actions(id),
  created_at    TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS foundation.sb_message_renderings (
  message_id      UUID NOT NULL REFERENCES foundation.sb_messages(id),
  lang            TEXT NOT NULL,
  body_rendered   TEXT NOT NULL,
  created_at      TIMESTAMPTZ DEFAULT NOW(),
  PRIMARY KEY (message_id, lang)
);

CREATE TABLE IF NOT EXISTS foundation.sb_pins (
  client_id     UUID NOT NULL REFERENCES foundation.client_profiles(id),
  user_id       UUID NOT NULL,
  agent_slug    TEXT NOT NULL REFERENCES foundation.ai_employees(id),
  sort_order    INT DEFAULT 0,
  PRIMARY KEY (client_id, user_id, agent_slug)
);

CREATE TABLE IF NOT EXISTS foundation.sb_settings (
  client_id     UUID NOT NULL REFERENCES foundation.client_profiles(id),
  user_id       UUID NOT NULL,
  corner        TEXT DEFAULT 'bottom-left',
  hidden        BOOLEAN DEFAULT FALSE,
  default_agent TEXT REFERENCES foundation.ai_employees(id),
  bubble_color  TEXT DEFAULT '#B4672B',    -- Addendum B.1
  lang          TEXT DEFAULT 'en',
  voice_id      TEXT,
  PRIMARY KEY (client_id, user_id)
);

-- Foundation-owned entitlement mask. Not in the spec's own table list —
-- SWITCHBOARD_BUILD.md §3.1 says "Foundation serves the full roster + the
-- entitlement mask" but no client-level per-agent entitlement source exists
-- anywhere in this schema (checked live: employee_platform_subscriptions is
-- PLATFORM-level — which product surfaces an agent appears on — not
-- client-level tier gating; no client_subscriptions/client_entitlements
-- table exists). This table is the minimal real thing Switchboard needs to
-- serve a genuine (not fabricated) locked/unlocked mask per client. A real
-- pricing/billing engine can become a second writer later; nothing here
-- precludes that.
CREATE TABLE IF NOT EXISTS foundation.client_agent_entitlements (
  client_id     UUID NOT NULL REFERENCES foundation.client_profiles(id),
  agent_slug    TEXT NOT NULL REFERENCES foundation.ai_employees(id),
  unlocked      BOOLEAN NOT NULL DEFAULT FALSE,
  source        TEXT DEFAULT 'manual',      -- manual | pricing_engine | promo
  updated_at    TIMESTAMPTZ DEFAULT NOW(),
  PRIMARY KEY (client_id, agent_slug)
);

CREATE INDEX IF NOT EXISTS idx_sb_threads_client_user ON foundation.sb_threads(client_id, user_id);
CREATE INDEX IF NOT EXISTS idx_sb_messages_thread ON foundation.sb_messages(thread_id, created_at);
CREATE INDEX IF NOT EXISTS idx_sb_memberships_user ON foundation.sb_memberships(user_id);

DO $$
DECLARE t TEXT;
BEGIN
  FOREACH t IN ARRAY ARRAY['sb_memberships','sb_threads','sb_messages','sb_message_renderings','sb_pins','sb_settings','client_agent_entitlements']
  LOOP
    EXECUTE format('ALTER TABLE foundation.%I ENABLE ROW LEVEL SECURITY', t);
    EXECUTE format('DROP POLICY IF EXISTS "service_role_all_%s" ON foundation.%I', t, t);
    EXECUTE format('CREATE POLICY "service_role_all_%s" ON foundation.%I FOR ALL USING (auth.role() = ''service_role'')', t, t);
  END LOOP;
END $$;
