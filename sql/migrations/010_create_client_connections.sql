-- 010_create_client_connections.sql
-- Connection broker — encrypted third-party credentials per client
-- Safe to run whether or not foundation.client_connections already exists

CREATE TABLE IF NOT EXISTS foundation.client_connections (
  id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  client_id               UUID NOT NULL REFERENCES foundation.client_profiles(id),
  provider                TEXT NOT NULL,
  connection_type         TEXT NOT NULL DEFAULT 'oauth' CHECK (connection_type IN ('oauth', 'api_key')),
  status                  TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'expired', 'revoked', 'error')),
  access_token_encrypted  TEXT,
  refresh_token_encrypted TEXT,
  token_expires_at        TIMESTAMPTZ,
  scopes                  TEXT[] DEFAULT '{}',
  external_account_id     TEXT,
  metadata                JSONB DEFAULT '{}',
  last_refreshed_at       TIMESTAMPTZ,
  created_at              TIMESTAMPTZ DEFAULT NOW(),
  updated_at              TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE (client_id, provider)
);

CREATE INDEX IF NOT EXISTS idx_client_connections_client
  ON foundation.client_connections(client_id, provider);

-- ── RLS — service-role-only, no public read (holds encrypted credentials) ──
ALTER TABLE foundation.client_connections ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "service_role_all_client_connections" ON foundation.client_connections;
CREATE POLICY "service_role_all_client_connections"
  ON foundation.client_connections FOR ALL
  USING (auth.role() = 'service_role');
