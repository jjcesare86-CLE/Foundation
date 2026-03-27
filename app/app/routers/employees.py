"""
Foundation API — Employees Router
Shared AI employee definitions, tier logic, handoff rules, and coverage engine.
Used by Automation Nation, VoiceMIO, and any other platform in the Foundation stack.
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional
import anthropic
import os

router = APIRouter(prefix="/employees", tags=["employees"])

# ─────────────────────────────────────────────
# EMPLOYEE DATA
# ─────────────────────────────────────────────

EMPLOYEES = [
    {
        "id": "maya", "name": "MAYA", "role": "Marketing Strategist",
        "department": "marketing", "department_label": "Marketing",
        "style": "Strategic & analytical",
        "helps": "Campaign strategy, ICP analysis, brand positioning, market research, competitive analysis, go-to-market planning",
        "outside_scope": "Writing copy or lead outreach — redirect to CLARA or KAI",
        "handoff_to": ["nina", "kai", "clara"],
        "covers_for": ["kai", "dean"],
        "covered_by": ["nina", "dean"],
        "color": "#7F77DD", "bg": "#EEEDFE",
    },
    {
        "id": "nina", "name": "NINA", "role": "Creative Strategist",
        "department": "marketing", "department_label": "Marketing",
        "style": "Creative & expressive",
        "helps": "Ad concepts, creative briefs, campaign hooks, visual direction, creative reviews, offer angles",
        "outside_scope": "Writing body copy or media buying — redirect to CLARA or KAI",
        "handoff_to": ["clara", "drew"],
        "covers_for": ["clara", "maya"],
        "covered_by": ["maya"],
        "color": "#7F77DD", "bg": "#EEEDFE",
    },
    {
        "id": "clara", "name": "CLARA", "role": "Copywriter",
        "department": "marketing", "department_label": "Marketing",
        "style": "Persuasive & precise",
        "helps": "Ad copy, email sequences, landing pages, social captions, VSL scripts, nurture content",
        "outside_scope": "Strategy or design direction — redirect to MAYA or NINA",
        "handoff_to": ["sage", "nina"],
        "covers_for": ["sage", "nina"],
        "covered_by": ["nina"],
        "color": "#7F77DD", "bg": "#EEEDFE",
    },
    {
        "id": "kai", "name": "KAI", "role": "Lead Gen Specialist",
        "department": "marketing", "department_label": "Marketing",
        "style": "Data-driven & systematic",
        "helps": "Lead lists, prospecting campaigns, outreach sequences, ICP targeting, Apollo & Clay workflows",
        "outside_scope": "Closing deals or onboarding — redirect to REX or OTTO",
        "handoff_to": ["rex", "maya"],
        "covers_for": ["maya"],
        "covered_by": ["maya", "rex"],
        "color": "#7F77DD", "bg": "#EEEDFE",
    },
    {
        "id": "rex", "name": "REX", "role": "Sales Coach",
        "department": "sales", "department_label": "Sales",
        "style": "Direct & motivating",
        "helps": "Sales scripts, objection handling, pipeline review, close strategies, call coaching, offer structuring",
        "outside_scope": "Onboarding or retention — redirect to OTTO or BLAKE",
        "handoff_to": ["blake", "otto"],
        "covers_for": ["blake", "kai"],
        "covered_by": ["blake"],
        "color": "#D85A30", "bg": "#FAECE7",
    },
    {
        "id": "blake", "name": "BLAKE", "role": "Retention Specialist",
        "department": "sales", "department_label": "Sales",
        "style": "Empathetic & conversational",
        "helps": "Client retention, churn prevention, upsell conversations, NPS, satisfaction campaigns",
        "outside_scope": "New sales or technical setup — redirect to REX or OTTO",
        "handoff_to": ["aria", "rex"],
        "covers_for": ["aria"],
        "covered_by": ["rex", "aria"],
        "color": "#D85A30", "bg": "#FAECE7",
    },
    {
        "id": "otto", "name": "OTTO", "role": "Onboarding Orchestrator",
        "department": "operations", "department_label": "Operations",
        "style": "Systematic & thorough",
        "helps": "New client setup, workflow deployment, task routing, project management, team coordination",
        "outside_scope": "Legal review or financial reporting — redirect to LEO or FIN",
        "handoff_to": ["ace", "vince", "leo", "ori"],
        "covers_for": ["ace", "ori"],
        "covered_by": ["ori", "ace"],
        "color": "#1D9E75", "bg": "#E1F5EE",
    },
    {
        "id": "ori", "name": "ORI", "role": "Operations Manager",
        "department": "operations", "department_label": "Operations",
        "style": "Process-oriented & structured",
        "helps": "SOPs, process documentation, efficiency analysis, capacity planning, team workflows",
        "outside_scope": "Client-facing delivery or tech builds — redirect to OTTO or ACE",
        "handoff_to": ["otto", "fin"],
        "covers_for": ["otto", "fin"],
        "covered_by": ["otto"],
        "color": "#1D9E75", "bg": "#E1F5EE",
    },
    {
        "id": "ace", "name": "ACE", "role": "Automation Architect",
        "department": "tech", "department_label": "Tech & Automation",
        "style": "Technical & precise",
        "helps": "Workflow design, n8n & Zapier builds, API integrations, automation strategy, system architecture",
        "outside_scope": "Voice agents or video — redirect to VINCE or DREW",
        "handoff_to": ["vince", "otto"],
        "covers_for": ["vince", "otto"],
        "covered_by": ["vince"],
        "color": "#378ADD", "bg": "#E6F1FB",
    },
    {
        "id": "vince", "name": "VINCE", "role": "Voice Agent Specialist",
        "department": "tech", "department_label": "Tech & Automation",
        "style": "Technical & methodical",
        "helps": "VAPI configuration, voice prompts, call flows, ElevenLabs voice selection, agent deployment",
        "outside_scope": "General automation or video — redirect to ACE or DREW",
        "handoff_to": ["ace", "otto"],
        "covers_for": ["ace"],
        "covered_by": ["ace"],
        "color": "#378ADD", "bg": "#E6F1FB",
    },
    {
        "id": "drew", "name": "DREW", "role": "Video Producer",
        "department": "media", "department_label": "Content & Media",
        "style": "Creative & visual",
        "helps": "Video strategy, script writing, production briefs, Blast Video workflows, YouTube & ad video",
        "outside_scope": "Static copy or lead gen — redirect to CLARA or KAI",
        "handoff_to": ["sage", "clara"],
        "covers_for": ["sage"],
        "covered_by": ["sage", "nina"],
        "color": "#BA7517", "bg": "#FAEEDA",
    },
    {
        "id": "sage", "name": "SAGE", "role": "Social Media Manager",
        "department": "media", "department_label": "Content & Media",
        "style": "Trendy & brand-aware",
        "helps": "Content calendars, posting schedules, platform strategy, engagement, community management",
        "outside_scope": "Paid ads or video production — redirect to KAI or DREW",
        "handoff_to": ["clara", "drew"],
        "covers_for": ["clara"],
        "covered_by": ["drew", "clara"],
        "color": "#BA7517", "bg": "#FAEEDA",
    },
    {
        "id": "leo", "name": "LEO", "role": "Legal Specialist",
        "department": "legal", "department_label": "Legal & Finance",
        "style": "Direct & matter-of-fact",
        "helps": "Contracts, compliance, terms of service, privacy policy, legal review, risk assessment",
        "outside_scope": "Financial reporting or operations — redirect to FIN or ORI",
        "handoff_to": ["fin", "otto"],
        "covers_for": ["fin"],
        "covered_by": [],
        "color": "#5F5E5A", "bg": "#F1EFE8",
    },
    {
        "id": "fin", "name": "FIN", "role": "Finance Analyst",
        "department": "legal", "department_label": "Legal & Finance",
        "style": "Precise & data-focused",
        "helps": "Revenue reporting, invoicing, expense tracking, Stripe analytics, financial projections",
        "outside_scope": "Legal contracts or tech builds — redirect to LEO or ACE",
        "handoff_to": ["leo", "ori"],
        "covers_for": ["ori"],
        "covered_by": ["leo", "ori"],
        "color": "#5F5E5A", "bg": "#F1EFE8",
    },
    {
        "id": "aria", "name": "ARIA", "role": "Client Success Manager",
        "department": "success", "department_label": "Client Success",
        "style": "Warm & solution-focused",
        "helps": "Support tickets, client satisfaction, issue escalation, onboarding support, proactive check-ins",
        "outside_scope": "New sales or technical builds — redirect to REX or ACE",
        "handoff_to": ["blake", "rex"],
        "covers_for": ["blake"],
        "covered_by": ["blake"],
        "color": "#639922", "bg": "#EAF3DE",
    },
    {
        "id": "dean", "name": "DEAN", "role": "Data Analyst",
        "department": "success", "department_label": "Client Success",
        "style": "Analytical & insights-driven",
        "helps": "Performance reporting, KPI dashboards, A/B test analysis, channel attribution, data insights",
        "outside_scope": "Content creation or sales — redirect to CLARA or REX",
        "handoff_to": ["fin", "maya"],
        "covers_for": ["fin", "maya"],
        "covered_by": ["fin"],
        "color": "#639922", "bg": "#EAF3DE",
    },
]

TIER_PACKS = {
    "starter":     ["otto", "rex", "maya"],
    "essentials":  ["otto", "rex", "maya", "ace", "aria", "clara"],
    "professional":["otto", "rex", "maya", "ace", "vince", "aria", "clara", "kai", "blake", "ori"],
    "enterprise":  [e["id"] for e in EMPLOYEES],
}

DEPARTMENTS = ["marketing", "sales", "operations", "tech", "media", "legal", "success"]

# ─────────────────────────────────────────────
# MODELS
# ─────────────────────────────────────────────

class CoverageRequest(BaseModel):
    employee_ids: list[str]

class CustomEmployeeRequest(BaseModel):
    name: str
    role: str
    department: str
    style: Optional[str] = "Professional & direct"
    helps: str
    outside_scope: Optional[str] = ""
    business_context: Optional[str] = ""

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def compute_coverage(selected_ids: list[str]) -> dict:
    """
    Given a list of active employee IDs, returns per-department coverage status
    and a list of gap messages for the client-facing fallback responses.
    """
    sel = set(selected_ids)
    result = {}
    gaps = []
    limited = []

    for dept in DEPARTMENTS:
        specs = [e for e in EMPLOYEES if e["department"] == dept]
        present = [e for e in specs if e["id"] in sel]
        missing = [e for e in specs if e["id"] not in sel]

        if len(present) == len(specs):
            result[dept] = {"status": "full", "label": "Full coverage", "active": [e["id"] for e in present]}
        elif present:
            result[dept] = {
                "status": "partial",
                "label": f"{len(present)}/{len(specs)} active",
                "active": [e["id"] for e in present],
                "missing": [e["id"] for e in missing],
            }
            limited.append(specs[0]["department_label"])
        else:
            # Check if any missing specialist is covered_by someone active
            cross_covered = any(
                cov_id in sel
                for e in specs
                for cov_id in e.get("covered_by", [])
            )
            if cross_covered:
                result[dept] = {
                    "status": "cross_covered",
                    "label": "Cross-covered (reduced depth)",
                    "active": [],
                    "missing": [e["id"] for e in specs],
                }
                limited.append(specs[0]["department_label"] + " (limited)")
            else:
                result[dept] = {
                    "status": "gap",
                    "label": "No coverage",
                    "active": [],
                    "missing": [e["id"] for e in specs],
                }
                gaps.append(specs[0]["department_label"])

    gap_message = None
    if gaps:
        gap_message = (
            f"Uncovered departments: {', '.join(gaps)}. "
            f"For requests in these areas, employees will respond: "
            f"\"This falls outside your current team. To handle this, "
            f"consider adding the relevant specialist. I can provide a "
            f"basic response or queue this for review.\""
        )

    return {
        "departments": result,
        "gaps": gaps,
        "limited": limited,
        "gap_message": gap_message,
    }

# ─────────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────────

@router.get("/")
def list_employees(department: Optional[str] = Query(None)):
    """Return all employees, optionally filtered by department."""
    if department:
        return [e for e in EMPLOYEES if e["department"] == department]
    return EMPLOYEES


@router.get("/tiers")
def list_tiers():
    """Return all predefined tier packs with their employee sets."""
    result = {}
    for tier, ids in TIER_PACKS.items():
        emps = [e for e in EMPLOYEES if e["id"] in ids]
        result[tier] = {
            "count": len(ids),
            "employee_ids": ids,
            "employees": [{"id": e["id"], "name": e["name"], "role": e["role"]} for e in emps],
        }
    return result


@router.get("/{employee_id}")
def get_employee(employee_id: str):
    """Return a single employee's full profile."""
    emp = next((e for e in EMPLOYEES if e["id"] == employee_id), None)
    if not emp:
        raise HTTPException(status_code=404, detail=f"Employee '{employee_id}' not found")
    # Hydrate handoff_to with full profiles
    emp_out = dict(emp)
    emp_out["handoff_to_details"] = [
        {"id": e["id"], "name": e["name"], "role": e["role"]}
        for e in EMPLOYEES if e["id"] in emp["handoff_to"]
    ]
    return emp_out


