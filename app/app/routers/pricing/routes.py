"""
FastAPI routes for the Foundation Pricing Engine.

Mounts at /pricing/* on the foundation-api service.
All endpoints require X-API-Key header matching PIPELINE_API_KEY env var.
"""
from __future__ import annotations

import os
import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, status
from fastapi.responses import JSONResponse

from .schemas import (
    QuoteRequest, QuoteResponse, QuoteLogRequest, QuoteLogResponse,
    VoiceQuoteRequest, VoiceIncentiveRequest, VoiceIncentiveResponse,
    VoiceDiscountRequest, VoiceDiscountResponse,
    VoiceEscalateRequest, VoiceEscalateResponse,
    NegotiationTier,
)
from .pricing_engine import calculate_quote, BASE_FEES
from .voice_pricing import (
    PERSONA_PRODUCT,
    TIER_2_CATALOG,
    evaluate_discount_request,
    quote_script,
    soft_incentive_script,
    discount_script,
    escalation_script,
)

log = logging.getLogger(__name__)
router = APIRouter(prefix="/pricing", tags=["pricing"])


# ============================================================================
# Auth dependency
# ============================================================================
def verify_api_key(x_api_key: Annotated[str | None, Header()] = None) -> None:
    expected = os.getenv("PIPELINE_API_KEY")
    if not expected:
        log.error("PIPELINE_API_KEY not set in environment")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Server misconfiguration: API key not set",
        )
    if x_api_key != expected:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing X-API-Key header",
        )


# ============================================================================
# Supabase client (lazy init)
# ============================================================================
_supabase = None


def get_supabase():
    """Lazy-initialize Supabase client. Returns None if not configured."""
    global _supabase
    if _supabase is not None:
        return _supabase

    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    if not url or not key:
        log.warning("Supabase not configured — quote logging disabled")
        return None

    try:
        from supabase import create_client
        _supabase = create_client(url, key)
        return _supabase
    except ImportError:
        log.warning("supabase-py not installed — quote logging disabled")
        return None


# ============================================================================
# Health
# ============================================================================
@router.get("/health")
async def health() -> dict:
    sb = get_supabase()
    return {
        "status": "ok",
        "supabase_configured": sb is not None,
        "version": "v5",
    }


# ============================================================================
# Quote endpoint — fair-price calculation
# ============================================================================
@router.post("/quote", response_model=QuoteResponse, dependencies=[Depends(verify_api_key)])
async def quote(req: QuoteRequest) -> QuoteResponse:
    """
    Calculate a fair-price quote. Used by:
    - Customer-facing calculators (no auth — proxied through public endpoint)
    - Internal quote tools
    - Voice agents (via /pricing/voice/quote which adds persona context)
    - Bundle calculator
    """
    return calculate_quote(req)


# ============================================================================
# Quote log — persist to pricing_quotes
# ============================================================================
@router.post("/quote/log", response_model=QuoteLogResponse, dependencies=[Depends(verify_api_key)])
async def log_quote(req: QuoteLogRequest) -> QuoteLogResponse:
    sb = get_supabase()
    if sb is None:
        return QuoteLogResponse(quote_id="", written=False)

    try:
        result = sb.table("pricing_quotes").insert({
            "contact_id": req.contact_id,
            "product": req.product,
            "inputs": req.inputs,
            "multipliers": req.multipliers,
            "base_fee": req.base_fee,
            "monthly_price": req.monthly_price,
            "setup_fee": req.setup_fee,
            "estimated_roi": req.estimated_roi,
            "roi_multiple": req.roi_multiple,
            "tier": req.tier,
            "source": req.source,
            "status": req.status,
            "negotiation_notes": req.negotiation_notes,
            "override_multipliers": req.override_multipliers,
        }).execute()

        quote_id = result.data[0]["id"] if result.data else ""
        return QuoteLogResponse(quote_id=str(quote_id), written=True)
    except Exception as e:
        log.exception(f"Failed to log quote: {e}")
        return QuoteLogResponse(quote_id="", written=False)


# ============================================================================
# Voice agent endpoints
# ============================================================================
@router.post("/voice/quote", response_model=QuoteResponse, dependencies=[Depends(verify_api_key)])
async def voice_quote(req: VoiceQuoteRequest) -> QuoteResponse:
    """
    Voice-agent quote endpoint. Same math as /quote but:
    - Adds persona-specific speak_script
    - Auto-logs to pricing_quotes with source=voice_agent
    """
    quote_resp = calculate_quote(req)
    quote_resp.speak_script = quote_script(
        persona=req.persona,
        monthly=quote_resp.monthly_price,
        setup=quote_resp.setup_fee,
        tier=quote_resp.tier,
        roi_x=quote_resp.roi_multiple,
    )

    # Auto-log Tier 1
    sb = get_supabase()
    if sb is not None:
        try:
            sb.table("pricing_quotes").insert({
                "contact_id": req.contact_id,
                "product": req.product,
                "inputs": req.model_dump(exclude={"contact_id", "company_name"}),
                "multipliers": {},
                "base_fee": quote_resp.base_fee,
                "monthly_price": quote_resp.monthly_price,
                "setup_fee": quote_resp.setup_fee,
                "estimated_roi": quote_resp.estimated_roi,
                "roi_multiple": quote_resp.roi_multiple,
                "tier": quote_resp.tier,
                "source": "voice_agent",
                "status": "draft",
                "override_multipliers": {
                    "persona": req.persona,
                    "tier_reached": NegotiationTier.TIER_1_QUOTE.value,
                    "call_sid": req.call_sid,
                    "quote_id": quote_resp.quote_id,
                },
            }).execute()
        except Exception as e:
            log.warning(f"Voice quote log failed (non-fatal): {e}")

    return quote_resp


