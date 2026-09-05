"""
Full-roster operational readiness audit — L1 Roster, L2 Prompt, L3 Access,
L4 Delivery, L5 Proof. An agent is GREEN only if all five pass.
"""
import logging
import re
from datetime import datetime, timezone
from typing import Optional

from app.database import supabase
from app.llm_router import llm_call, TaskTier, MODEL_MAP

logger = logging.getLogger(__name__)

VALID_MODEL_TIERS = {"orchestrator_max", "complex", "standard", "fast", "orchestrator"}
HOUSE_FIELDS = ["role", "department", "department_label", "handoff_to", "color", "bg"]

TIER_TO_TASKTIER = {
    "orchestrator_max": TaskTier.ORCHESTRATOR_MAX,
    "orchestrator": TaskTier.COMPLEX,
    "complex": TaskTier.COMPLEX,
    "standard": TaskTier.STANDARD,
    "fast": TaskTier.FAST,
}

# Capability -> a callable that returns (ok: bool, detail: str).
def _check_ghl() -> tuple[bool, str]:
    import os
    return (bool(os.getenv("GHL_API_KEY")), "GHL_API_KEY " + ("set" if os.getenv("GHL_API_KEY") else "not set"))


def _check_maps() -> tuple[bool, str]:
    import os
    return (bool(os.getenv("GOOGLE_MAPS_API_KEY")), "GOOGLE_MAPS_API_KEY " + ("set" if os.getenv("GOOGLE_MAPS_API_KEY") else "not set"))


def _check_stripe() -> tuple[bool, str]:
    result = (
        supabase.schema("foundation").table("client_connections")
        .select("id", count="exact").eq("provider", "stripe").eq("status", "active").execute()
    )
    ok = bool(result.count)
    return (ok, f"{result.count or 0} active stripe client_connections rows")


def _check_gps_feed() -> tuple[bool, str]:
    return (False, "no GPS clock-in feed integration exists yet (no config surface to check)")


CAPABILITY_CHECKS = {
    "ghl": _check_ghl,
    "ghl_social": _check_ghl,
    "maps": _check_maps,
    "stripe": _check_stripe,
    "stripe_read": _check_stripe,
    "gps_feed": _check_gps_feed,
}

_TEMPLATE_VAR_RE = re.compile(r"\{([a-zA-Z_][a-zA-Z0-9_]*)\}")


def audit_l1(agent: dict) -> dict:
    if not agent.get("is_active"):
        return {"pass": False, "reason": "row not active"}
    if agent.get("model_tier") not in VALID_MODEL_TIERS:
        return {"pass": False, "reason": f"invalid model_tier={agent.get('model_tier')!r}"}
    # handoff_to is legitimately [] for terminal agents (Eden, by the hard
    # eden_sessions privacy-isolation rule: no handoffs, never gated). Only
    # a genuine NULL is a gap; an empty array is a valid org-chart leaf.
    missing = [
        f for f in HOUSE_FIELDS
        if agent.get(f) is None or (agent.get(f) == "" and f not in ("handoff_to",))
    ]
    if missing:
        return {"pass": False, "reason": f"missing house fields: {missing}"}
    return {"pass": True, "reason": ""}


def audit_l2(agent: dict) -> dict:
    prompt = agent.get("system_prompt")
    if not prompt:
        return {"pass": False, "reason": "system_prompt never written"}
    # Sanity check: every {var} looks like a real identifier (not malformed
    # like "{{" or an empty "{}"). Can't confirm true resolvability without
    # a render context, but this catches the obvious break.
    if "{}" in prompt or "{{" in prompt:
        return {"pass": False, "reason": "malformed template braces in system_prompt"}
    return {"pass": True, "reason": f"{len(_TEMPLATE_VAR_RE.findall(prompt))} template var(s), all well-formed"}


def audit_l3(agent: dict) -> dict:
    required = agent.get("required_capabilities") or []
    if not required:
        return {"pass": True, "reason": "no capabilities required"}
    failures = []
    for cap in required:
        checker = CAPABILITY_CHECKS.get(cap)
        if checker is None:
            failures.append(f"{cap}: no checker registered")
            continue
        ok, detail = checker()
        if not ok:
            failures.append(f"{cap}: {detail}")
    if failures:
        return {"pass": False, "reason": "; ".join(failures)}
    return {"pass": True, "reason": f"all {len(required)} capability(s) live"}


