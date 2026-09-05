"""
Daily dispatch builder: assigns each scheduled job to a crew by required
skills, then orders each crew's stops with a greedy nearest-neighbor tour
from the crew's home base.

Route ordering here is straight-line (haversine) distance via PostGIS
coordinates (see migration silas_geo_helpers), NOT real drive time. It's a
genuine, working stand-in for Google Maps Distance Matrix — swapping in
real drive-time is a matter of replacing _distance() below with a Distance
Matrix lookup once GOOGLE_MAPS_API_KEY is configured; nothing else in this
module needs to change.
"""
import math
from datetime import date as date_type

from app.database import supabase


def _haversine_km(lon1: float, lat1: float, lon2: float, lat2: float) -> float:
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlambda / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def build_dispatch(client_id: str, for_date: date_type) -> dict:
    crews = supabase.schema("foundation").rpc("fs_crew_coords", {"p_client_id": client_id}).execute().data
    jobs = supabase.schema("foundation").rpc(
        "fs_job_coords", {"p_client_id": client_id, "p_date": for_date.isoformat()}
    ).execute().data
    jobs = [j for j in jobs if j["status"] == "scheduled"]

    assignments: dict[str, list[dict]] = {c["id"]: [] for c in crews}
    unassigned: list[dict] = []

    for job in jobs:
        required = set(job["required_skills"] or [])
        candidates = [c for c in crews if required.issubset(set(c["skills"] or []))]
        if not candidates:
            unassigned.append(job)
            continue
        # Load-balance: assign to whichever qualifying crew has fewest jobs so far.
        crew = min(candidates, key=lambda c: len(assignments[c["id"]]))
        assignments[crew["id"]].append(job)

    for crew in crews:
        ordered = _nearest_neighbor_order(crew["lon"], crew["lat"], assignments[crew["id"]])
        for i, job in enumerate(ordered):
            supabase.schema("foundation").table("fs_jobs").update({
                "crew_id": crew["id"], "route_order": i, "status": "dispatched",
            }).eq("id", job["id"]).execute()

    return {
        "date": for_date.isoformat(),
        "crews_used": len([c for c in crews if assignments[c["id"]]]),
        "jobs_dispatched": sum(len(v) for v in assignments.values()),
        "unassigned": [j["id"] for j in unassigned],
    }


def _nearest_neighbor_order(start_lon: float, start_lat: float, jobs: list[dict]) -> list[dict]:
    remaining = list(jobs)
    ordered = []
    cur_lon, cur_lat = start_lon, start_lat
    while remaining:
        nearest = min(remaining, key=lambda j: _haversine_km(cur_lon, cur_lat, j["lon"], j["lat"]))
        ordered.append(nearest)
        remaining.remove(nearest)
        cur_lon, cur_lat = nearest["lon"], nearest["lat"]
    return ordered
