-- silas_agent
-- Batch 1 Phase 4, Agent 29: SILAS — Field Service Dispatcher (HyperSchedule
-- Phase 1). Seed client: Exterior Rescue WNY, 2 demo crews, 8 demo jobs.

CREATE EXTENSION IF NOT EXISTS postgis;

INSERT INTO foundation.client_profiles (business_name, industry, onboarding_platform, status)
SELECT 'Exterior Rescue WNY', 'home_services_roofing', 'automation-nation', 'active'
WHERE NOT EXISTS (SELECT 1 FROM foundation.client_profiles WHERE business_name = 'Exterior Rescue WNY');

INSERT INTO foundation.ai_employees (
  id, name, biblical_name, product_name, role, department, department_label,
  model_tier, tier_access, is_csuite, is_confidential, style, helps,
  outside_scope, handoff_to, covers_for, covered_by, reports_to, supervises,
  color, bg, config, is_active, system_prompt
) VALUES (
  'silas-dispatch', 'SID', 'Silas', 'Silas', 'Field Service Dispatcher',
  'operations', 'Operations', 'standard', 'Professional+', FALSE, FALSE,
  'Calm under pressure, radio-operator crisp',
  'Daily job board to crew assignments, route ordering, customer ETA/status texts, weather-triggered rescheduling, crew clock-in reconciliation, cancellation backfill via atomic slot claims',
  'New-customer booking — redirect to SAGE; invoicing after job completion — redirect to JOANNA; review request after completion is automatic (handoff to RAE)',
  ARRAY['sage','joanna-finance','rahab-reputation'], ARRAY[]::text[], ARRAY[]::text[],
  'nehemiah-coo', ARRAY[]::text[],
  '#D85A30', '#FAECE7', '{}'::jsonb, TRUE,
$prompt$You are Silas, the Field Service Dispatcher for {business_name}. Crews on the road,
customers waiting — your job is that everyone is in the right place at the right time
and nobody is surprised.

PERSONALITY: Calm, crisp, decisive. Radio-operator style with crews (short, exact).
Warm and reassuring with customers. You never over-promise an ETA.

YOUR JOB:
1. Each morning build the day's dispatch: assign jobs to crews by required skills,
   territory, and drive time; order each crew's stops to minimize total driving.
2. Send each crew their run sheet (jobs, addresses, notes, materials) by {dispatch_time}.
3. Customer comms via SMS: confirmation night before; "on our way, ETA {window}" at
   dispatch; proactive delay notices the moment a slip is detected (never let a
   customer discover lateness on their own).
4. Weather watch: check forecasts against weather-sensitive job types
   ({weather_rules}). Flag conflicts by {cutoff_time} the day before, propose
   reschedule slots, and message affected customers once the owner approves.
5. Cancellations: immediately offer the open slot to the waitlist in priority order;
   first confirmed reply claims it (atomic — never double-book a slot).
6. Reconcile GPS clock-ins vs schedule; flag no-shows, long-runners, and jobs at
   risk of slipping, with a suggested shuffle.
7. End of day: recap to the owner — completed, slipped (why), revenue on the truck
   tomorrow.

HARD RULES:
- Never double-book a crew or a slot. Slot claims are first-confirm-wins, atomic.
- ETAs are windows, never exact minutes. Under-promise.
- Reschedules that move a customer more than 24h require owner approval first.
- Safety-critical weather rules ({weather_rules}) are non-negotiable — you never
  suggest 'squeezing in' a job that violates them.
- Crew personal data stays internal; customers never see crew phone numbers or names
  beyond first name.

DATA ACCESS: via connection_broker (calendar, GHL contacts/SMS, GPS clock-in feed,
weather API). Missing → "I need {service} connected first — Connect Your Accounts."

HANDOFFS: new bookings → Naomi, invoices → Joanna, review requests → Rahab (auto
on job completion).$prompt$
)
ON CONFLICT (id) DO UPDATE SET
  role = EXCLUDED.role, helps = EXCLUDED.helps, outside_scope = EXCLUDED.outside_scope,
  handoff_to = EXCLUDED.handoff_to, system_prompt = EXCLUDED.system_prompt,
  updated_at = NOW();

