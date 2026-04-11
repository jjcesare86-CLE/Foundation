"""
llm_router.py — Foundation Layer Central LLM Router
Handles model selection, cost optimization, and prompt caching
across AN, VoiceMIO, Blast Video, and MRLIN.

Canonical location: foundation/llm_router.py
Runtime copy:       app/app/llm_router.py (kept in sync)

Env vars needed: ANTHROPIC_API_KEY, MODEL_FAST, MODEL_STANDARD, MODEL_COMPLEX (optional overrides)
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
    FAST     = "fast"      # classify, tag, route, yes/no  → Haiku
    STANDARD = "standard"  # draft, analyze, code, respond  → Sonnet
    COMPLEX  = "complex"   # plan, architect, multi-step    → Opus
    VOICE    = "voice"     # real-time audio agents         → Gemini 3.1 Flash Live
    LONGCTX  = "longctx"   # >100k token tasks              → Gemini 3.1 Pro

# ─── Model Registry (override via env vars for zero-code model swaps) ────────

MODEL_MAP: dict[TaskTier, str] = {
    TaskTier.FAST:     os.getenv("MODEL_FAST",     "claude-haiku-4-5-20251001"),
    TaskTier.STANDARD: os.getenv("MODEL_STANDARD", "claude-sonnet-4-6"),
    TaskTier.COMPLEX:  os.getenv("MODEL_COMPLEX",  "claude-opus-4-6"),
    TaskTier.VOICE:    os.getenv("MODEL_VOICE",    "gemini-3.1-flash-live"),
    TaskTier.LONGCTX:  os.getenv("MODEL_LONGCTX",  "gemini-3.1-pro"),
}

# Pricing per 1M tokens (update when providers change pricing)
PRICING_PER_1M: dict[str, dict] = {
    "claude-haiku-4-5-20251001": {"input": 0.80,   "output": 4.00},
    "claude-sonnet-4-6":         {"input": 3.00,   "output": 15.00},
    "claude-opus-4-6":           {"input": 15.00,  "output": 75.00},
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

    # Build system param with optional prompt caching
    system_param = _build_system(system, use_cache)

    client = get_client()

    try:
        response = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            system=system_param,
            messages=messages,
        )

        content = response.content[0].text

        # Log usage
        _log_usage(
            project=project,
            agent_name=agent_name,
            model=model,
            tier=tier,
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens,
            task_type=task_type,
        )

        return content

    except anthropic.APIError as e:
        logger.error(f"LLM call failed | model={model} tier={tier} error={e}")
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


def estimate_cost(input_tokens: int, output_tokens: int, model: str) -> float:
    """Estimate USD cost for a call."""
    pricing = PRICING_PER_1M.get(model, {"input": 3.00, "output": 15.00})
    return (input_tokens * pricing["input"] + output_tokens * pricing["output"]) / 1_000_000


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


def _log_usage(
    project: str,
    agent_name: Optional[str],
    model: str,
    tier: TaskTier,
    input_tokens: int,
    output_tokens: int,
    task_type: Optional[str],
):
    """Log token usage. Extend to write to Supabase llm_usage table."""
    cost = estimate_cost(input_tokens, output_tokens, model)

    logger.info(
        f"LLM | project={project} agent={agent_name} model={model} "
        f"tier={tier.value} in={input_tokens} out={output_tokens} "
        f"cost=${cost:.6f} task={task_type}"
    )

    # TODO: async Supabase insert
    # from supabase import create_client
    # supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_SERVICE_KEY"))
    # supabase.table("llm_usage").insert({
    #     "project": project,
    #     "agent_name": agent_name,
    #     "model": model,
    #     "tier": tier.value,
    #     "input_tokens": input_tokens,
    #     "output_tokens": output_tokens,
    #     "estimated_cost_usd": cost,
    #     "task_type": task_type,
    # }).execute()
