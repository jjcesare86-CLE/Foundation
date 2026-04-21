"""
Foundation API — Employees Router
Supabase-backed. Storage + retrieval only. NO tier gating, NO caps, NO subscription
enforcement. Each platform (AN, Assistmeo, VoiceMIO, Blast Video, MRLIN) is
responsible for checking its own client subscriptions and serving accordingly.

Foundation just stores the catalog. Platforms enforce.
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List
from app.database import supabase
from app.llm_router import llm_call, MODEL_MAP, TaskTier

router = APIRouter(prefix="/employees", tags=["employees"])

# ── DISPLAY-ONLY tier metadata. NEVER used to gate or cap.
# Platforms read this from the API and use it to build their own pricing pages.
# Foundation never enforces any of this.
TIER_DISPLAY_META = {
    "starter":      {"price": "$199/mo",   "suggested_count": 3,  "featured_departments": ["Sales"]},
    "essentials":   {"price": "$299/mo",   "suggested_count": 6,  "featured_departments": ["Sales", "Marketing"]},
    "professional": {"price": "$999/mo",   "suggested_count": 10, "featured_departments": ["Sales", "Marketing", "Operations"]},
    "enterprise":   {"price": "$1,999/mo", "suggested_count": 26, "featured_departments": ["All"]},
}

# Maps tier_name → list of tier_access column values that should be
# *suggested* at that marketing tier. DISPLAY-ONLY. Not a gate.
TIER_ACCESS_DISPLAY = {
    "starter":      ["All"],
    "essentials":   ["All", "Essentials+"],
    "professional": ["All", "Essentials+", "Professional+"],
    "enterprise":   ["All", "Essentials+", "Professional+", "Enterprise"],
}

CORE_DEPARTMENTS = {
    "Sales", "Marketing", "Operations",
    "People & Culture", "Legal & Strategy", "C-Suite",
}


def _resolve_model(model_tier: str) -> str:
    """Map model_tier column value to actual model ID via llm_router."""
    tier_map = {
        "orchestrator": TaskTier.COMPLEX,
        "standard":     TaskTier.STANDARD,
        "fast":         TaskTier.FAST,
    }
    task_tier = tier_map.get(model_tier, TaskTier.STANDARD)
    return MODEL_MAP.get(task_tier, MODEL_MAP[TaskTier.STANDARD])


def _fetch_employees(
    platform: str,
    include_system_prompt: bool = False,
    department: Optional[str] = None,
) -> list:
    """All active employees subscribed to a platform. No gating, no caps."""
    cols = (
        "id,name,biblical_name,product_name,role,department,department_label,"
        "model_tier,tier_access,is_csuite,is_confidential,style,helps,"
        "outside_scope,handoff_to,covers_for,covered_by,reports_to,supervises,color,bg,config"
    )
    if include_system_prompt:
        cols += ",system_prompt"

    subs = (
        supabase.schema("foundation")
        .table("employee_platform_subscriptions")
        .select("employee_id")
        .eq("platform_slug", platform)
        .eq("is_active", True)
        .execute()
    )
    subscribed_ids = [r["employee_id"] for r in (subs.data or [])]
    if not subscribed_ids:
        return []

    query = (
        supabase.schema("foundation")
        .table("ai_employees")
        .select(cols)
        .eq("is_active", True)
        .in_("id", subscribed_ids)
    )
    if department:
        query = query.eq("department", department)

    employees = (query.execute().data) or []
    for emp in employees:
        emp["resolved_model"] = _resolve_model(emp.get("model_tier", "standard"))
    return employees


def _group_by_department(employees: list) -> dict:
    groups: dict = {}
    for emp in employees:
        dept = emp.get("department_label", emp.get("department", "Other"))
        groups.setdefault(dept, []).append(emp["name"])
    return groups


def _log_sync(platform: str, count: int):
    try:
        supabase.schema("foundation").table("employee_sync_log").insert({
            "platform_slug": platform,
            "employee_count": count,
            "sync_status": "success",
        }).execute()
    except Exception:
        pass


# ── ENDPOINTS ──────────────────────────────────────────────────────────

@router.get("/")
async def list_employees(
    platform: str = Query("automation-nation"),
    department: Optional[str] = Query(None),
):
    """All active employees for a platform. No caps, no gating."""
    employees = _fetch_employees(platform, department=department)
    _log_sync(platform, len(employees))
    return employees


@router.get("/tiers")
async def list_tiers():
    """Display-only tier metadata. NOT an access gate."""
    return TIER_DISPLAY_META


@router.get("/tiers/{tier_name}/coverage")
async def tier_coverage(
    tier_name: str,
    platform: str = Query("automation-nation"),
):
    """Which employees are *suggested* for this tier based on tier_access metadata.
    Platforms use this to build their pricing pages. NOT an access gate.
    """
    if tier_name not in TIER_DISPLAY_META:
        raise HTTPException(status_code=404, detail=f"Tier '{tier_name}' not found")

    allowed_access_values = TIER_ACCESS_DISPLAY.get(tier_name, [])
    all_employees = _fetch_employees(platform)
    suggested = [e for e in all_employees if e.get("tier_access") in allowed_access_values]

    return {
        "tier": tier_name,
        "tier_info": TIER_DISPLAY_META[tier_name],
        "suggested_count": len(suggested),
        "suggested_employees": suggested,
        "department_coverage": _group_by_department(suggested),
    }


@router.post("/coverage")
async def custom_coverage(
    employee_ids: List[str],
    platform: str = Query("automation-nation"),
):
    """Department coverage analysis for an arbitrary employee set."""
    all_employees = _fetch_employees(platform)
    selected = [e for e in all_employees if e["id"] in employee_ids]
    departments = _group_by_department(selected)
    return {
        "selected_count": len(selected),
        "employees": selected,
        "department_coverage": departments,
        "gaps": sorted(CORE_DEPARTMENTS - set(departments.keys())),
    }


class GeneratePromptRequest(BaseModel):
    employee_name: str
    role: str
    department: Optional[str] = None
    style: Optional[str] = None
    helps: Optional[str] = None
    outside_scope: Optional[str] = None
    business_context: Optional[str] = None


@router.post("/generate-prompt")
async def generate_prompt(req: GeneratePromptRequest):
    """Claude-powered custom agent prompt builder."""
    user_message = f"""Generate a professional AI employee system prompt for:
