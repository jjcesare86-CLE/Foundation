"""
Pydantic schemas for the Foundation Pricing API.
All request/response shapes that flow in and out of /pricing/* endpoints.
"""
from __future__ import annotations

from enum import Enum
from typing import Optional, Literal
from pydantic import BaseModel, Field, ConfigDict


# ============================================================================
# Enums
# ============================================================================
class Product(str, Enum):
    AN = "AN"
    VMIO = "VMIO"
    AMIO = "AMIO"
    BLAST = "BLAST"
    MRLIN = "MRLIN"


class QuoteSource(str, Enum):
    CUSTOMER_CALC = "customer_calc"
    INTERNAL_QUOTE = "internal_quote"
    BUNDLE_CALC = "bundle_calc"
    VOICE_AGENT = "voice_agent"
    API = "api"


class QuoteStatus(str, Enum):
    DRAFT = "draft"
    SENT = "sent"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    EXPIRED = "expired"


class NegotiationTier(str, Enum):
    TIER_1_QUOTE = "tier_1_quote"
    TIER_2_SOFT = "tier_2_soft"
    TIER_3_HARD = "tier_3_hard"
    TIER_4_ESCALATE = "tier_4_escalate"


# ============================================================================
# Request schemas
# ============================================================================
class QuoteRequest(BaseModel):
    """Inputs for a fair-price quote calculation."""
    model_config = ConfigDict(use_enum_values=True)

    product: Product
    market: float = Field(ge=1.0, le=2.4, description="Market size multiplier")
    structure: float = Field(ge=1.0, le=3.2, description="Business structure multiplier")
    revenue: float = Field(ge=1.0, le=3.0, description="Revenue tier multiplier")
    vertical: float = Field(ge=1.0, le=1.6, description="Industry vertical multiplier")
    locations: int = Field(ge=1, le=500, default=1)

    # AN/VMIO/AMIO use volume + agents + integrations
    volume: int = Field(ge=1, le=50000, default=2000)
    agents: int = Field(ge=1, le=16, default=3)
    integrations: int = Field(ge=0, le=12, default=2)

    # BLAST uses videos + complexity
    videos: Optional[int] = Field(default=None, ge=1, le=10000)
    complexity: Optional[float] = Field(default=None, ge=1.0, le=2.5)

    # MRLIN uses sources + users + queries
    sources: Optional[int] = Field(default=None, ge=1, le=6)
    users: Optional[int] = Field(default=None, ge=1, le=500)
    queries_k: Optional[int] = Field(default=None, ge=1, le=500)

    # Optional context
    contact_id: Optional[str] = None
    company_name: Optional[str] = None


class QuoteLogRequest(BaseModel):
    """Persist a calculated quote to pricing_quotes."""
    model_config = ConfigDict(use_enum_values=True)

    contact_id: Optional[str] = None
    product: str
    inputs: dict
    multipliers: dict = Field(default_factory=dict)
    base_fee: float
    monthly_price: float
    setup_fee: float
    estimated_roi: float = 0
    roi_multiple: float = 0
    tier: str = ""
    source: QuoteSource = QuoteSource.API
    status: QuoteStatus = QuoteStatus.DRAFT
    negotiation_notes: Optional[str] = None
    override_multipliers: Optional[dict] = None


class VoiceQuoteRequest(QuoteRequest):
    """Voice-agent quote — adds persona and call context."""
    persona: Literal["chris", "mia", "celeste", "atlas", "oracle"]
    call_sid: Optional[str] = None
    quote_id: Optional[str] = None


class VoiceIncentiveRequest(BaseModel):
    """Tier 2 soft incentive (no monetary discount)."""
    quote_id: str
    persona: Literal["chris", "mia", "celeste", "atlas", "oracle"]
    incentive_key: Literal[
        "first_month_free",
        "bonus_voice_agent_90d",
        "extended_trial_14d",
        "priority_onboarding",
        "annual_commit_setup_waive",
    ]
    call_sid: Optional[str] = None


class VoiceDiscountRequest(BaseModel):
    """Tier 3 monetary discount with hard limits."""
    quote_id: str
    persona: Literal["chris", "mia", "celeste", "atlas", "oracle"]
    requested_monthly_pct: float = Field(ge=0.0, le=0.20)
    requested_setup_waive: bool = False
    call_sid: Optional[str] = None


class VoiceEscalateRequest(BaseModel):
    """Tier 4 — hand off to human."""
    quote_id: str
    persona: Literal["chris", "mia", "celeste", "atlas", "oracle"]
    reason: Literal[
        "discount_exceeds_authority",
        "custom_terms_requested",
        "enterprise_complexity",
        "strategic_partnership",
        "prospect_requested_owner",
    ]
    context: str
    call_sid: Optional[str] = None


# ============================================================================
# Response schemas
# ============================================================================
class QuoteBreakdown(BaseModel):
    """Per-multiplier breakdown for transparency."""
    label: str
    multiplier: float
    contribution: Optional[str] = None


class QuoteResponse(BaseModel):
    """Result of a /pricing/quote call."""
    quote_id: str
    product: str
    monthly_price: float
    setup_fee: float
    base_fee: float
    estimated_roi: float
    roi_multiple: float
    tier: str
    capped: bool = False
    breakdown: list[QuoteBreakdown] = Field(default_factory=list)
    speak_script: Optional[str] = None  # populated for voice-agent calls


class VoiceIncentiveResponse(BaseModel):
    quote_id: str
    concession_label: str
    new_monthly: float
    new_setup: float
    speak_script: str
    tier_reached: NegotiationTier


class VoiceDiscountResponse(BaseModel):
    quote_id: str
    escalated: bool
    concession_label: Optional[str] = None
    new_monthly: Optional[float] = None
    new_setup: Optional[float] = None
    speak_script: str
    tier_reached: NegotiationTier


class VoiceEscalateResponse(BaseModel):
    quote_id: str
    escalated: bool = True
    speak_script: str
    notification_sent: bool = False


class QuoteLogResponse(BaseModel):
    quote_id: str
    written: bool
    table: str = "pricing_quotes"
