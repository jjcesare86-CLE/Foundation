"""Foundation Pricing Engine — shared pricing module."""
from .pricing_engine import calculate_quote, calculate_setup_fee, calculate_bundle, BASE_FEES
from .voice_pricing import (
    PERSONA_PRODUCT,
    TIER_2_CATALOG,
    evaluate_discount_request,
    quote_script,
    soft_incentive_script,
    discount_script,
    escalation_script,
)
from .routes import router as pricing_router

__version__ = "5.0.0"
__all__ = [
    "calculate_quote",
    "calculate_setup_fee",
    "calculate_bundle",
    "BASE_FEES",
    "PERSONA_PRODUCT",
    "TIER_2_CATALOG",
    "evaluate_discount_request",
    "quote_script",
    "soft_incentive_script",
    "discount_script",
    "escalation_script",
    "pricing_router",
]