@router.post(
    "/voice/incentive",
    response_model=VoiceIncentiveResponse,
    dependencies=[Depends(verify_api_key)],
)
async def voice_incentive(req: VoiceIncentiveRequest) -> VoiceIncentiveResponse:
    """Tier 2 — soft incentive, no monetary discount."""
    if req.incentive_key not in TIER_2_CATALOG:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown incentive key: {req.incentive_key}",
        )

    concession = TIER_2_CATALOG[req.incentive_key]
    script = soft_incentive_script(req.persona, concession)

    # Log Tier 2 concession
    sb = get_supabase()
    if sb is not None:
        try:
            sb.table("pricing_quotes").update({
                "negotiation_notes": f"Tier 2 offered: {concession.label}",
                "override_multipliers": {
                    "persona": req.persona,
                    "tier_reached": NegotiationTier.TIER_2_SOFT.value,
                    "incentive": concession.incentive_type,
                    "call_sid": req.call_sid,
                },
            }).eq("override_multipliers->>quote_id", req.quote_id).execute()
        except Exception as e:
            log.warning(f"Tier 2 log update failed: {e}")

    return VoiceIncentiveResponse(
        quote_id=req.quote_id,
        concession_label=concession.label,
        new_monthly=0.0,  # No price change in Tier 2
        new_setup=0.0,
        speak_script=script,
        tier_reached=NegotiationTier.TIER_2_SOFT,
    )


@router.post(
    "/voice/discount",
    response_model=VoiceDiscountResponse,
    dependencies=[Depends(verify_api_key)],
)
async def voice_discount(req: VoiceDiscountRequest) -> VoiceDiscountResponse:
    """Tier 3 — capped monetary discount. Up to 20% off + setup waiver."""
    concession, needs_escalation = evaluate_discount_request(
        requested_monthly_pct=req.requested_monthly_pct,
        requested_setup_waive=req.requested_setup_waive,
    )

    if needs_escalation or concession is None:
        return VoiceDiscountResponse(
            quote_id=req.quote_id,
            escalated=True,
            speak_script=escalation_script(req.persona),
            tier_reached=NegotiationTier.TIER_4_ESCALATE,
        )

    # Apply concession to original quote (lookup from Supabase)
    sb = get_supabase()
    new_monthly = 0.0
    new_setup = 0.0
    setup_savings = 0.0

    if sb is not None:
        try:
            result = (
                sb.table("pricing_quotes")
                .select("monthly_price, setup_fee")
                .eq("override_multipliers->>quote_id", req.quote_id)
                .order("created_at", desc=True)
                .limit(1)
                .execute()
            )
            if result.data:
                base_monthly = result.data[0]["monthly_price"]
                base_setup = result.data[0]["setup_fee"]
                new_monthly = base_monthly * (1 - concession.monthly_discount_pct)
                new_setup = base_setup * (1 - concession.setup_discount_pct)
                setup_savings = base_setup - new_setup
        except Exception as e:
            log.warning(f"Tier 3 quote lookup failed: {e}")

    script = discount_script(req.persona, concession, new_monthly, setup_savings)

    # Log Tier 3
    if sb is not None:
        try:
            sb.table("pricing_quotes").update({
                "monthly_price": round(new_monthly, 2),
                "setup_fee": round(new_setup, 2),
                "negotiation_notes": f"Tier 3 offered: {concession.label}",
                "override_multipliers": {
                    "persona": req.persona,
                    "tier_reached": NegotiationTier.TIER_3_HARD.value,
                    "discount_pct": concession.monthly_discount_pct,
                    "setup_waived": concession.setup_discount_pct >= 1.0,
                    "call_sid": req.call_sid,
                },
            }).eq("override_multipliers->>quote_id", req.quote_id).execute()
        except Exception as e:
            log.warning(f"Tier 3 log update failed: {e}")

    return VoiceDiscountResponse(
        quote_id=req.quote_id,
        escalated=False,
        concession_label=concession.label,
        new_monthly=round(new_monthly, 2),
        new_setup=round(new_setup, 2),
        speak_script=script,
        tier_reached=NegotiationTier.TIER_3_HARD,
    )


@router.post(
    "/voice/escalate",
    response_model=VoiceEscalateResponse,
    dependencies=[Depends(verify_api_key)],
)
async def voice_escalate(req: VoiceEscalateRequest) -> VoiceEscalateResponse:
    """Tier 4 — hand off to John. Logs and ideally fires a Slack/email alert."""
    script = escalation_script(req.persona)

    sb = get_supabase()
    notif_sent = False
    if sb is not None:
        try:
            sb.table("pricing_quotes").update({
                "status": "draft",
                "negotiation_notes": f"ESCALATED: {req.reason} — {req.context}",
                "override_multipliers": {
                    "persona": req.persona,
                    "tier_reached": NegotiationTier.TIER_4_ESCALATE.value,
                    "escalated": True,
                    "escalation_reason": req.reason,
                    "context": req.context,
                    "call_sid": req.call_sid,
                },
            }).eq("override_multipliers->>quote_id", req.quote_id).execute()
            notif_sent = True
        except Exception as e:
            log.exception(f"Escalation log failed: {e}")

    # TODO: hook up Slack webhook or email alert here
    log.info(f"ESCALATION: {req.persona} → John for quote {req.quote_id}: {req.context}")

    return VoiceEscalateResponse(
        quote_id=req.quote_id,
        escalated=True,
        speak_script=script,
        notification_sent=notif_sent,
    )
