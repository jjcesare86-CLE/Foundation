-- silas_geo_helpers
-- PostgREST can't select computed geometry expressions directly, so these
-- two read-only functions expose job/crew coordinates as plain lon/lat for
-- the Python-side nearest-neighbor route builder (dispatch.py). This is a
-- straight-line approximation standing in for Google Maps Distance Matrix
-- (real drive-time) until GOOGLE_MAPS_API_KEY is configured.

CREATE OR REPLACE FUNCTION foundation.fs_job_coords(p_client_id UUID, p_date DATE)
RETURNS TABLE(id UUID, job_type TEXT, required_skills TEXT[], lon DOUBLE PRECISION, lat DOUBLE PRECISION, weather_sensitive BOOLEAN, address TEXT, status TEXT)
LANGUAGE sql STABLE AS $$
  SELECT id, job_type, required_skills, ST_X(location::geometry), ST_Y(location::geometry), weather_sensitive, address, status
  FROM foundation.fs_jobs
  WHERE client_id = p_client_id AND scheduled_date = p_date;
$$;

CREATE OR REPLACE FUNCTION foundation.fs_crew_coords(p_client_id UUID)
RETURNS TABLE(id UUID, crew_name TEXT, skills TEXT[], lon DOUBLE PRECISION, lat DOUBLE PRECISION)
LANGUAGE sql STABLE AS $$
  SELECT id, crew_name, skills, ST_X(home_base::geometry), ST_Y(home_base::geometry)
  FROM foundation.fs_crews
  WHERE client_id = p_client_id AND active = TRUE;
$$;
