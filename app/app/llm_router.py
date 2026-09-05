"""
llm_router.py — Foundation Layer Central LLM Router
Handles model selection, cost optimization, and prompt caching
across AN, VoiceMIO, Blast Video, and MRLIN.

Canonical location: foundation/llm_router.py
Runtime copy:       app/app/llm_router.py (kept in sync)

Env vars needed: ANTHROPIC_API_KEY, MODEL_FAST, MODEL_STANDARD, MODEL_COMPLEX,
                  MODEL_ORCH_MAX, MODEL_LONGCTX (optional overrides)

# ENTERPRISE FLIP: set MODEL_COMPLEX=claude-fable-5-1 in Render to move the
# full C-suite to Fable 5.1. See docs/specs/FOUNDATION_BATCH1... Part 0.1.
"""

import os
import logging
from enum import Enum
from typing import Optional
from datetime import datetime
import anthropic

logger = logging.getLogger(__name__)

# ─── Task Tier Enum ─────────────────────────────────────────────────────────

class TaskTier(str, Enum):
    FAST              = "fast"               # classify, tag, route, yes/no  → Haiku
    STANDARD          = "standard"           # draft, analyze, code, respond  → Sonnet
    COMPLEX           = "complex"            # bounded C-suite workloads      → Opus
    ORCHESTRATOR_MAX  = "orchestrator_max"   # Solomon + cross-agent escalations → Fable 5.1
    VOICE             = "voice"              # real-time audio agents         → Gemini 3.1 Flash Live
    LONGCTX           = "longctx"            # >100k token, Claude-native     → Fable 5.1 (1M ctx)

# Tiers that require prompt caching — the router refuses uncached calls on these.
CACHE_REQUIRED_TIERS = {TaskTier.COMPLEX, TaskTier.ORCHESTRATOR_MAX}

# ─── Model Registry (override via env vars for zero-code model swaps) ────────

MODEL_MAP: dict[TaskTier, str] = {
    TaskTier.FAST:             os.getenv("MODEL_FAST",     "claude-haiku-4-5-20251001"),
    TaskTier.STANDARD:         os.getenv("MODEL_STANDARD", "claude-sonnet-5"),
    TaskTier.COMPLEX:          os.getenv("MODEL_COMPLEX",  "claude-opus-4-8"),
    TaskTier.ORCHESTRATOR_MAX: os.getenv("MODEL_ORCH_MAX", "claude-fable-5-1"),
    TaskTier.VOICE:            os.getenv("MODEL_VOICE",    "gemini-3.1-flash-live"),
    TaskTier.LONGCTX:          os.getenv("MODEL_LONGCTX",  "claude-fable-5-1"),
}

# The model string that a fable-5.1 safeguard-flagged call reroutes to, billed
# at that model's rates. Resolved from whatever currently maps to fable-5.1 —
# not hardcoded to a tier — so the Enterprise flip (MODEL_COMPLEX=claude-fable-5-1)
# keeps working without touching this.
FALLBACK_MODEL = os.getenv("MODEL_FABLE_FALLBACK", "claude-opus-4-8")

# Pricing per 1M tokens (update when providers change pricing)
# "cache_input": price for cache-hit input tokens (prompt caching); falls back
# to 10% of "input" when not given explicitly.
PRICING_PER_1M: dict[str, dict] = {
    "claude-haiku-4-5-20251001": {"input": 0.80,   "output": 4.00},
    "claude-sonnet-4-6":         {"input": 3.00,   "output": 15.00},   # legacy — kept for cost lookups on old llm_usage rows
    "claude-sonnet-5":           {"input": 2.00,   "output": 10.00},
    "claude-opus-4-6":           {"input": 15.00,  "output": 75.00},   # legacy — kept for cost lookups on old llm_usage rows
    "claude-opus-4-8":           {"input": 5.00,   "output": 25.00,  "cache_input": 0.50},
    "claude-fable-5":            {"input": 10.00,  "output": 50.00,  "cache_input": 1.00},   # legacy — kept for cost lookups on old llm_usage rows
    "claude-fable-5-1":          {"input": 10.00,  "output": 50.00,  "cache_input": 0.25},   # cache reads 2.5% of input, not 10%
    "gemini-3.1-flash-live":     {"input": 0.50,   "output": 1.50},   # estimate — verify
    "gemini-3.1-pro":            {"input": 2.50,   "output": 10.00},  # estimate — verify
}

# ─── Anthropic Client ────────────────────────────────────────────────────────

_client: Optional[anthropic.Anthropic] = None

def get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    return _client

