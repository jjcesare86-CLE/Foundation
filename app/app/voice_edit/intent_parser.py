"""
Foundation Layer · voice_edit · intent_parser.py

Turns a raw voice transcript ("change my hours to nine to five weekdays")
into either a confident JSON Patch or a clarifying question.

Routing per the efficiency skill:
  - Sonnet 4.6 for the parse itself (structured reasoning + JSON output)
  - Haiku 4.5 for a cheap pre-filter that classifies the utterance type
    (edit / question / chitchat / undo / confirm) before we burn Sonnet
    tokens.

The system prompt is static and prompt-cached so repeated calls are ~90%
cheaper after the first.
"""

from __future__ import annotations

import json
import os
from typing import Any

import anthropic

from .models import JsonPatchOp, ParsedIntent

# ---------------------------------------------------------------------
# Models — pulled from env per llm_router.py convention
# ---------------------------------------------------------------------
MODEL_PARSE      = os.getenv("MODEL_STANDARD", "claude-sonnet-4-6")
MODEL_PREFILTER  = os.getenv("MODEL_FAST",     "claude-haiku-4-5-20251001")

_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# ---------------------------------------------------------------------
# Static system prompt — cached
# ---------------------------------------------------------------------
_SYSTEM_PROMPT = """You are the voice-edit intent parser for an AI onboarding platform.

A customer is editing their business profile, website, voice agent, or social config by speaking. Your job: turn their utterance into a structured edit operation against the surface schema you'll be given.

You ALWAYS reply with a single JSON object matching this shape exactly — no prose, no markdown, no backticks:

{
  "confident": <bool>,
  "patch": [{"op": "add"|"replace"|"remove"|"append", "path": "<json-pointer>", "value": <any>}],
  "confidence": <0.0-1.0>,
  "explanation": "<one short sentence stating the change in the customer's voice, e.g. 'Your headline now reads X'>",
  "clarifying_question": "<string or null>",
  "candidates": [{"label": "<human label>", "path": "<json-pointer>"}],
  "requires_confirmation": <bool>,
  "affected_fields": ["<field key from schema>"]
}

Rules:
1. If the utterance unambiguously maps to ONE field in the schema, set confident=true, fill `patch`, leave `clarifying_question` and `candidates` empty.
2. If the utterance plausibly maps to 2+ fields, set confident=false, set `clarifying_question` to a short natural question, and list the candidates. Leave `patch` empty.
3. If the utterance is not an edit (it's a question, chitchat, or undo/confirm), set confident=false and set `clarifying_question` to "NOT_AN_EDIT".
4. `requires_confirmation` is true when ANY affected field has confirm:true in the schema.
5. Use the field's exact `path` from the schema. Never invent paths.
6. Validate values lightly: phone numbers should be E.164-ish, emails should look like emails, enums must match enum_values. If invalid, set confident=false and ask for clarification.
7. For list[T] fields: prefer `append` over `add` unless the customer specifies a position ("at the top" → /list/0, "at the end" → append).
8. For removal ("delete the testimonial about Bob"), use op:"remove" with the right index — but if you can't identify the index, ask.
9. Keep `explanation` < 25 words and phrased as a result the agent will read back, e.g. "Headline updated to 'Welcome to Joe's Plumbing'".
10. NEVER include keys outside the schema you're given. NEVER touch fields not in the schema.

You will receive the surface schema and the customer's transcript. Reply with the JSON object only."""


# ---------------------------------------------------------------------
# Pre-filter: cheap classification
# ---------------------------------------------------------------------
async def classify_utterance(transcript: str) -> str:
    """
    Returns one of: 'edit' | 'undo' | 'confirm' | 'cancel' | 'question' | 'chitchat'

    Cheap Haiku call so we don't burn Sonnet tokens on "okay" / "thanks" /
    "wait what did you say".
    """
    resp = _client.messages.create(
        model=MODEL_PREFILTER,
        max_tokens=10,
        system="Classify the customer utterance as one of: edit, undo, confirm, cancel, question, chitchat. Reply with the single word only.",
        messages=[{"role": "user", "content": transcript}],
    )
    label = resp.content[0].text.strip().lower()
    if label not in {"edit", "undo", "confirm", "cancel", "question", "chitchat"}:
        return "edit"   # safe default — let Sonnet figure it out
    return label


# ---------------------------------------------------------------------
# Main parse
# ---------------------------------------------------------------------
async def parse_voice_intent(
    transcript: str,
    surface_schema: dict[str, Any],
    current_state: dict[str, Any] | None = None,
    last_visible_section: str | None = None,
) -> ParsedIntent:
    """
    Parameters
    ----------
    transcript           : raw customer utterance from VAPI/Gemini.
    surface_schema       : the SurfaceSchema for the current surface,
                           dumped to dict (fields + aliases + paths).
    current_state        : current value of the target document, used to
                           resolve references like "the second testimonial".
    last_visible_section : if the customer is on the web form, the section
                           they were looking at — disambiguates "this".

    Returns
    -------
    ParsedIntent
    """
    user_payload = {
        "surface_schema": surface_schema,
        "current_state": current_state or {},
        "last_visible_section": last_visible_section,
        "transcript": transcript,
    }

    resp = _client.messages.create(
        model=MODEL_PARSE,
        max_tokens=1024,
        system=[
            {
                "type": "text",
                "text": _SYSTEM_PROMPT,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[
            {
                "role": "user",
                "content": json.dumps(user_payload, ensure_ascii=False),
            }
        ],
    )

    raw = resp.content[0].text.strip()

    # Defensive parse — Sonnet rarely strays but never trust the LLM
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        # Strip markdown fences if model added them despite instructions
        cleaned = raw.replace("```json", "").replace("```", "").strip()
        data = json.loads(cleaned)

    # Coerce patch ops into JsonPatchOp instances
    raw_patch = data.get("patch") or []
    patch_ops = [JsonPatchOp(**op) for op in raw_patch]

    return ParsedIntent(
        confident=bool(data.get("confident", False)),
        patch=patch_ops,
        confidence=float(data.get("confidence", 0.0)),
        explanation=data.get("explanation"),
        clarifying_question=data.get("clarifying_question"),
        candidates=data.get("candidates", []),
        requires_confirmation=bool(data.get("requires_confirmation", False)),
        affected_fields=data.get("affected_fields", []),
    )


# ---------------------------------------------------------------------
# Combined helper: prefilter → parse
# ---------------------------------------------------------------------
async def route_voice_input(
    transcript: str,
    surface_schema: dict[str, Any],
    current_state: dict[str, Any] | None = None,
    last_visible_section: str | None = None,
) -> tuple[str, ParsedIntent | None]:
    """
    Returns (utterance_class, parsed_intent_or_none).
    Caller handles undo/confirm/cancel/question/chitchat without needing
    to call parse_voice_intent.
    """
    klass = await classify_utterance(transcript)
    if klass != "edit":
        return klass, None

    parsed = await parse_voice_intent(
        transcript, surface_schema, current_state, last_visible_section
    )
    return klass, parsed