def audit_l4(agent: dict) -> dict:
    jobs = supabase.schema("foundation").table("agent_jobs").select("*").eq("agent_slug", agent["id"]).execute().data
    if not jobs:
        return {"pass": True, "reason": "no scheduled jobs for this agent"}
    stale = []
    for job in jobs:
        if not job.get("last_run_at"):
            stale.append(f"{job['job_name']}: never run")
            continue
        last_run = datetime.fromisoformat(job["last_run_at"].replace("Z", "+00:00"))
        age_minutes = (datetime.now(timezone.utc) - last_run).total_seconds() / 60
        if age_minutes > job["schedule_interval_minutes"] * 2:
            stale.append(f"{job['job_name']}: last heartbeat {int(age_minutes)}min ago (limit {job['schedule_interval_minutes']*2}min)")
        elif job.get("last_status") == "failed":
            stale.append(f"{job['job_name']}: last run failed ({job.get('last_detail')})")
    if stale:
        return {"pass": False, "reason": "; ".join(stale)}
    return {"pass": True, "reason": f"{len(jobs)} job(s) heartbeating on schedule"}


def audit_receipts(agent_id: str) -> dict:
    """Proof-of-Work integration (UNLAZY_AND_PROOF_OF_WORK.md §2.6): the
    agent's last 10 completed actions (executed or simulated) must have
    non-null evidence AND verification_status='verified'. A simulated
    action can never satisfy this by design (verify_method='none',
    verification_status='pending') -- an agent whose recent completions
    are mostly simulated is correctly unverified, not falsely green."""
    rows = (
        supabase.schema("foundation").table("agent_actions")
        .select("id,status,evidence,verification_status")
        .eq("agent_id", agent_id)
        .in_("status", ["executed", "simulated"])
        .order("executed_at", desc=True)
        .limit(10)
        .execute().data
    )
    if not rows:
        return {"pass": True, "reason": "no completed actions yet to check"}
    unverified = [r["id"] for r in rows if r.get("verification_status") != "verified" or not r.get("evidence")]
    if unverified:
        return {"pass": False, "reason": f"{len(unverified)} of {len(rows)} recent completions not verified: {unverified[:3]}"}
    return {"pass": True, "reason": f"all {len(rows)} recent completions verified"}


def audit_l5(agent: dict) -> dict:
    tier = TIER_TO_TASKTIER.get(agent.get("model_tier"))
    if tier is None:
        smoke_pass, smoke_reason = False, f"can't map model_tier={agent.get('model_tier')!r} to a TaskTier"
    else:
        expected_model = MODEL_MAP[tier]
        try:
            llm_call(
                messages=[{"role": "user", "content": "Introduce yourself in one sentence and name your department."}],
                tier=tier,
                system=f"You are {agent.get('biblical_name', agent['id'])}, {agent.get('role', '')} in the {agent.get('department_label', '')} department.",
                max_tokens=100,
                project="foundation",
                agent_name=agent["id"],
                task_type="ops_audit:smoke",
            )
            smoke_pass, smoke_reason = True, f"smoke call succeeded, expected model {expected_model}"
        except Exception as e:
            smoke_pass, smoke_reason = False, f"smoke call failed: {e}"

    receipts = audit_receipts(agent["id"])
    return {
        "pass": smoke_pass and receipts["pass"],
        "reason": f"smoke: {smoke_reason} | receipts: {receipts['reason']}",
        "smoke_pass": smoke_pass,
        "receipts_pass": receipts["pass"],
    }


def audit_agent(agent: dict, run_l5: bool = True) -> dict:
    l1, l2, l3, l4 = audit_l1(agent), audit_l2(agent), audit_l3(agent), audit_l4(agent)
    l5 = audit_l5(agent) if run_l5 else {"pass": None, "reason": "skipped", "smoke_pass": None, "receipts_pass": None}
    layers = {"L1": l1, "L2": l2, "L3": l3, "L4": l4, "L5": l5}

    base_pass = all(layers[k]["pass"] for k in ("L1", "L2", "L3", "L4"))
    smoke_pass = l5.get("smoke_pass")
    receipts_pass = l5.get("receipts_pass")

    if not base_pass or smoke_pass is False:
        # L1-4 failure or a genuinely unreachable agent -- red, same as before.
        status = "red"
    elif smoke_pass is None:
        # L5 skipped entirely (e.g. no ANTHROPIC_API_KEY available) -- amber, same as before.
        status = "amber"
    elif receipts_pass is False:
        # Reachable and responding normally, but recent completions aren't
        # verified -- amber per §2.6: "a chatty agent that silently fails
        # its side effects is worse than a dead one."
        status = "amber"
    else:
        status = "green"

    return {"agent_id": agent["id"], "biblical_name": agent.get("biblical_name"), "status": status, "layers": layers}


def run_full_audit(run_l5: bool = True) -> list[dict]:
    agents = supabase.schema("foundation").table("ai_employees").select("*").eq("is_active", True).execute().data
    return [audit_agent(a, run_l5=run_l5) for a in agents]