# ─── Core Router ─────────────────────────────────────────────────────────────

def llm_call(
    messages: list[dict],
    tier: TaskTier = TaskTier.STANDARD,
    system: Optional[str] = None,
    max_tokens: int = 2048,
    use_cache: bool = True,
    project: str = "foundation",
    agent_name: Optional[str] = None,
    task_type: Optional[str] = None,
) -> str:
    """
    Central LLM call with automatic model routing and cost tracking.

    Args:
        messages:    Anthropic messages array
        tier:        TaskTier — determines which model to use
        system:      System prompt string (cached by default)
        max_tokens:  Max output tokens
        use_cache:   Enable Anthropic prompt caching on system prompt
        project:     'AN' | 'VoiceMIO' | 'BlastVideo' | 'MRLIN' | 'foundation'
        agent_name:  Name of the agent making the call (for logging)
        task_type:   What kind of task (for logging + analysis)

    Returns:
        Response text string
    """
    model = MODEL_MAP[tier]

    # Prompt caching is mandatory on COMPLEX and ORCHESTRATOR_MAX — reject
    # uncached C-suite calls at the router level rather than silently
    # overriding the caller's intent.
    if tier in CACHE_REQUIRED_TIERS:
        if not use_cache:
            raise ValueError(
                f"tier={tier.value} requires prompt caching; refusing to call "
                f"with use_cache=False"
            )
        if not system:
            raise ValueError(
                f"tier={tier.value} requires a system prompt to cache; "
                f"got none"
            )

    # Build system param with optional prompt caching
    system_param = _build_system(system, use_cache)

    client = get_client()

    fallback_from = None
    try:
        response = _create_with_fallback(client, model, max_tokens, system_param, messages)
        if response.model != model:
            # Fallback API rerouted a safeguard-flagged fable-5 call.
            fallback_from = model
            model = response.model

        content = response.content[0].text

        # Log usage
        _log_usage(
            project=project,
            agent_name=agent_name,
            model=model,
            tier=tier,
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
            cache_read_input_tokens=getattr(response.usage, "cache_read_input_tokens", 0) or 0,
            cache_creation_input_tokens=getattr(response.usage, "cache_creation_input_tokens", 0) or 0,
            task_type="fable_fallback" if fallback_from else task_type,
            fallback_from=fallback_from,
        )

        return content

    except anthropic.APIError as e:
        logger.error(f"LLM call failed | model={model} tier={tier} error={e}")
        raise


def _create_with_fallback(client, model, max_tokens, system_param, messages):
    """
    Wraps messages.create() with the Anthropic Fallback API for fable-5.1
    calls: safeguard-flagged (bio/cyber) requests reroute to FALLBACK_MODEL
    and bill at its rates. NOTE: this targets whatever currently resolves
    to "claude-fable-5-1" — verify the exact Fallback API request/response
    shape against current Anthropic SDK docs before relying on this in
    production; the SDK surface for this is newer than what these
    comments were written against.
    """
    if model != "claude-fable-5-1":
        return client.messages.create(
            model=model,
            max_tokens=max_tokens,
            system=system_param,
            messages=messages,
        )

    try:
        return client.messages.create(
            model=model,
            max_tokens=max_tokens,
            system=system_param,
            messages=messages,
            extra_body={"fallback": {"model": FALLBACK_MODEL}},
        )
    except anthropic.APIError as e:
        # Safeguard-flag rejection without fallback support server-side —
        # fall back to Opus 4.8 client-side so a flagged business-ops query
        # (near-certainly a false positive for this workload) doesn't hard-fail.
        if getattr(e, "status_code", None) in (400, 403):
            logger.warning(f"fable-5 safeguard reroute → {FALLBACK_MODEL} | {e}")
            return client.messages.create(
                model=FALLBACK_MODEL,
                max_tokens=max_tokens,
                system=system_param,
                messages=messages,
            )
        raise


def llm_call_json(
    messages: list[dict],
    tier: TaskTier = TaskTier.STANDARD,
    system: Optional[str] = None,
    max_tokens: int = 2048,
    project: str = "foundation",
    agent_name: Optional[str] = None,
    task_type: Optional[str] = None,
) -> dict:
    """
    Same as llm_call but ensures JSON output.
    Appends JSON instruction to system prompt automatically.
    """
    json_system = (system or "") + "\n\nRespond ONLY with valid JSON. No markdown, no preamble."

    raw = llm_call(
        messages=messages,
        tier=tier,
        system=json_system,
        max_tokens=max_tokens,
        project=project,
        agent_name=agent_name,
        task_type=task_type,
    )

    import json
    # Strip markdown fences if model adds them anyway
    clean = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    return json.loads(clean)


