"""
Switchboard message generation: real thread history -> llm_router. The
system prompt itself (agent persona + PROOF OF WORK + CONVERSATION
DISCIPLINE + open items) is built by app.prompt_composer.compose_system_prompt
-- the single source of truth for those two blocks (2026-09-09 fix; see
that module's docstring). This file no longer builds any part of the system
prompt itself, only the thread-history-to-messages conversion.

Thread memory window is last-30-messages only for this phase, not the full
"+ rolling summary" from SWITCHBOARD_BUILD.md §3.4 — rolling summarization
is its own piece of work (a scheduled compaction job), trimmed from Phase 1
same as Batch 2/3's follow-on pipelines were trimmed: flagged, not silently
dropped. Thirty messages is a real, working memory window on its own.
"""
from app.llm_router import llm_call, TaskTier
from app.ops.ops_audit import TIER_TO_TASKTIER
from app.prompt_composer import compose_system_prompt

THREAD_WINDOW = 30


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
