"""
Foundation API · research router

Implements the research_pipeline skill as a programmatic endpoint.
Pipeline phases (mirroring foundation/skills/research_pipeline/):
  01 scope    → LLM call, no tools
  02 gather   → Anthropic web_search tool_use loop (Sonnet)
  03 verify   → LLM call, no tools
  04 draft    → LLM call, no tools
  05 finalize → emit markdown; upload to Supabase Storage; PDF stubbed

Auth: PIPELINE_API_KEY (header `X-API-Key` or `Authorization: Bearer <key>`)
Routing: synchronous request; quick-mode (~1-3 min) recommended for HTTP path,
deep-mode (5-25 min) may require a worker timeout extension.

Out of scope for v1 (TODO when next sprint touches this):
  - PDF rendering via weasyprint or pandoc
  - SER API fallback when web_search is unavailable
  - Async job queue for deep-mode runs

See foundation/skills/research_pipeline/SKILL.md for the canonical contract.
"""
from __future__ import annotations

import json
import logging
import os
import re
import time
from datetime import datetime, timezone
from typing import Annotated, Literal, Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel, Field

from app.database import supabase
from app.llm_router import TaskTier, estimate_cost, get_client, llm_call

log = logging.getLogger(__name__)

router = APIRouter(prefix="/research", tags=["research"])


# ─── Auth ─────────────────────────────────────────────────────────────────────

def verify_api_key(
    x_api_key: Annotated[Optional[str], Header()] = None,
    authorization: Annotated[Optional[str], Header()] = None,
) -> None:
    expected = os.getenv("PIPELINE_API_KEY")
    if not expected:
        log.warning("PIPELINE_API_KEY not set — research endpoint open in dev")
        return
    got = x_api_key or (authorization or "").removeprefix("Bearer ").strip()
    if got != expected:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")


# ─── Schemas ──────────────────────────────────────────────────────────────────

class RunResearchRequest(BaseModel):
    topic: str = Field(..., min_length=4, description="The research question or brief.")
    depth: Literal["quick", "deep"] = "quick"
    output_format: Literal["md", "pdf", "both"] = "md"
    audience: Optional[str] = Field(None, description="Who reads this? (proposal, exec brief, etc.)")
    requesting_agent: Optional[str] = Field(None, description="Biblical name of the agent requesting (for logging).")


class RunResearchResponse(BaseModel):
    report_url: Optional[str] = Field(None, description="Public URL to the final report.")
    sources_count: int
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    run_id: str
    md_inline: Optional[str] = Field(None, description="Inline markdown body when storage upload unavailable.")
    warnings: list[str] = Field(default_factory=list)


# ─── Phase 01 · Scope ─────────────────────────────────────────────────────────

PHASE_01_SYSTEM = """You are running phase 01 of the research_pipeline skill.

Your job: take a raw user research request and produce a tight scope document.
Output VALID JSON with this shape:

{
  "restated_question": "<one sentence>",
  "sub_questions": ["...", "..."],     // 3 to 7 items
  "success_criteria": ["...", "..."],   // 2 to 5 items
  "source_tier_priority": ["authoritative", "analyst", "vendor", "blog"],
  "freshness_months": 18,               // override only with explicit reason
  "estimated_source_count": 8,          // 5-10 quick, 20-40 deep
  "search_queries": ["...", "..."]      // 4-8 distinct query strings for phase 02
}

If the request is too vague to scope, return:
{"clarifying_question": "<one focused question>"}

No prose, no markdown — JSON only.
"""


def run_phase_01_scope(topic: str, depth: str, audience: Optional[str], run_id: str) -> dict:
    user_msg = (
        f"Topic: {topic}\n"
        f"Depth: {depth}\n"
        f"Audience: {audience or 'unspecified'}\n\n"
        f"Produce the scope JSON."
    )
    raw = llm_call(
        messages=[{"role": "user", "content": user_msg}],
        tier=TaskTier.STANDARD,
        system=PHASE_01_SYSTEM,
        max_tokens=1024,
        project="foundation",
        agent_name=f"research_pipeline:{run_id}",
        task_type="research:phase_01_scope",
    )
    return _parse_json(raw, "phase_01_scope")