# ─── Batch API (50% cost savings for non-urgent tasks) ───────────────────────

def llm_batch_prepare(
    requests: list[dict],
    tier: TaskTier = TaskTier.STANDARD,
) -> list[dict]:
    """
    Prepare requests for Anthropic Batch API.
    Use for non-urgent bulk tasks to save 50% on costs.

    Each request: {"custom_id": str, "messages": list, "system": str (optional)}
    Returns batch-ready request list for client.messages.batches.create()
    """
    model = MODEL_MAP[tier]
    batch_requests = []

    for req in requests:
        batch_requests.append({
            "custom_id": req["custom_id"],
            "params": {
                "model": model,
                "max_tokens": req.get("max_tokens", 2048),
                "system": req.get("system", ""),
                "messages": req["messages"],
            }
        })

    return batch_requests


# ─── Helper: Model Info ───────────────────────────────────────────────────────

def get_model(tier: TaskTier) -> str:
    """Get the current model string for a given tier."""
    return MODEL_MAP[tier]


def estimate_cost(
    input_tokens: int,
    output_tokens: int,
    model: str,
    cache_read_input_tokens: int = 0,
    cache_creation_input_tokens: int = 0,
) -> float:
    """
    Estimate USD cost for a call. Per Anthropic's usage accounting,
    input_tokens is already the non-cached ("fresh") count — cache_read_
    input_tokens and cache_creation_input_tokens are separate, additive
    fields, not a subset of input_tokens. cache_read bills at the model's
    cache_input rate (falls back to 10% of the input rate); cache_creation
    bills at the full input rate (writing the cache costs the same as a
    normal input token).
    """
    pricing = PRICING_PER_1M.get(model, {"input": 3.00, "output": 15.00})
    cache_rate = pricing.get("cache_input", pricing["input"] * 0.10)

    return (
        input_tokens * pricing["input"]
        + cache_read_input_tokens * cache_rate
        + cache_creation_input_tokens * pricing["input"]
        + output_tokens * pricing["output"]
    ) / 1_000_000


def model_summary() -> dict:
    """Return current model assignments — useful for health endpoint."""
    return {tier.value: model for tier, model in MODEL_MAP.items()}


# ─── Usage Logging ────────────────────────────────────────────────────────────

def _build_system(system: Optional[str], use_cache: bool) -> list | str:
    if not system:
        return []
    if use_cache:
        return [{"type": "text", "text": system, "cache_control": {"type": "ephemeral"}}]
    return system


_usage_client = None


def _get_usage_client():
    """Lazily create the Supabase client used for llm_usage logging."""
    global _usage_client
    if _usage_client is None:
        from supabase import create_client
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        if not url or not key:
            return None
        _usage_client = create_client(url, key)
    return _usage_client


def _log_usage(
    project: str,
    agent_name: Optional[str],
    model: str,
    tier: TaskTier,
    input_tokens: int,
    output_tokens: int,
    task_type: Optional[str],
    cache_read_input_tokens: int = 0,
    cache_creation_input_tokens: int = 0,
    fallback_from: Optional[str] = None,
):
    """Log token usage to foundation.llm_usage (best-effort — never blocks the call)."""
    cost = estimate_cost(
        input_tokens, output_tokens, model,
        cache_read_input_tokens, cache_creation_input_tokens,
    )

    logger.info(
        f"LLM | project={project} agent={agent_name} model={model} "
        f"tier={tier.value} in={input_tokens} out={output_tokens} "
        f"cache_read={cache_read_input_tokens} cache_write={cache_creation_input_tokens} "
        f"cost=${cost:.6f} task={task_type}"
        + (f" fallback_from={fallback_from}" if fallback_from else "")
    )

    try:
        client = _get_usage_client()
        if client is None:
            logger.warning("llm_usage insert skipped — SUPABASE_URL/SERVICE_ROLE_KEY not set")
            return
        client.schema("foundation").table("llm_usage").insert({
            "project": project,
            "agent_name": agent_name,
            "model": model,
            "tier": tier.value,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cache_read_input_tokens": cache_read_input_tokens,
            "cache_creation_input_tokens": cache_creation_input_tokens,
            "estimated_cost_usd": round(cost, 6),
            "task_type": task_type,
            "fallback_from": fallback_from,
        }).execute()
    except Exception as e:
        # Usage logging must never break the caller's LLM call.
        logger.error(f"llm_usage insert failed: {e}")
