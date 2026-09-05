"""
Foundation Layer · voice_edit · upload_classifier.py

When a customer drags a file onto the LiveEditPanel, we need to figure
out what it IS and where it should go.

Strategy:
  1. Cheap heuristics first (mime type + dimensions + filename hints).
     Most uploads are unambiguous and never need an LLM call.
  2. Haiku 4.5 with vision for the genuinely ambiguous cases — e.g.
     "is this portrait JPG meant to be a logo, hero image, or team photo?"
"""

from __future__ import annotations

import base64
import os
from dataclasses import dataclass
from typing import Literal

import anthropic

MODEL_FAST = os.getenv("MODEL_FAST", "claude-haiku-4-5-20251001")
_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


AssetKind = Literal[
    "logo", "hero_image", "profile_image", "team_photo",
    "product_photo", "document", "legal_doc", "other"
]


@dataclass
class ClassificationResult:
    kind: AssetKind
    confidence: float
    suggested_field_path: str | None
    needs_user_confirmation: bool


# ---------------------------------------------------------------------
# Heuristic layer — fast, free, handles ~80% of cases
# ---------------------------------------------------------------------

def _filename_hint(filename: str) -> AssetKind | None:
    f = filename.lower()
    if any(k in f for k in ("logo", "brand", "mark")):
        return "logo"
    if any(k in f for k in ("avatar", "headshot", "profile", "portrait")):
        return "profile_image"
    if any(k in f for k in ("hero", "banner", "cover")):
        return "hero_image"
    if any(k in f for k in ("contract", "agreement", "tos", "privacy", "policy", "legal")):
        return "legal_doc"
    return None


def _mime_hint(mime: str) -> AssetKind | None:
    if mime == "application/pdf":
        return "document"        # might be legal, might not — refine below
    if mime.startswith("text/") or mime in {
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    }:
        return "document"
    return None


def _is_likely_logo_by_image(width: int, height: int, has_alpha: bool) -> bool:
    """
    Logos are usually:
      - small-ish (under ~1024px on either axis)
      - close to square or wide-short, NOT tall portraits
      - usually have transparency
    """
    if not has_alpha:
        return False
    aspect = width / max(height, 1)
    if max(width, height) > 1500:
        return False
    if aspect < 0.6 or aspect > 4.0:
        return False
    return True


# ---------------------------------------------------------------------
# Vision fallback — only when heuristics are inconclusive
# ---------------------------------------------------------------------

_VISION_PROMPT = """Classify this image as ONE of:
- logo (a brand mark, monogram, or wordmark with transparent or solid bg)
- hero_image (lifestyle/scene photo suitable for a website hero banner)
- profile_image (a single person, headshot or social-style portrait)
- team_photo (multiple people)
- product_photo (a product on plain or styled bg)
- other

Reply with just the single word, no punctuation."""


async def _vision_classify(image_bytes: bytes, mime: str) -> AssetKind:
    b64 = base64.b64encode(image_bytes).decode()
    resp = _client.messages.create(
        model=MODEL_FAST,
        max_tokens=10,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": mime,
                            "data": b64,
                        },
                    },
                    {"type": "text", "text": _VISION_PROMPT},
                ],
            }
        ],
    )
    label = resp.content[0].text.strip().lower()
    valid = {"logo", "hero_image", "profile_image", "team_photo", "product_photo", "other"}
    return label if label in valid else "other"   # type: ignore[return-value]


# ---------------------------------------------------------------------
# Public entrypoint
# ---------------------------------------------------------------------