# ─── Phase 02 · Gather (Anthropic web_search tool_use) ────────────────────────

PHASE_02_SYSTEM = """You are running phase 02 of the research_pipeline skill.

Use the web_search tool to gather sources for each sub-question. Run multiple
searches if needed. For each source you decide is worth keeping, capture:
  - URL
  - Title
  - Publication / author / date if visible
  - 2-4 verbatim key quotes (no paraphrasing)
  - Tier classification: authoritative | analyst | vendor | blog
  - Bias note if any

When you have enough sources (target: estimated_source_count from scope),
emit a final JSON object with this shape:

{
  "sources": [
    {
      "id": 1,
      "url": "https://...",
      "title": "...",
      "publication": "...",
      "publication_date": "YYYY-MM-DD or null",
      "tier": "authoritative",
      "bias_note": "...",
      "supports_subquestion": [1, 3],
      "key_quotes": ["...", "..."],
      "summary": "2-3 sentences"
    }
  ]
}

Reject sources older than the freshness_months from scope unless you note why
in bias_note. Prefer primary sources over secondary.

Final output: JSON only. No prose.
"""


def run_phase_02_gather(scope: dict, run_id: str) -> list[dict]:
    """Use Anthropic web_search tool to gather sources. Falls back to empty list if tool unavailable."""
    client = get_client()
    model = os.getenv("MODEL_STANDARD", "claude-sonnet-4-6")

    user_msg = (
        f"Scope:\n```json\n{json.dumps(scope, indent=2)}\n```\n\n"
        f"Run web searches and return the sources JSON."
    )

    max_uses = 8 if scope.get("estimated_source_count", 8) <= 10 else 20
    web_search_tool = {
        "type": "web_search_20250305",
        "name": "web_search",
        "max_uses": max_uses,
    }

    try:
        response = client.messages.create(
            model=model,
            max_tokens=8192,
            system=PHASE_02_SYSTEM,
            tools=[web_search_tool],
            messages=[{"role": "user", "content": user_msg}],
        )
    except Exception as e:
        log.exception(f"phase_02 web_search failed: {e}")
        return []

    # Log usage (inline since this call bypasses llm_call due to tool_use)
    try:
        in_tokens = response.usage.input_tokens
        out_tokens = response.usage.output_tokens
        cost = estimate_cost(in_tokens, out_tokens, model)
        log.info(
            f"LLM | project=foundation agent=research_pipeline:{run_id} model={model} "
            f"tier=standard in={in_tokens} out={out_tokens} cost=${cost:.6f} "
            f"task=research:phase_02_gather"
        )
    except Exception:
        pass

    # Extract the final text block (the JSON output) from a possibly tool-use-interleaved response
    text_blocks = [b.text for b in response.content if getattr(b, "type", None) == "text"]
    if not text_blocks:
        log.warning("phase_02 returned no text blocks — likely model is mid-tool-use; v1 expects single-pass")
        return []

    final_text = text_blocks[-1]
    parsed = _parse_json(final_text, "phase_02_gather", strict=False)
    return parsed.get("sources", []) if isinstance(parsed, dict) else []


# ─── Phase 03 · Verify ────────────────────────────────────────────────────────

PHASE_03_SYSTEM = """You are running phase 03 of the research_pipeline skill.

Given the scope and the gathered sources, extract every distinct factual claim
and assess whether ≥2 cross-tier sources support it.

Hard rules:
  - A claim is verified only if ≥2 sources support it AND ideally ≠1 tier
  - Single-source claims are flagged "unverified"
  - Conflicts are surfaced, not buried
  - Do not invent claims. Only claims actually present in the sources.

Output VALID JSON:

{
  "claims": [
    {
      "subquestion": 1,
      "text": "Claim restated",
      "source_ids": [1, 4],
      "verified": true,
      "tier_diversity": true,
      "notes": ""
    }
  ],
  "conflicts": [
    {"description": "Source 2 says X, source 5 says Y. Source 5 is more recent and analyst-tier."}
  ],
  "verification_rate": 0.82,
  "below_threshold": false
}

verification_rate = verified_claims / total_claims.
below_threshold is true if rate < 0.70.

JSON only.
"""


