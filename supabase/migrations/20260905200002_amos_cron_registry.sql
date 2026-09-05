-- amos_cron_registry
-- Register the amos-daily cron in agent_jobs (heartbeat retrofit already
-- lives in the script itself, per the same pattern as the other crons).
INSERT INTO foundation.agent_jobs (agent_slug, job_name, schedule_cron, schedule_interval_minutes)
VALUES ('amos-compliance', 'amos-daily', '0 7 * * *', 1440)
ON CONFLICT (agent_slug, job_name) DO NOTHING;
