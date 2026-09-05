"""
Foundation Pricing Engine
==========================

Pure-function pricing math for all products. No I/O, no DB, no HTTP — those
live in routes.py. This module is fully unit-testable in isolation.

Formulas live here. To retune multipliers without code changes, edit the
pricing_config table in Supabase (this module reads from cache or DB if
configured, with fallback constants).

Version: v5 (2026-04-29)
"""
from __future__ import annotations

import math
import uuid
from dataclasses import dataclass
from typing import Optional

from .schemas import QuoteRequest, QuoteResponse, QuoteBreakdown


# ============================================================================
# Product constants (v5 — Apr 22 2026)
# ============================================================================
BASE_FEES = {
    "AN":    {"monthly": 299, "setup": 1999, "floor": 299, "ceiling": 500_000},
    "VMIO":  {"monthly": 299, "setup": 999,  "floor": 299, "ceiling": 500_000},
    "AMIO":  {"monthly": 299, "setup": 1999, "floor": 299, "ceiling": 500_000},
    "BLAST": {"monthly": 249, "setup": 99,   "floor": 99,  "ceiling": 10_000},
    "MRLIN": {"monthly": 99,  "setup": 99,   "floor": 99,  "ceiling": 500_000},
}

VALUE_PER_UNIT = {
    "AN":    27,   # per interaction
    "VMIO":  13,   # per interaction
    "AMIO":  27,   # per interaction
    "BLAST": 10,   # per video (with vertical applied to ROI)
    "MRLIN": 9,    # per query
}

DEFAULT_CONVERSION_RATE = 0.22  # for ROI calculation
ROI_WARNING_THRESHOLD = 1.5

# Bundle discount tiers
BUNDLE_DISCOUNTS = {1: 0.00, 2: 0.10, 3: 0.18, 4: 0.25, 5: 0.32}


# ============================================================================
# Tier label assignment
# ============================================================================
def _tier_label(product: str, monthly: float) -> str:
    """Auto-assign tier based on price."""
    if product == "BLAST":
        if monthly >= 9999: return "Enterprise Unlimited"
        if monthly >= 2000: return "Scale"
        if monthly >= 500:  return "Growth"
        return "Starter"

    if monthly >= 100_000: return "National"
    if monthly >= 10_000:  return "Enterprise"
    if monthly >= 2_500:   return "Professional"
    if monthly >= 900:     return "Essentials"
    return "Starter"


# ============================================================================
# Setup fee scaling
# ============================================================================
def calculate_setup_fee(base_setup: float, structure: float, revenue: float) -> float:
    """Setup scales by structure × revenue, capped at 5×."""
    scale = min(5.0, structure * revenue * 0.5)
    scale = max(1.0, scale)  # never below base
    return round(base_setup * scale, 2)


# ============================================================================
# Per-product price calculations
# ============================================================================
def _price_an_vmio_amio(req: QuoteRequest) -> tuple[float, list[QuoteBreakdown]]:
    """AN, VoiceMIO, AssistMIO share the same compounding formula."""
    base = BASE_FEES[req.product]["monthly"]
    floor = BASE_FEES[req.product]["floor"]
    ceiling = BASE_FEES[req.product]["ceiling"]

    loc_mult = 1 + math.log2(max(1, req.locations)) * 0.6
    vol_mult = 1 + (req.volume / 2000) * 0.35
    agent_mult = 1 + (req.agents - 1) * 0.18
    int_mult = 1 + req.integrations * 0.07

    raw = (
        base
        * req.market
        * req.structure
        * req.revenue
        * req.vertical
        * loc_mult
        * vol_mult
        * agent_mult
        * int_mult
    )
    final = max(floor, min(ceiling, raw))

    breakdown = [
        QuoteBreakdown(label=f"Base ({req.product})", multiplier=base),
        QuoteBreakdown(label="Market size", multiplier=round(req.market, 2)),
        QuoteBreakdown(label="Business structure", multiplier=round(req.structure, 2)),
        QuoteBreakdown(label="Revenue tier", multiplier=round(req.revenue, 2)),
        QuoteBreakdown(label="Industry vertical", multiplier=round(req.vertical, 2)),
        QuoteBreakdown(label=f"Locations ({req.locations})", multiplier=round(loc_mult, 2)),
        QuoteBreakdown(label=f"Interaction volume ({req.volume:,}/mo)", multiplier=round(vol_mult, 2)),
        QuoteBreakdown(label=f"AI employees ({req.agents})", multiplier=round(agent_mult, 2)),
        QuoteBreakdown(label=f"Integrations ({req.integrations})", multiplier=round(int_mult, 2)),
    ]
    return final, breakdown


def _price_blast(req: QuoteRequest) -> tuple[float, bool, list[QuoteBreakdown]]:
    """Blast Video — capped at $10k, vertical applies to ROI not price."""
    base = BASE_FEES["BLAST"]["monthly"]
    floor = BASE_FEES["BLAST"]["floor"]
    ceiling = BASE_FEES["BLAST"]["ceiling"]

    videos = req.videos or req.volume
    complexity = req.complexity or 1.35

    video_mult = 1 + (videos / 40) * 0.28
    loc_mult = 1 + math.log2(max(1, req.locations)) * 0.35

    raw = (
        base
        * req.market
        * req.structure
        * req.revenue
        * video_mult
        * complexity
        * loc_mult
    )
    capped = raw > ceiling
    final = max(floor, min(ceiling, raw))

    breakdown = [
        QuoteBreakdown(label="Base (Blast Video)", multiplier=base),
        QuoteBreakdown(label="Market size", multiplier=round(req.market, 2)),
        QuoteBreakdown(label="Business structure", multiplier=round(req.structure, 2)),
        QuoteBreakdown(label="Revenue tier", multiplier=round(req.revenue, 2)),
        QuoteBreakdown(label=f"Videos ({videos:,}/mo)", multiplier=round(video_mult, 2)),
        QuoteBreakdown(label="Complexity", multiplier=round(complexity, 2)),
        QuoteBreakdown(label=f"Locations ({req.locations})", multiplier=round(loc_mult, 2)),
        QuoteBreakdown(label="Vertical (applies to ROI side)", multiplier=round(req.vertical, 2)),
    ]
    if capped:
        breakdown.append(QuoteBreakdown(label="Enterprise cap applied", multiplier=10000))

    return final, capped, breakdown