def run_phase_03_verify(scope: dict, sources: list[dict], run_id: str) -> dict:
    user_msg = (
        f"Scope:\n```json\n{json.dumps(scope, indent=2)}\n```\n\n"
        f"Sources:\n```json\n{json.dumps(sources, indent=2)}\n```\n\n"
        f"Produce the verification JSON."
    )
    raw = llm_call(
        messages=[{"role": "user", "content": user_msg}],
        tier=TaskTier.STANDARD,
        system=PHASE_03_SYSTEM,
        max_tokens=4096,
        project="foundation",
        agent_name=f"research_pipeline:{run_id}",
        task_type="research:phase_03_verify",
    )
    return _parse_json(raw, "phase_03_verify")


# ─── Phase 04 · Draft ─────────────────────────────────────────────────────────

PHASE_04_SYSTEM = """You are running phase 04 of the research_pipeline skill.

Write the report body in markdown using the verified claims and the sources.

Required structure:
  # <Topic>
  > **TL;DR.** 3-5 bullets, each with [^N] citation
  ## Background
  ## Sub-question 1: ...
  ## Sub-question 2: ...
  ## Risks / unknowns
  ## Recommendations

Hard rules:
  - Every factual claim ends with [^N] citation
  - Single-source claims marked [unverified] inline
  - Conflicts surfaced, not buried
  - Numbers always with unit and date: "$45B (2024)"
  - Active voice
  - Never recommend pricing below floors ($299 AN/VoiceMIO/Assistmio, $99 MRLIN/Blast)

Do NOT include a References section yet — phase 05 appends it from the source list.

Output: pure markdown. No JSON, no preamble.
"""


def run_phase_04_draft(scope: dict, verified: dict, sources: list[dict], run_id: str) -> str:
    user_msg = (
        f"Scope:\n```json\n{json.dumps(scope, indent=2)}\n```\n\n"
        f"Verified claims:\n```json\n{json.dumps(verified, indent=2)}\n```\n\n"
        f"Sources (for direct quotes):\n```json\n{json.dumps(sources, indent=2)}\n```\n\n"
        f"Write the report body."
    )
    return llm_call(
        messages=[{"role": "user", "content": user_msg}],
        tier=TaskTier.STANDARD,
        system=PHASE_04_SYSTEM,
        max_tokens=6000,
        project="foundation",
        agent_name=f"research_pipeline:{run_id}",
        task_type="research:phase_04_draft",
    )


# ─── Phase 05 · Finalize ──────────────────────────────────────────────────────

def run_phase_05_finalize(
    topic: str,
    body_md: str,
    sources: list[dict],
    verified: dict,
    output_format: str,
    run_id: str,
) -> tuple[Optional[str], Optional[str], list[str]]:
    """Returns (report_url, md_inline, warnings)."""
    warnings: list[str] = []
    confidence = float(verified.get("verification_rate", 0.0) or 0.0)
    total_claims = len(verified.get("claims", []) or [])
    verified_count = sum(1 for c in verified.get("claims", []) if c.get("verified"))
    unverified_count = total_claims - verified_count
    conflicts_count = len(verified.get("conflicts", []) or [])

    confidence_block = (
        f"\n\n## Confidence\n\n"
        f"- **Verification rate:** {confidence:.0%} of claims have ≥2 cross-tier sources\n"
        f"- **Total sources used:** {len(sources)}\n"
        f"- **Conflicts surfaced:** {conflicts_count}\n"
        f"- **Single-source claims (`[unverified]` in body):** {unverified_count}\n"
    )

    references_block = "\n\n## References\n\n"
    for s in sources:
        sid = s.get("id")
        title = s.get("title", "Untitled")
        url = s.get("url", "")
        pub_date = s.get("publication_date") or "n.d."
        tier = s.get("tier", "unknown")
        bias = s.get("bias_note", "")
        bias_str = f" — {bias}" if bias else ""
        references_block += f"[^{sid}]: {title} — [{url}]({url}) — {pub_date} — tier: {tier}{bias_str}\n"

    final_md = body_md.rstrip() + confidence_block + references_block

    # Try uploading MD to Supabase Storage; fall back to inline return
    slug = _slugify(topic)
    storage_path = f"research/{run_id}/{slug}.md"
    public_url: Optional[str] = None
    md_inline: Optional[str] = None

    try:
        bucket = "foundation-bucket"
        supabase.storage.from_(bucket).upload(
            path=storage_path,
            file=final_md.encode("utf-8"),
            file_options={"content-type": "text/markdown", "upsert": "true"},
        )
        public_url = f"{os.getenv('SUPABASE_URL', '').rstrip('/')}/storage/v1/object/public/{bucket}/{storage_path}"
    except Exception as e:
        log.warning(f"Storage upload failed (non-fatal): {e}")
        warnings.append(f"storage_upload_failed: {e}")
        md_inline = final_md

    if output_format in ("pdf", "both"):
        warnings.append("pdf_not_implemented_v1: weasyprint not in requirements.txt")

    return public_url, md_inline, warnings