async def classify_upload(
    *,
    filename: str,
    mime_type: str,
    width: int | None = None,
    height: int | None = None,
    has_alpha: bool | None = None,
    image_bytes: bytes | None = None,
    surface_id: str,
    user_provided_label: str | None = None,
    surface_field_hint: str | None = None,
) -> ClassificationResult:
    """
    Returns the best-guess kind and the suggested field path on the
    target surface. If `needs_user_confirmation` is True, the frontend
    should ask the customer where to attach it.
    """
    # 1. User explicitly said what it is — trust them
    if user_provided_label:
        return ClassificationResult(
            kind=_normalize_label(user_provided_label),
            confidence=1.0,
            suggested_field_path=_field_path_for(surface_id, _normalize_label(user_provided_label)),
            needs_user_confirmation=False,
        )

    # 2. They dropped on a specific slot
    if surface_field_hint:
        return ClassificationResult(
            kind=_kind_from_field(surface_field_hint),
            confidence=1.0,
            suggested_field_path=surface_field_hint,
            needs_user_confirmation=False,
        )

    # 3. Heuristic layer
    name_kind = _filename_hint(filename)
    mime_kind = _mime_hint(mime_type)

    if name_kind:
        return ClassificationResult(
            kind=name_kind,
            confidence=0.85,
            suggested_field_path=_field_path_for(surface_id, name_kind),
            needs_user_confirmation=False,
        )

    if mime_type == "application/pdf":
        # PDFs default to "document"; legal hint already caught above
        return ClassificationResult(
            kind="document",
            confidence=0.7,
            suggested_field_path=None,   # docs don't auto-attach to a field
            needs_user_confirmation=True,
        )

    # 4. Image with strong logo signal
    if mime_type.startswith("image/") and width and height and has_alpha is not None:
        if _is_likely_logo_by_image(width, height, has_alpha):
            return ClassificationResult(
                kind="logo",
                confidence=0.75,
                suggested_field_path=_field_path_for(surface_id, "logo"),
                needs_user_confirmation=False,
            )

    # 5. Vision fallback for ambiguous images
    if mime_type.startswith("image/") and image_bytes:
        kind = await _vision_classify(image_bytes, mime_type)
        return ClassificationResult(
            kind=kind,
            confidence=0.65,
            suggested_field_path=_field_path_for(surface_id, kind),
            needs_user_confirmation=(kind == "other"),
        )

    return ClassificationResult(
        kind="other",
        confidence=0.0,
        suggested_field_path=None,
        needs_user_confirmation=True,
    )


# ---------------------------------------------------------------------
# Mappings: kind → field path on each surface
# ---------------------------------------------------------------------

_KIND_TO_PATH: dict[str, dict[str, str]] = {
    "brand_portfolio": {
        "logo": "/assets/logo",
        "profile_image": "/assets/profile_image",
    },
    "website": {
        "logo": "/theme/logo",
        "hero_image": "/hero/image",
        "team_photo": "/sections/team/image",
        "product_photo": "/sections/products/image",
    },
    "social_brand_launcher": {
        "logo": "/profile_image",
        "profile_image": "/profile_image",
    },
    "voice_agent_prompt": {},
}


def _field_path_for(surface_id: str, kind: AssetKind) -> str | None:
    return _KIND_TO_PATH.get(surface_id, {}).get(kind)


def _kind_from_field(path: str) -> AssetKind:
    if "logo" in path:
        return "logo"
    if "hero" in path:
        return "hero_image"
    if "profile" in path or "avatar" in path:
        return "profile_image"
    if "team" in path:
        return "team_photo"
    return "other"


def _normalize_label(label: str) -> AssetKind:
    l = label.lower().strip()
    mapping = {
        "logo": "logo", "brand mark": "logo",
        "hero": "hero_image", "banner": "hero_image", "cover": "hero_image",
        "headshot": "profile_image", "avatar": "profile_image", "portrait": "profile_image",
        "team": "team_photo", "staff": "team_photo",
        "product": "product_photo",
        "contract": "legal_doc", "agreement": "legal_doc",
        "document": "document", "doc": "document", "pdf": "document",
    }
    for k, v in mapping.items():
        if k in l:
            return v   # type: ignore[return-value]
    return "other"
