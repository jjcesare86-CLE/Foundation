"""
Voice Agent Pricing & Negotiation
==================================

Powers Chris (AN), Mia (VoiceMIO), Celeste (AssistMIO), Atlas (Blast Video),
and Oracle (MRLIN). Provides:

1. Fair-price quoting via VAPI function calls
2. Four-tier negotiation framework with hard authority limits
3. Per-persona speak scripts tuned for voice delivery
4. Always-log policy: every quote and concession persists to Supabase

Authority (per directive 2026-04-22):
- Tier 2 (soft incentives): unlimited
- Tier 3 (hard discount): up to 20% off monthly + full setup waiver
- Tier 4 (escalate): anything beyond Tier 3
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional

from .schemas import NegotiationTier
from .pricing_engine import calculate_quote


# ============================================================================
# Personas
# ============================================================================
PERSONA_PRODUCT = {
    "chris": "AN",
    "mia": "VMIO",
    "celeste": "AMIO",
    "atlas": "BLAST",
    "oracle": "MRLIN",
}


# ============================================================================
# Authority limits
# ============================================================================
@dataclass(frozen=True)
class NegotiationAuthority:
    max_monthly_discount_pct: float = 0.20
    max_setup_discount_full_waiver: bool = True
    escalate_if_request_exceeds_pct: float = 0.20
    escalate_if_request_waives_and_max_discount: bool = False  # Per directive: allow combined
    escalate_if_multi_year_terms_requested: bool = True


DEFAULT_AUTHORITY = NegotiationAuthority()


# ============================================================================
# Tier 2 incentive catalog
# ============================================================================
@dataclass
class Concession:
    tier: NegotiationTier
    label: str
    monthly_discount_pct: float = 0.0
    setup_discount_pct: float = 0.0
    incentive_type: Optional[str] = None
    rationale: str = ""
    granted_at: datetime = field(default_factory=datetime.utcnow)


TIER_2_CATALOG = {
    "first_month_free": Concession(
        tier=NegotiationTier.TIER_2_SOFT,
        label="First month free",
        incentive_type="first_month_free",
        rationale="MRR intact, just deferred — closes deals without long-term value erosion",
    ),
    "bonus_voice_agent_90d": Concession(
        tier=NegotiationTier.TIER_2_SOFT,
        label="Free bonus voice agent for 90 days",
        incentive_type="bonus_voice_agent_90d",
        rationale="High perceived value, builds upsell path",
    ),
    "extended_trial_14d": Concession(
        tier=NegotiationTier.TIER_2_SOFT,
        label="Extended 14-day full-access trial",
        incentive_type="extended_trial_14d",
        rationale="De-risks commitment, maintains price integrity",
    ),
    "priority_onboarding": Concession(
        tier=NegotiationTier.TIER_2_SOFT,
        label="White-glove priority onboarding (first 30 days)",
        incentive_type="priority_onboarding",
        rationale="Signals investment without price concession",
    ),
    "annual_commit_setup_waive": Concession(
        tier=NegotiationTier.TIER_2_SOFT,
        label="Setup waived with annual prepay",
        incentive_type="annual_commit_setup_waive",
        setup_discount_pct=1.0,
        rationale="Net cash positive — full year upfront covers setup",
    ),
}


# ============================================================================
# Tier 3 evaluation
# ============================================================================
def evaluate_discount_request(
    requested_monthly_pct: float,
    requested_setup_waive: bool,
    authority: NegotiationAuthority = DEFAULT_AUTHORITY,
) -> tuple[Optional[Concession], bool]:
    """
    Returns (concession_or_None, needs_escalation).
    """
    if requested_monthly_pct > authority.max_monthly_discount_pct:
        return None, True

    monthly_pct = min(requested_monthly_pct, authority.max_monthly_discount_pct)
    setup_pct = 1.0 if requested_setup_waive else 0.0

    label_parts = []
    if monthly_pct > 0:
        label_parts.append(f"{int(monthly_pct*100)}% off monthly")
    if requested_setup_waive:
        label_parts.append("setup waived")
    label = " + ".join(label_parts) if label_parts else "No concession"

    return (
        Concession(
            tier=NegotiationTier.TIER_3_HARD,
            label=label,
            monthly_discount_pct=monthly_pct,
            setup_discount_pct=setup_pct,
            rationale="Tier 3 closing concession",
        ),
        False,
    )


# ============================================================================
# Speak script generation
# ============================================================================
def quote_script(persona: str, monthly: float, setup: float, tier: str, roi_x: float) -> str:
    m = int(monthly)
    s = int(setup)

    if persona == "chris":
        return (
            f"Based on what you've shared, Automation Nation will run you "
            f"{m} dollars a month with a setup of {s}. That puts you in our "
            f"{tier} tier. At your volume we project that drives about {roi_x} times ROI."
        )
    if persona == "mia":
        return (
            f"Okay — for Voice-Me-Oh, I'm seeing {m} a month, plus a one-time "
            f"{s} to get your voice agents set up. You'd be in our {tier} tier."
        )
    if persona == "celeste":
        return (
            f"For AssistMIO, your fair monthly is {m}, with a {s} setup. "
            f"That's the {tier} tier. We expect about {roi_x}x return on that investment."
        )
    if persona == "atlas":
        return (
            f"Blast Video comes in at {m} a month — and your setup is just {s}. "
            f"You're in our {tier} tier. Unlimited video production at that rate."
        )
    if persona == "oracle":
        return (
            f"MRLIN pricing for your profile: {m} monthly, {s} to configure your "
            f"data connections. {tier} tier."
        )
    return f"{m} dollars a month, {s} setup."


def soft_incentive_script(persona: str, concession: Concession) -> str:
    t = concession.incentive_type
    if t == "first_month_free":
        return (
            "Here's what I can do — let me give you the first month free. "
            "No payment until month two, full access from day one."
        )
    if t == "bonus_voice_agent_90d":
        return (
            "I can include a bonus voice agent at no charge for your first 90 days. "
            "That's an extra agent running alongside your main deployment."
        )
    if t == "extended_trial_14d":
        return (
            "Let me extend your trial to 14 days with full access. "
            "No credit card until day 15. If it's not delivering, you walk."
        )
    if t == "priority_onboarding":
        return (
            "I'll put you in priority onboarding. Dedicated setup support for "
            "your first 30 days — direct line whenever you need help."
        )
    if t == "annual_commit_setup_waive":
        return (
            "If you commit to twelve months, I waive the setup fee entirely. "
            "Save that money upfront and lock in today's pricing for a full year."
        )
    return concession.label


def discount_script(persona: str, concession: Concession, new_monthly: float, setup_savings: float) -> str:
    pct = int(concession.monthly_discount_pct * 100)
    waive = concession.setup_discount_pct >= 1.0
    nm = int(new_monthly)

    if pct > 0 and waive:
        return (
            f"Alright, here's what I can do: I'll take {pct} percent off your "
            f"monthly — bringing it to {nm} dollars — and waive the setup fee "
            f"entirely. That saves you {int(setup_savings)} today. Best I'm "
            f"authorized to do on the spot."
        )
    if pct > 0:
        return (
            f"Alright — I can take {pct} percent off your monthly, bringing it "
            f"to {nm} per month. That's my best offer today."
        )
    if waive:
        return (
            f"I'll waive the setup fee entirely — saves you {int(setup_savings)} "
            f"today. Can we get you started this week?"
        )
    return concession.label


def escalation_script(persona: str) -> str:
    if persona == "chris":
        return (
            "I want to get this right for you. What you're asking is beyond what "
            "I can authorize on my own — but I'm going to have John reach out "
            "personally within 24 hours. He has the authority to put together "
            "something custom. Is that okay?"
        )
    return (
        "That's a bigger conversation than I can close today. Let me connect "
        "you with John directly — he can work on custom terms. You'll hear "
        "from him within 24 hours. Sound good?"
    )
