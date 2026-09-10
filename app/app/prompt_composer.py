"""
Structural source of truth for the two non-negotiable, agent-wide prompt
blocks (PROOF OF WORK and CONVERSATION DISCIPLINE). Every caller that sends
an agent's system prompt to an LLM must go through compose_system_prompt()
here -- never read `ai_employees.system_prompt` or
`config->>'proof_of_work_block'` / `config->>'conversation_discipline_block'`
directly and assume either block is present.

Why this exists (2026-09-09 fix): the original sweeps (20260905210001,
20260905220001) had two different storage paths for these blocks -- baked
directly into `system_prompt` text for the 8 agents that had real prompts,
staged as a separate `config` copy for the other 27 -- and no single place
actually guaranteed both were present for both PROOF OF WORK (Eden
excepted) and CONVERSATION DISCIPLINE (Eden included) at the moment a
prompt is actually sent to an LLM. Composing structurally in code closes
that gap once, here, instead of re-auditing N storage locations.

The `config->>'*_block'` values and the text already appended into
`system_prompt` for the 8 real-prompt agents are left in place (harmless
dead data now that nothing reads them) rather than migrated out -- see
DECISIONS.md 2026-09-09.
"""
from typing import Optional

EDEN_ID = "eden-headspace"

PROOF_OF_WORK_BLOCK = (
    "PROOF OF WORK (non-negotiable):\n"
    "1. You never report a task complete based on your own belief that you did it.\n"
    "   Completion is a receipt: an external id, a status code, a row count, or a\n"
    "   confirmed webhook. No receipt means not done.\n"
    "2. Report exact numbers, always as completed-of-intended. \"Sent 387 of 400 --\n"
    "   13 had invalid addresses\" is a good report. \"Campaign sent!\" is a bad one.\n"
    "3. Partial completion is reported as partial, immediately, with the reason and\n"
    "   what you need to finish. Never round a partial up to a success.\n"
    "4. If a task turns out to be impossible, say so explicitly and name what\n"
    "   blocked it. An honest abandon beats a quiet drop every time.\n"
    "5. Re-measure every number at report time. Do not carry a count from earlier\n"
    "   in the task into your summary -- read it fresh.\n"
    "6. If a required connection is missing or a call failed, name the service and\n"
    "   give the Connections Hub link. Never silently skip and report success."
)

CONVERSATION_DISCIPLINE_BLOCK = (
    "CONVERSATION DISCIPLINE (non-negotiable):\n"
    "1. Before replying, read OPEN ITEMS. If any exist, decide whether this message\n"
    "   answers one. If it does not, you are not done until you have restated it.\n"
    "2. A greeting, \"ok\", \"thanks\", or small talk is never an answer. Reply in kind\n"
    "   briefly, then put the open question back in one sentence with the choices.\n"
    "   Example -- open item: \"price the repair now or come back Thursday?\"\n"
    "   User: \"hi\"  ->  You: \"Hi John. Still need your call on the Central gutter:\n"
    "   price the fascia repair while the crew's up there, or come back Thursday?\"\n"
    "3. \"Copy that\" / \"Got it\" / \"Understood\" are only for actual instructions.\n"
    "4. If a message could be an answer or could be an aside, ask one clarifying\n"
    "   question that includes the choices. Never guess which one they meant.\n"
    "5. When a new topic arrives mid-decision, handle it and then restate the\n"
    "   open item. Nothing gets dropped silently.\n"
    "6. When you resolve an open item, say what you understood in one line before\n"
    "   acting: \"Pricing it now -- I'll have a number in twenty minutes.\"\n"
    "7. If a human teammate is the one being asked (not you), never answer on their\n"
    "   behalf. Say the message was delivered and when they're likely to see it."
)

_BLOCK_HEADERS = (
    "PROOF OF WORK (non-negotiable):",
    "CONVERSATION DISCIPLINE (non-negotiable):",
)


def _strip_known_blocks(text: str) -> str:
    """Defensive: cut a stored prompt off at the first occurrence of either
    block's header. Without this, the 8 agents whose system_prompt already
    has PROOF OF WORK (and, for those touched by the second sweep,
    CONVERSATION DISCIPLINE too) baked into its text would get that block
    twice once this module also injects it structurally."""
    if not text:
        return text
    cut_at = len(text)
    for header in _BLOCK_HEADERS:
        idx = text.find(header)
        if idx != -1:
            cut_at = min(cut_at, idx)
    return text[:cut_at].rstrip()


def base_prompt(agent: dict) -> str:
    """The agent's own persona/role text -- never the source of truth for
    PROOF OF WORK or CONVERSATION DISCIPLINE, even if a stored system_prompt
    happens to contain that text from an earlier sweep."""
    prompt = agent.get("system_prompt")
    if prompt:
        return _strip_known_blocks(prompt)
    role = agent.get("role") or agent.get("id")
    dept = agent.get("department_label") or agent.get("department") or ""
    return f"You are {agent.get('biblical_name', agent['id'])}, {role} in {dept}."


def _open_items_block(open_items: list[dict]) -> Optional[str]:
    open_only = [i for i in open_items if not i.get("resolved_at")]
    if not open_only:
        return None
    lines = ["OPEN ITEMS (unresolved -- read before replying, per CONVERSATION DISCIPLINE):"]
    for item in open_only:
        choices = item.get("choices") or []
        choice_str = f" Choices: {', '.join(choices)}." if choices else ""
        lines.append(f"- [{item['id']}] {item['question']}{choice_str}")
    return "\n".join(lines)


def compose_system_prompt(agent: dict, open_items: Optional[list[dict]] = None) -> str:
    """The one place every agent's full system prompt gets assembled, for
    every caller (Switchboard messages, ops-audit smoke calls, anything
    else that talks to an agent). Rule (05_CONVERSATION_DISCIPLINE.md §5,
    plus the 2026-09-09 fix): every active agent gets CONVERSATION
    DISCIPLINE. Every active agent EXCEPT Eden also gets PROOF OF WORK --
    Eden's sessions stay isolated, no receipt/verification language crosses
    her boundary (eden_sessions privacy rule). Open items, when given, are
    injected above the rest so context pressure can't drop them (§2)."""
    parts = [base_prompt(agent)]
    if agent.get("id") != EDEN_ID:
        parts.append(PROOF_OF_WORK_BLOCK)
    parts.append(CONVERSATION_DISCIPLINE_BLOCK)
    open_block = _open_items_block(open_items or [])
    if open_block:
        parts.append(open_block)
    return "\n\n".join(parts)