def _price_mrlin(req: QuoteRequest) -> tuple[float, list[QuoteBreakdown]]:
    """MRLIN — data-depth formula."""
    base = BASE_FEES["MRLIN"]["monthly"]
    floor = BASE_FEES["MRLIN"]["floor"]
    ceiling = BASE_FEES["MRLIN"]["ceiling"]

    sources = req.sources or 1
    users = req.users or 1
    queries_k = req.queries_k or 1

    source_mult = 1 + (sources - 1) * 0.25
    user_mult = 1 + math.log2(max(1, users)) * 0.35
    query_mult = 1 + (queries_k / 5) * 0.30

    raw = (
        base
        * req.market
        * req.structure
        * req.revenue
        * req.vertical
        * source_mult
        * user_mult
        * query_mult
    )
    final = max(floor, min(ceiling, raw))

    breakdown = [
        QuoteBreakdown(label="Base (MRLIN)", multiplier=base),
        QuoteBreakdown(label="Market size", multiplier=round(req.market, 2)),
        QuoteBreakdown(label="Business structure", multiplier=round(req.structure, 2)),
        QuoteBreakdown(label="Revenue tier", multiplier=round(req.revenue, 2)),
        QuoteBreakdown(label="Industry vertical", multiplier=round(req.vertical, 2)),
        QuoteBreakdown(label=f"Data sources ({sources})", multiplier=round(source_mult, 2)),
        QuoteBreakdown(label=f"Active users ({users})", multiplier=round(user_mult, 2)),
        QuoteBreakdown(label=f"Query volume ({queries_k}k/mo)", multiplier=round(query_mult, 2)),
    ]
    return final, breakdown


# ============================================================================
# ROI calculation
# ============================================================================
def _calculate_roi(req: QuoteRequest, monthly_price: float) -> tuple[float, float]:
    """
    Returns (estimated_roi, roi_multiple).

    Different products have different ROI formulas:
    - AN/VMIO/AMIO: volume × value_per_unit × conversion_rate
    - BLAST: videos × $10 × complexity × vertical (vertical on ROI side)
    - MRLIN: queries × $9 × conversion_rate (volume model — strategic model
      lives in voice_pricing.py for enterprise discovery calls)
    """
    if req.product == "BLAST":
        videos = req.videos or req.volume
        complexity = req.complexity or 1.35
        roi = videos * VALUE_PER_UNIT["BLAST"] * complexity * req.vertical
    elif req.product == "MRLIN":
        queries = (req.queries_k or 1) * 1000
        roi = queries * VALUE_PER_UNIT["MRLIN"] * DEFAULT_CONVERSION_RATE
    else:
        roi = req.volume * VALUE_PER_UNIT[req.product] * DEFAULT_CONVERSION_RATE

    multiple = roi / monthly_price if monthly_price > 0 else 0
    return round(roi, 2), round(multiple, 2)


# ============================================================================
# Public API — the one function the routes call
# ============================================================================
def calculate_quote(req: QuoteRequest) -> QuoteResponse:
    """
    Calculate a fair-price quote for any product.
    Pure function — no side effects, fully testable.
    """
    capped = False

    if req.product == "BLAST":
        monthly, capped, breakdown = _price_blast(req)
    elif req.product == "MRLIN":
        monthly, breakdown = _price_mrlin(req)
    else:
        monthly, breakdown = _price_an_vmio_amio(req)

    base_setup = BASE_FEES[req.product]["setup"]
    setup = calculate_setup_fee(base_setup, req.structure, req.revenue)

    estimated_roi, roi_multiple = _calculate_roi(req, monthly)
    tier = _tier_label(req.product, monthly)

    return QuoteResponse(
        quote_id=str(uuid.uuid4()),
        product=req.product,
        monthly_price=round(monthly, 2),
        setup_fee=setup,
        base_fee=BASE_FEES[req.product]["monthly"],
        estimated_roi=estimated_roi,
        roi_multiple=roi_multiple,
        tier=tier,
        capped=capped,
        breakdown=breakdown,
    )


# ============================================================================
# Bundle pricing
# ============================================================================
@dataclass
class BundleQuote:
    products: list[str]
    individual_prices: dict[str, float]
    alacarte_total: float
    discount_pct: float
    bundle_price: float
    monthly_savings: float


def calculate_bundle(quotes: dict[str, QuoteResponse]) -> BundleQuote:
    """
    Apply bundle discount based on product count.
    quotes is {product_code: QuoteResponse}
    """
    products = list(quotes.keys())
    individual = {p: q.monthly_price for p, q in quotes.items()}
    alacarte = sum(individual.values())

    count = len(products)
    discount = BUNDLE_DISCOUNTS.get(count, 0.0)
    bundle_price = alacarte * (1 - discount)
    savings = alacarte - bundle_price

    return BundleQuote(
        products=products,
        individual_prices=individual,
        alacarte_total=round(alacarte, 2),
        discount_pct=discount,
        bundle_price=round(bundle_price, 2),
        monthly_savings=round(savings, 2),
    )
