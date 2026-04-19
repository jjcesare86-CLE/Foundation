"""
Foundation API — Employees Router
Supabase-backed. Single source of truth for all platforms.
All existing endpoints preserved with identical response shapes.
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List
from app.database import supabase
from app.llm_router import llm_call, MODEL_MAP, TaskTier

router = APIRouter(prefix="/employees", tags=["employees"])

# Assistmeo subscription tier gating
ASSISTMEO_TIER_LIMITS = {
    "starter":      3,
    "essentials":   6,
    "professional": 10,
    "enterprise":   99,
}

# Tier pack metadata (mirrors original hardcoded packs)
TIER_PACKS = {
    "starter":      {"price": "$199/mo",   "count": 3,  "departments": ["Sales"]},
    "essentials":   {"price": "$299/mo",   "count": 6,  "departments": ["Sales", "Marketing"]},
    "professional": {"price": "$999/mo",   "count": 10, "departments": ["Sales", "Marketing", "Operations"]},
    "enterprise":   {"price": "$1,999/mo", "count": 26, "departments": ["All"]},
}

TIER_ACCESS_MAP = {
    "All":           ["starter", "essentials", "professional", "enterprise"],
    "Essentials+":   ["essentials", "professional", "enterprise"],
    "Professional+": ["professional", "enterprise"],
    "Enterprise":    ["enterprise"],
}

CORE_DEPARTMENTS = {
    "Sales", "Marketing", "Operations",
    "People & Culture", "Legal & Strategy", "C-Suite"
}


def _resolve_model(model_tier: str) -> str:
    """Map model_tier string to actual model ID via llm_router."""
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
    """Core Supabase query — employees for a platform."""
    cols = (
        "id,name,biblical_name,product_name,role,department,department_label,"
        "model_tier,tier_access,is_csuite,is_confidential,style,helps,"
        "outside_scope,handoff_to,covers_for,covered_by,reports_to,supervises,color,bg,config"
    )
    if include_system_prompt:
        cols += ",system_prompt"

    # Get subscribed employee IDs for this platform
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

    result = query.execute()
    employees = result.data or []

    # Attach resolved model string
    for emp in employees:
        emp["resolved_model"] = _resolve_model(emp.get("model_tier", "standard"))

    return employees


def _identify_gaps(department_coverage: dict) -> list:
    """Flag core departments with no coverage."""
    return list(CORE_DEPARTMENTS - set(department_coverage.keys()))


def _log_sync(platform: str, count: int):
    """Fire-and-forget sync log — never block on logging failures."""
    try:
        supabase.schema("foundation").table("employee_sync_log").insert({
            "platform_slug": platform,
            "employee_count": count,
            "sync_status": "success",
        }).execute()
    except Exception:
        pass


# ── PRESERVED ENDPOINTS (identical response shapes) ───────────────────────

@router.get("/")
async def list_employees(
    platform: str = Query("automation-nation"),
    department: Optional[str] = Query(None),
):
    """List all active employees for a platform."""
    employees = _fetch_employees(platform, department=department)
    _log_sync(platform, len(employees))
    return employees  # bare list — same as original


@router.get("/tiers")
async def list_tiers():
    """List all available tier packs. PRESERVED from original."""
    return TIER_PACKS


@router.get("/tiers/{tier_name}/coverage")
async def tier_coverage(
    tier_name: str,
    platform: str = Query("automation-nation"),
):
    """Coverage analysis for a named tier. PRESERVED from original."""
    if tier_name not in TIER_PACKS:
        raise HTTPException(status_code=404, detail=f"Tier '{tier_name}' not found")

    all_employees = _fetch_employees(platform)
    allowed = TIER_ACCESS_MAP

    tier_employees = [
        e for e in all_employees
        if tier_name in allowed.get(e.get("tier_access", "All"), [])
    ]

    departments: dict = {}
    for emp in tier_employees:
        dept = emp.get("department_label", emp.get("department", "Other"))
        departments.setdefault(dept, []).append(emp["name"])

    return {
        "tier": tier_name,
        "tier_info": TIER_PACKS[tier_name],
        "employee_count": len(tier_employees),
        "employees": tier_employees,
        "department_coverage": departments,
        "gaps": _identify_gaps(departments),
    }


@router.post("/coverage")
async def custom_coverage(
    employee_ids: List[str],
    platform: str = Query("automation-nation"),
):
    """Coverage for a custom employee set. PRESERVED from original."""
    all_employees = _fetch_employees(platform)
    selected = [e for e in all_employees if e["id"] in employee_ids]

    departments: dict = {}
    for emp in selected:
        dept = emp.get("department_label", emp.get("department", "Other"))
        departments.setdefault(dept, []).append(emp["name"])

    return {
        "selected_count": len(selected),
        "employees": selected,
        "department_coverage": departments,
        "gaps": _identify_gaps(departments),
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
    """Claude-powered custom agent builder. PRESERVED — uses llm_call()."""
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


# ── NEW ENDPOINTS ─────────────────────────────────────────────────────────

@router.get("/csuite/all")
async def get_csuite(platform: str = Query("automation-nation")):
    """Get all C-suite agents. Used by orchestration layer."""
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
    return {
        "platform": platform,
        "last_sync": result.data[0] if result.data else None,
    }


@router.get("/{employee_id}")
async def get_employee(
    employee_id: str,
    platform: str = Query("automation-nation"),
    include_system_prompt: bool = Query(False),
):
    """Get a single employee by ID."""
    employees = _fetch_employees(platform, include_system_prompt=include_system_prompt)
    match = next((e for e in employees if e["id"] == employee_id), None)
    if not match:
        raise HTTPException(
            status_code=404,
            detail=f"Employee '{employee_id}' not found for platform '{platform}'"
        )
    return match