@router.post("/coverage")
def check_coverage(req: CoverageRequest):
    """
    Given a list of active employee IDs, return coverage analysis per department
    including gap messages for fallback responses.
    """
    unknown = [i for i in req.employee_ids if not any(e["id"] == i for e in EMPLOYEES)]
    if unknown:
        raise HTTPException(status_code=400, detail=f"Unknown employee IDs: {unknown}")
    return compute_coverage(req.employee_ids)


@router.get("/tiers/{tier_name}/coverage")
def tier_coverage(tier_name: str):
    """Return coverage analysis for a named tier pack."""
    if tier_name not in TIER_PACKS:
        raise HTTPException(status_code=404, detail=f"Tier '{tier_name}' not found. Valid: {list(TIER_PACKS.keys())}")
    return {
        "tier": tier_name,
        "employees": TIER_PACKS[tier_name],
        "coverage": compute_coverage(TIER_PACKS[tier_name]),
    }


@router.post("/generate-prompt")
async def generate_employee_prompt(req: CustomEmployeeRequest):
    """
    Generate a deployable system prompt for a custom AI employee using Claude.
    """
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

    user_message = f"""Generate a complete, deployable AI employee system prompt for a business automation agency.

Employee:
- Name: {req.name.upper()}
- Role: {req.role}
- Department: {req.department}
- Communication style: {req.style}
- Expertise: {req.helps}
- Scope limits / redirects: {req.outside_scope or 'None specified'}
{f'- Business context: {req.business_context}' if req.business_context else ''}

The prompt must include:
1. Identity: who {req.name.upper()} is, their role, and their communication style
2. Expertise areas with specific capabilities
3. Hard scope rules — what {req.name.upper()} does NOT handle, and exact redirect language to use
4. Information-gathering protocol — {req.name.upper()} must ask clarifying questions if the brief is vague. They refuse to produce output until they have sufficient information to meet the required standard.
5. Quality standard — never deliver generic, low-effort output. Always confirm deliverables meet the standard before responding.
6. A brief opening greeting {req.name.upper()} uses when a new conversation starts.

Format with clearly labeled sections. Make it direct and immediately deployable."""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        messages=[{"role": "user", "content": user_message}],
    )

    return {
        "name": req.name.upper(),
        "role": req.role,
        "system_prompt": message.content[0].text,
    }
