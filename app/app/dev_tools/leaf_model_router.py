"""
Dev-time model routing for Unlazy orchestrated leaves (UNLAZY_AND_PROOF_OF_WORK.md §1.6).

Unlazy's own PLAN.md template keeps `Tier` intentionally abstract
(mechanical | judgment — see .agents/skills/unlazy/templates/PLAN.md) and
explicitly defers host-specific model mapping rather than baking it into
the vendored skill. This module is that mapping for Foundation: when a
leaf's own work makes an LLM call, route it through llm_router using the
tier below and log it with project='Foundation-dev' — separate from
client-runtime cost (project='foundation') in llm_usage/cost dashboards.

Not wired into any actual orchestrated dispatch in this build — no
Workflow-based leaf tree was run this session — but ready for the next
one: a leaf's own code should call resolve_leaf_tier(plan_tier) to get
the TaskTier, then pass agent_name=f"unlazy-leaf:{leaf_id}",
project="Foundation-dev" through the normal llm_call()/llm_call_json().
"""
from app.llm_router import TaskTier

# mechanical: boilerplate, migrations, tests, fixed-pattern work -> cheap tier.
# judgment: architecture, security-sensitive, or ambiguous leaves -> Opus 4.8.
# Whole-system synthesis (driver/branch/final-audit duties) stays a judgment
# responsibility outside the leaf field per Unlazy's own template -- those
# route to ORCHESTRATOR_MAX only when the work is genuinely whole-system,
# not merely because a leaf is hard.
LEAF_TIER_MAP = {
    "mechanical": TaskTier.FAST,
    "judgment": TaskTier.COMPLEX,
}


def resolve_leaf_tier(plan_tier: str) -> TaskTier:
    """plan_tier: the PLAN.md leaf's `Tier` value ('mechanical' | 'judgment').
    Defaults to STANDARD for anything else rather than guessing cheap or
    expensive — an unrecognized tier value is a planning bug worth surfacing,
    not silently routing to the cheapest or priciest model."""
    if plan_tier not in LEAF_TIER_MAP:
        return TaskTier.STANDARD
    return LEAF_TIER_MAP[plan_tier]


DEV_PROJECT = "Foundation-dev"
