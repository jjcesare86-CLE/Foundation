-- caleb_legacy_slug
-- Follow-up to 20260905120000_caleb_ciso_nehemiah_coo.sql: Caleb's id
-- ('caleb-coo') still embeds the old COO role even though the id itself
-- wasn't renamed. Per spec, record that in legacy_slug anyway so anything
-- scanning for role-changed agents finds Caleb too.

UPDATE foundation.ai_employees
SET legacy_slug = 'caleb-coo', updated_at = NOW()
WHERE id = 'caleb-coo' AND legacy_slug IS NULL;