Name: {req.employee_name}
Role: {req.role}
Department: {req.department or 'General'}
Communication Style: {req.style or 'Professional'}
Primary Responsibilities: {req.helps or 'Not specified'}
Outside Their Scope: {req.outside_scope or 'Not specified'}
Business Context: {req.business_context or 'AI automation agency'}

The system prompt should be concise (under 300 words), define clear boundaries,
and specify handoff behavior when requests fall outside scope."""

    response_text = llm_call(
        messages=[{"role": "user", "content": user_message}],
        tier=TaskTier.STANDARD,
        max_tokens=600,
        project="foundation",
        agent_name="employees_generate_prompt",
        task_type="custom_agent_prompt",
    )
    return {
        "employee_name": req.employee_name,
        "role": req.role,
        "system_prompt": response_text,
    }


@router.get("/csuite/all")
async def get_csuite(platform: str = Query("automation-nation")):
    """All C-suite agents for a platform."""
    employees = _fetch_employees(platform)
    csuite = [e for e in employees if e.get("is_csuite")]
    return {"csuite": csuite, "total": len(csuite)}


@router.get("/sync/status")
async def sync_status(platform: str = Query("automation-nation")):
    """When did this platform last sync?"""
    result = (
        supabase.schema("foundation")
        .table("employee_sync_log")
        .select("*")
        .eq("platform_slug", platform)
        .order("synced_at", desc=True)
        .limit(1)
        .execute()
    )
    return {"platform": platform, "last_sync": result.data[0] if result.data else None}


@router.get("/{employee_id}")
async def get_employee(
    employee_id: str,
    platform: str = Query("automation-nation"),
    include_system_prompt: bool = Query(False),
):
    """Get a single employee by ID. Raises 404 if not subscribed to platform."""
    employees = _fetch_employees(platform, include_system_prompt=include_system_prompt)
    match = next((e for e in employees if e["id"] == employee_id), None)
    if not match:
        raise HTTPException(
            status_code=404,
            detail=f"Employee '{employee_id}' not found for platform '{platform}'",
        )
    return match
