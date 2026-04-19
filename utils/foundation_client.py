"""
utils/foundation_client.py
Foundation client utility — used by AN, Assistmeo, and any future platform.
All employee data comes from Foundation. No platform maintains its own list.

Drop a copy of this file into the AN repo at utils/foundation_client.py.
Set FOUNDATION_API_URL in the AN repo's Render env vars.
"""

import os
import httpx
from typing import Optional

FOUNDATION_URL = os.getenv(
    "FOUNDATION_API_URL",
    "https://foundation-api-9gpl.onrender.com"
)
TIMEOUT = 10


async def get_employees(
    platform: str = "automation-nation",
    department: Optional[str] = None,
) -> list:
    """List all active employees for a platform."""
    params = {"platform": platform}
    if department:
        params["department"] = department
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        resp = await client.get(f"{FOUNDATION_URL}/employees/", params=params)
        resp.raise_for_status()
        return resp.json()


async def get_employee(
    employee_id: str,
    platform: str = "automation-nation",
    include_system_prompt: bool = False,
) -> dict:
    """Get a single employee by ID. Set include_system_prompt=True to fetch the full prompt."""
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        resp = await client.get(
            f"{FOUNDATION_URL}/employees/{employee_id}",
            params={"platform": platform, "include_system_prompt": include_system_prompt},
        )
        resp.raise_for_status()
        return resp.json()


async def get_csuite(platform: str = "automation-nation") -> list:
    """Get all C-suite agents for a platform."""
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        resp = await client.get(
            f"{FOUNDATION_URL}/employees/csuite/all",
            params={"platform": platform},
        )
        resp.raise_for_status()
        return resp.json()["csuite"]


async def get_tier_coverage(
    tier: str,
    platform: str = "automation-nation",
) -> dict:
    """Get coverage analysis for a named tier (starter/essentials/professional/enterprise)."""
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        resp = await client.get(
            f"{FOUNDATION_URL}/employees/tiers/{tier}/coverage",
            params={"platform": platform},
        )
        resp.raise_for_status()
        return resp.json()
