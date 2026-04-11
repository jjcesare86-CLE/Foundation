"""
foundation_agents.py

Single source of truth for the 16 named AI Employee voice agents.
The frontend useAgents() hook fetches this list to render agent cards.
gemini_voice_proxy.py imports AGENT_VOICES from here.
"""

from fastapi import APIRouter

router = APIRouter(prefix="/voice-agents", tags=["AI Employees"])

# Canonical AI Employee roster. Voice names match Gemini Live prebuilt voices:
# Puck, Charon, Kore, Fenrir, Aoede.
AGENTS: list[dict] = [
    # ── STRATEGY ────────────────────────────────────────────
    {"name": "John",    "role": "General Assistant",       "department": "Strategy",   "voice": "Charon", "avatar": "J"},
    {"name": "Paul",    "role": "Mindset Coach",           "department": "Strategy",   "voice": "Puck",   "avatar": "P"},
    {"name": "Mary",    "role": "Business Strategist",     "department": "Strategy",   "voice": "Aoede",  "avatar": "M"},
    {"name": "Luke",    "role": "Legal Assistant",         "department": "Strategy",   "voice": "Fenrir", "avatar": "L"},

    # ── SALES ───────────────────────────────────────────────
    {"name": "Deborah", "role": "Lead Generator",          "department": "Sales",      "voice": "Kore",   "avatar": "D"},
    {"name": "Nathan",  "role": "Outreach Specialist",     "department": "Sales",      "voice": "Charon", "avatar": "N"},
    {"name": "Anna",    "role": "Social Media Manager",    "department": "Sales",      "voice": "Aoede",  "avatar": "A"},
    {"name": "Joseph",  "role": "Sales Coach",             "department": "Sales",      "voice": "Puck",   "avatar": "J"},

    # ── MARKETING ───────────────────────────────────────────
    {"name": "Naomi",   "role": "Marketing Strategist",    "department": "Marketing",  "voice": "Kore",   "avatar": "N"},
    {"name": "Lydia",   "role": "Marketing Strategist",    "department": "Marketing",  "voice": "Aoede",  "avatar": "L"},
    {"name": "Martha",  "role": "Copywriter",              "department": "Marketing",  "voice": "Kore",   "avatar": "M"},
    {"name": "Leah",    "role": "Content Creator",         "department": "Marketing",  "voice": "Aoede",  "avatar": "L"},

    # ── OPERATIONS ──────────────────────────────────────────
    {"name": "Delilah", "role": "Sales Development Rep",   "department": "Operations", "voice": "Kore",   "avatar": "D"},
    {"name": "Hannah",  "role": "Hiring Assistant",        "department": "Operations", "voice": "Aoede",  "avatar": "H"},
    {"name": "Peter",   "role": "Systems Architect",       "department": "Operations", "voice": "Charon", "avatar": "P"},
    {"name": "Elijah",  "role": "Chief Financial Officer", "department": "Operations", "voice": "Charon", "avatar": "E"},
]

# Lookup helpers used by gemini_voice_proxy.py
AGENTS_BY_NAME: dict[str, dict] = {a["name"]: a for a in AGENTS}
AGENT_VOICES: dict[str, str] = {a["name"]: a["voice"] for a in AGENTS}


@router.get("")
def list_voice_agents():
    """Return the canonical list of all 16 AI Employees."""
    return AGENTS


@router.get("/{name}")
def get_voice_agent(name: str):
    """Return a single AI Employee by name."""
    return AGENTS_BY_NAME.get(name) or {"error": "not found"}
