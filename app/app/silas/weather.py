"""
Weather-conflict checking for weather-sensitive jobs. Per-client rules are
real and enforced; fetching a live forecast is not — no WEATHER_API_KEY
and no StormReach client access exist in this build (the spec says "reuse
StormReach's weather-trigger source" but that source isn't reachable from
here). fetch_forecast() is an honest stub, not a silent no-op: it raises
rather than inventing a forecast. check_conflicts() takes an already-known
forecast dict so the conflict LOGIC is real and testable independent of
where the forecast data comes from.
"""
from typing import Optional

WEATHER_RULES: dict[str, dict] = {
    # keyed by client business_name for now -- move to a per-client config
    # column once more than a couple of clients have weather-sensitive jobs.
    "Exterior Rescue WNY": {"job_types": ["roof_repair"], "max_precip_pct": 40, "max_wind_mph": 25},
}


def get_rules(business_name: str) -> Optional[dict]:
    return WEATHER_RULES.get(business_name)


def fetch_forecast(location_lat: float, location_lon: float, for_date) -> dict:
    """TODO: wire to a real weather provider (reusing StormReach's source per
    spec, or a direct NWS/OpenWeather call) once one is reachable from here.
    Raises rather than returning fabricated conditions."""
    raise NotImplementedError(
        "no live weather source configured -- see module docstring. "
        "Pass a forecast dict directly to check_conflicts() for testing."
    )


def check_conflicts(jobs: list[dict], rules: dict, forecast: dict) -> list[dict]:
    """jobs: [{"id", "job_type", ...}], forecast: {"precip_pct": int, "wind_mph": int}.
    Returns the subset of jobs that conflict with the weather rules."""
    if forecast.get("precip_pct", 0) <= rules["max_precip_pct"] and forecast.get("wind_mph", 0) <= rules["max_wind_mph"]:
        return []
    return [j for j in jobs if j["job_type"] in rules["job_types"]]
