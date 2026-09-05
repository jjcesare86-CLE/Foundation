-- connections_hub_schema
-- Item C: bring client_connections up to the Connections Hub spec's shape
-- (Part 4) on top of the table already created for item A/D
-- (20260905170001_client_connections.sql). Keeps the existing
-- access_token_encrypted/refresh_token_encrypted/connection_type columns
-- (Fernet, per the later decision that supersedes this spec's
-- Vault/pgsodium line -- see DECISIONS.md 2026-07-08 and 2026-09-05).

ALTER TABLE foundation.client_connections
  ADD COLUMN IF NOT EXISTS provider_scope TEXT,
  ADD COLUMN IF NOT EXISTS display_name TEXT,
  ADD COLUMN IF NOT EXISTS last_verified_at TIMESTAMPTZ,
  ADD COLUMN IF NOT EXISTS error_detail TEXT;

-- Spec wants uniqueness per (client, provider, provider_scope, external
-- account) rather than just (client, provider) -- e.g. separate rows for
-- Gmail vs Calendar under the same Google account. Drop the coarser
-- constraint from the original table and add the finer one.
DO $$
DECLARE
  v_constraint TEXT;
BEGIN
  SELECT conname INTO v_constraint
  FROM pg_constraint
  WHERE conrelid = 'foundation.client_connections'::regclass
    AND contype = 'u';

  IF v_constraint IS NOT NULL THEN
    EXECUTE format('ALTER TABLE foundation.client_connections DROP CONSTRAINT %I', v_constraint);
  END IF;

  ALTER TABLE foundation.client_connections
    ADD CONSTRAINT client_connections_scope_unique
    UNIQUE (client_id, provider, provider_scope, external_account_id);
END $$;