INSERT INTO foundation.employee_platform_subscriptions (platform_slug, employee_id, is_active)
SELECT DISTINCT platform_slug, 'silas-dispatch', TRUE
FROM foundation.employee_platform_subscriptions
ON CONFLICT (platform_slug, employee_id) DO NOTHING;

-- ── HyperSchedule Phase 1 schema ───────────────────────────────────────
CREATE TABLE IF NOT EXISTS foundation.fs_crews (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  client_id   UUID NOT NULL REFERENCES foundation.client_profiles(id),
  crew_name   TEXT NOT NULL,
  skills      TEXT[] DEFAULT '{}',
  home_base   GEOGRAPHY(POINT),
  active      BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS foundation.fs_jobs (
  id                    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  client_id             UUID NOT NULL REFERENCES foundation.client_profiles(id),
  customer_contact_id   TEXT,                     -- GHL contact
  job_type              TEXT NOT NULL,
  required_skills       TEXT[] DEFAULT '{}',
  location              GEOGRAPHY(POINT),
  address               TEXT,
  scheduled_date        DATE,
  time_window           TSTZRANGE,
  crew_id               UUID REFERENCES foundation.fs_crews(id),
  route_order           INT,
  status                TEXT DEFAULT 'scheduled'
                          CHECK (status IN ('scheduled','dispatched','enroute','onsite','done','slipped','cancelled')),
  weather_sensitive     BOOLEAN DEFAULT FALSE,
  est_duration_min      INT,
  notes                 TEXT
);

CREATE INDEX IF NOT EXISTS idx_fs_jobs_client_date ON foundation.fs_jobs(client_id, scheduled_date);
CREATE INDEX IF NOT EXISTS idx_fs_jobs_crew ON foundation.fs_jobs(crew_id, scheduled_date);

CREATE TABLE IF NOT EXISTS foundation.fs_slot_offers (
  id                    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  client_id             UUID NOT NULL REFERENCES foundation.client_profiles(id),
  job_id                UUID REFERENCES foundation.fs_jobs(id),
  offered_to_contact_id TEXT NOT NULL,
  offered_at            TIMESTAMPTZ DEFAULT NOW(),
  expires_at            TIMESTAMPTZ,
  status                TEXT DEFAULT 'offered' CHECK (status IN ('offered','claimed','expired','declined'))
);

CREATE INDEX IF NOT EXISTS idx_fs_slot_offers_job ON foundation.fs_slot_offers(job_id, status);

ALTER TABLE foundation.fs_crews ENABLE ROW LEVEL SECURITY;
ALTER TABLE foundation.fs_jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE foundation.fs_slot_offers ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "service_role_all_fs_crews" ON foundation.fs_crews;
CREATE POLICY "service_role_all_fs_crews" ON foundation.fs_crews FOR ALL USING (auth.role() = 'service_role');

DROP POLICY IF EXISTS "service_role_all_fs_jobs" ON foundation.fs_jobs;
CREATE POLICY "service_role_all_fs_jobs" ON foundation.fs_jobs FOR ALL USING (auth.role() = 'service_role');

DROP POLICY IF EXISTS "service_role_all_fs_slot_offers" ON foundation.fs_slot_offers;
CREATE POLICY "service_role_all_fs_slot_offers" ON foundation.fs_slot_offers FOR ALL USING (auth.role() = 'service_role');

-- Atomic, first-confirm-wins slot claim. FOR UPDATE SKIP LOCKED means a
-- second concurrent caller never blocks waiting on the first — it simply
-- finds nothing to claim and returns claimed=false immediately.
CREATE OR REPLACE FUNCTION foundation.claim_slot(p_offer_id UUID, p_contact_id TEXT)
RETURNS TABLE(claimed BOOLEAN, offer_id UUID) AS $$
DECLARE
  v_id UUID;
BEGIN
  SELECT id INTO v_id
  FROM foundation.fs_slot_offers
  WHERE id = p_offer_id
    AND status = 'offered'
    AND (expires_at IS NULL OR expires_at > NOW())
  FOR UPDATE SKIP LOCKED;

  IF v_id IS NULL THEN
    RETURN QUERY SELECT FALSE, p_offer_id;
    RETURN;
  END IF;

  UPDATE foundation.fs_slot_offers
  SET status = 'claimed', offered_to_contact_id = p_contact_id
  WHERE id = v_id;

  RETURN QUERY SELECT TRUE, v_id;
END;
$$ LANGUAGE plpgsql;

-- ── Seed: Exterior Rescue WNY, 2 crews, 8 jobs ─────────────────────────
DO $$
DECLARE
  v_client_id UUID;
  v_crew1_id UUID;
  v_crew2_id UUID;
BEGIN
  SELECT id INTO v_client_id FROM foundation.client_profiles WHERE business_name = 'Exterior Rescue WNY';

  IF NOT EXISTS (SELECT 1 FROM foundation.fs_crews WHERE client_id = v_client_id) THEN
    INSERT INTO foundation.fs_crews (client_id, crew_name, skills, home_base)
    VALUES (v_client_id, 'Crew Alpha', ARRAY['roofing','gutter'], ST_GeogFromText('POINT(-78.8784 42.8864)'))
    RETURNING id INTO v_crew1_id;

    INSERT INTO foundation.fs_crews (client_id, crew_name, skills, home_base)
    VALUES (v_client_id, 'Crew Bravo', ARRAY['power_wash','gutter'], ST_GeogFromText('POINT(-78.8784 42.8864)'))
    RETURNING id INTO v_crew2_id;

    -- 8 demo jobs scattered around the Buffalo, NY metro area, today's date.
    INSERT INTO foundation.fs_jobs (client_id, job_type, required_skills, location, address, scheduled_date, weather_sensitive, est_duration_min, status)
    VALUES
      (v_client_id, 'roof_repair',  ARRAY['roofing'],    ST_GeogFromText('POINT(-78.8500 42.9000)'), '100 Elmwood Ave, Buffalo NY',  CURRENT_DATE, TRUE,  120, 'scheduled'),
      (v_client_id, 'gutter_clean', ARRAY['gutter'],     ST_GeogFromText('POINT(-78.7300 42.9500)'), '200 Sheridan Dr, Tonawanda NY', CURRENT_DATE, FALSE,  60, 'scheduled'),
      (v_client_id, 'power_wash',   ARRAY['power_wash'], ST_GeogFromText('POINT(-78.7800 42.8600)'), '300 Delaware Ave, Buffalo NY',  CURRENT_DATE, FALSE,  90, 'scheduled'),
      (v_client_id, 'roof_repair',  ARRAY['roofing'],    ST_GeogFromText('POINT(-78.6200 42.9700)'), '400 Niagara Falls Blvd, Amherst NY', CURRENT_DATE, TRUE, 150, 'scheduled'),
      (v_client_id, 'gutter_clean', ARRAY['gutter'],     ST_GeogFromText('POINT(-78.9100 42.8300)'), '500 South Park Ave, Buffalo NY', CURRENT_DATE, FALSE, 60, 'scheduled'),
      (v_client_id, 'power_wash',   ARRAY['power_wash'], ST_GeogFromText('POINT(-78.7000 42.9100)'), '600 Main St, Williamsville NY', CURRENT_DATE, FALSE, 90, 'scheduled'),
      (v_client_id, 'roof_repair',  ARRAY['roofing'],    ST_GeogFromText('POINT(-78.8200 42.9800)'), '700 Kenmore Ave, Kenmore NY', CURRENT_DATE, TRUE, 120, 'scheduled'),
      (v_client_id, 'gutter_clean', ARRAY['gutter'],     ST_GeogFromText('POINT(-78.7600 42.8100)'), '800 Seneca St, Buffalo NY', CURRENT_DATE, FALSE, 60, 'scheduled');
  END IF;
END $$;
