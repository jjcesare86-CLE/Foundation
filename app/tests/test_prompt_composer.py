"""
Unit test for app.prompt_composer -- the structural single source of truth
for the PROOF OF WORK and CONVERSATION DISCIPLINE blocks (2026-09-09 fix).

Requires live Supabase credentials (SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY,
via .env or the environment) because it composes against the real roster,
not synthetic fixtures -- the whole point is proving every currently-active
agent row gets the right blocks, including the 8 whose system_prompt already
had PROOF OF WORK text baked in from an earlier sweep (the exact case that
would silently double-inject without the defensive stripping in
prompt_composer._strip_known_blocks). Skips cleanly if those creds aren't
configured in this environment, rather than failing confusingly.
"""
import os

import pytest

if not os.getenv("SUPABASE_URL") or not os.getenv("SUPABASE_SERVICE_ROLE_KEY"):
    pytest.skip(
        "SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY not set -- this test composes "
        "against the live roster and needs real credentials, see .env.example",
        allow_module_level=True,
    )

from app.database import supabase
from app.prompt_composer import (
    CONVERSATION_DISCIPLINE_BLOCK, EDEN_ID, PROOF_OF_WORK_BLOCK, compose_system_prompt,
)


@pytest.fixture(scope="module")
def active_agents():
    return (
        supabase.schema("foundation").table("ai_employees")
        .select("*").eq("is_active", True).execute().data
    )


def test_exactly_35_active_agents(active_agents):
    assert len(active_agents) == 35, (
        f"expected 35 active agents (Batches 1-3 shipped), got {len(active_agents)} -- "
        "roster count changed, update this test if that's expected"
    )


def test_every_agent_gets_conversation_discipline(active_agents):
    for agent in active_agents:
        composed = compose_system_prompt(agent)
        assert CONVERSATION_DISCIPLINE_BLOCK in composed, (
            f"{agent['id']}: missing CONVERSATION DISCIPLINE block"
        )
        # Exactly once -- guards against double-injection for the agents
        # whose stored system_prompt already had this text appended by the
        # original sweep (20260905220001).
        assert composed.count("CONVERSATION DISCIPLINE (non-negotiable):") == 1, (
            f"{agent['id']}: CONVERSATION DISCIPLINE block appears more than once"
        )


def test_every_agent_except_eden_gets_proof_of_work(active_agents):
    for agent in active_agents:
        composed = compose_system_prompt(agent)
        if agent["id"] == EDEN_ID:
            assert PROOF_OF_WORK_BLOCK not in composed, "Eden must never get PROOF OF WORK"
            assert "PROOF OF WORK (non-negotiable):" not in composed
        else:
            assert PROOF_OF_WORK_BLOCK in composed, f"{agent['id']}: missing PROOF OF WORK block"
            assert composed.count("PROOF OF WORK (non-negotiable):") == 1, (
                f"{agent['id']}: PROOF OF WORK block appears more than once "
                "(check _strip_known_blocks against its stored system_prompt)"
            )


def test_eden_present_and_is_the_only_exception(active_agents):
    ids = [a["id"] for a in active_agents]
    assert EDEN_ID in ids, "Eden must be in the active roster for this test to mean anything"


def test_open_items_included_in_system_prompt_unresolved_only(active_agents):
    # 05_CONVERSATION_DISCIPLINE.md §2: open items live in the system prompt
    # (never subject to message-history trimming), not the message array --
    # this checks they're present at all and that resolved items drop off,
    # not their exact position within the system prompt text.
    agent = next(a for a in active_agents if a["id"] != EDEN_ID)
    open_items = [
        {"id": "oi1", "question": "price now or Thursday?", "choices": ["price now", "Thursday"], "resolved_at": None},
        {"id": "oi2", "question": "already answered", "choices": [], "resolved_at": "2026-09-01T00:00:00Z"},
    ]
    composed = compose_system_prompt(agent, open_items)
    assert "OPEN ITEMS" in composed
    assert "price now or Thursday?" in composed
    assert "already answered" not in composed  # resolved items are not restated
    assert compose_system_prompt(agent, []) == compose_system_prompt(agent, None)  # no open items -> identical, no stray block