# ─── Helpers ──────────────────────────────────────────────────────────────────

_JSON_FENCE_RE = re.compile(r"^```(?:json)?\s*|\s*```$", re.MULTILINE)


def _parse_json(raw: str, label: str, strict: bool = True) -> dict:
    cleaned = _JSON_FENCE_RE.sub("", raw.strip()).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        if strict:
            log.error(f"{label} returned invalid JSON: {e}\nraw: {raw[:500]}")
            raise HTTPException(500, f"{label} returned invalid JSON")
        log.warning(f"{label} JSON parse failed (non-strict): {e}")
        return {}


def _slugify(s: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9]+", "-", s.lower()).strip("-")
    return s[:60] or "untitled"


# ─── Main endpoint ────────────────────────────────────────────────────────────

@router.post("/run", response_model=RunResearchResponse, dependencies=[Depends(verify_api_key)])
async def run_research(req: RunResearchRequest) -> RunResearchResponse:
    """
    Run the full 5-phase research pipeline.

    Quick mode (~1-3 min): 5-10 sources, recommended for HTTP path.
    Deep mode (5-25 min): 20-40 sources, may require worker timeout extension.

    See foundation/skills/research_pipeline/SKILL.md for full contract.
    """
    run_id = str(uuid4())
    started = time.time()
    log.info(f"research:run id={run_id} topic={req.topic[:80]!r} depth={req.depth}")

    # Phase 01
    scope = run_phase_01_scope(req.topic, req.depth, req.audience, run_id)
    if "clarifying_question" in scope:
        raise HTTPException(
            status_code=400,
            detail={"clarifying_question": scope["clarifying_question"]},
        )

    # Phase 02
    sources = run_phase_02_gather(scope, run_id)
    if not sources:
        raise HTTPException(
            status_code=502,
            detail="phase_02_gather returned no sources — web_search unavailable or model failed mid-tool-use",
        )

    # Phase 03
    verified = run_phase_03_verify(scope, sources, run_id)
    if verified.get("below_threshold"):
        log.warning(f"research:run id={run_id} verification rate {verified.get('verification_rate')} below 0.70")
        # v1: continue anyway, surface in confidence_score. Future: re-gather.

    # Phase 04
    body_md = run_phase_04_draft(scope, verified, sources, run_id)

    # Phase 05
    report_url, md_inline, warnings = run_phase_05_finalize(
        topic=req.topic,
        body_md=body_md,
        sources=sources,
        verified=verified,
        output_format=req.output_format,
        run_id=run_id,
    )

    elapsed = time.time() - started
    log.info(f"research:run id={run_id} done elapsed={elapsed:.1f}s sources={len(sources)} confidence={verified.get('verification_rate')}")

    return RunResearchResponse(
        report_url=report_url,
        sources_count=len(sources),
        confidence_score=float(verified.get("verification_rate", 0.0) or 0.0),
        run_id=run_id,
        md_inline=md_inline,
        warnings=warnings,
    )


@router.get("/health")
async def health() -> dict:
    return {
        "status": "ok",
        "pipeline_version": "v1",
        "implemented": ["phase_01_scope", "phase_02_gather", "phase_03_verify", "phase_04_draft", "phase_05_finalize_md"],
        "todo": ["phase_05_pdf", "async_deep_mode", "ser_api_fallback"],
    }
