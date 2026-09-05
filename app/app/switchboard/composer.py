"""
Prompt composer for Switchboard messages: agent system prompt + open items
(injected ABOVE the recent-messages window per 05_CONVERSATION_DISCIPLINE.md
§2, so context pressure can't drop them) + thread memory window -> llm_router.

Thread memory window is last-30-messages only for this phase, not the full
"+ rolling summary" from SWITCHBOARD_BUILD.md §3.4 — rolling summarization
is its own piece of work (a scheduled compaction job), trimmed from Phase 1
same as Batch 2/3's follow-on pipelines were trimmed: flagged, not silently
dropped. Thirty messages is a real, working memory window on its own.
"""
import json
from typing import Optional

from app.database import supabase
from app.llm_router import llm_call, TaskTier
from app.ops.ops_audit import TIER_TO_TASKTIER

THREAD_WINDOW = 30


def _agent_prompt_block(agent: dict) -> str:
    prompt = agent.get("system_prompt")
    if prompt:
        return prompt
    # No real prompt yet (27 of 35 agents) -- compose a minimal honest one
    # from house fields rather than pretending a real persona exists.
    role = agent.get("role") or agent.get("id")
    dept = agent.get("department_label") or agent.get("department") or ""
    block = f"You are {agent.get('biblical_name', agent['id'])}, {role} in {dept}."
    staged = (agent.get("config") or {}).get("proof_of_work_block")
    if staged:
        block += "\n\n" + staged
    staged_cd = (agent.get("config") or {}).get("conversation_discipline_block")
    if staged_cd:
        block += "\n\n" + staged_cd
    return block


def _open_items_block(open_items: list[dict]) -> str:
    open_only = [i for i in open_items if not i.get("resolved_at")]
    if not open_only:
        return ""
    lines = ["OPEN ITEMS (unresolved -- read before replying, per CONVERSATION DISCIPLINE):"]
    for item in open_only:
        choices = item.get("choices") or []
        choice_str = f" Choices: {', '.join(choices)}." if choices else ""
        lines.append(f"- [{item['id']}] {item['question']}{choice_str}")
    return "\n".join(lines)


def compose_system_prompt(agent: dict, open_items: list[dict]) -> str:
    parts = [_agent_prompt_block(agent)]
    open_block = _open_items_block(open_items)
    if open_block:
        parts.append(open_block)
    return "\n\n".join(parts)


def _history_to_messages(history: list[dict]) -> list[dict]:
    messages = []
    for m in history[-THREAD_WINDOW:]:
        if m["sender"] == "user":
            messages.append({"role": "user", "content": m["body"] or ""})
        elif m["sender"] == "agent":
            messages.append({"role": "assistant", "content": m["body"] or ""})
        # 'system' rows (handoff notes, call summaries) are context, not
        # turns -- surfaced via the system prompt if ever needed, not injected
        # as a fake user/assistant turn.
    return messages


def generate_reply(agent: dict, thread: dict, history: list[dict], user_text: str) -> str:
    tier = TIER_TO_TASKTIER.get(agent.get("model_tier"), TaskTier.STANDARD)
    system = compose_system_prompt(agent, thread.get("open_items") or [])
    messages = _history_to_messages(history) + [{"role": "user", "content": user_text}]
    return llm_call(
        messages=messages,
        tier=tier,
        system=system,
        max_tokens=600,
        project="foundation",
        agent_name=agent["id"],
        task_type="switchboard:message",
    )
