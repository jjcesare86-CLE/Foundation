"""
Shared typed action library — the approval-inbox pattern every agent reuses.

An "action type" is a handler function: (draft: dict, payload: dict, demo: bool) -> dict.
`demo` tells the handler whether a required credential is missing (or demo
mode is forced globally) — the handler decides what that means for itself:
typically "skip the real HTTP call, still do safe internal bookkeeping,
return a result tagged accordingly." The executor never calls a handler's
real-API branch without required_env satisfied, but always calls the
handler itself, so bookkeeping (e.g. marking a review 'posted') isn't
skipped just because the external call was mocked. Handlers should not
raise for expected failure modes (catch and return {"ok": False, "detail":
...} instead); executor.py wraps everything else in try/except as a last
resort.

register_action_type() lets any module (Rahab's, Zacchaeus's, Silas's,
GABRIEL's when reactivated) add a new action type without editing this file.
"""
import os
from typing import Callable, Optional

ActionHandler = Callable[[dict, dict, bool], dict]

ACTION_REGISTRY: dict[str, ActionHandler] = {}
REQUIRED_ENV: dict[str, list[str]] = {}


def register_action_type(action_type: str, handler: ActionHandler, required_env: Optional[list[str]] = None) -> None:
    ACTION_REGISTRY[action_type] = handler
    REQUIRED_ENV[action_type] = required_env or []


def is_demo_mode(action_type: str) -> bool:
    """
    True if this action type should simulate rather than call a real
    external API — either the operator forced demo mode globally, or a
    credential this action type needs is missing. Fail-closed toward
    simulation, matching connection_broker's pattern: never guess a real
    call is safe.
    """
    if os.getenv("ACTION_LIBRARY_DEMO_MODE", "").lower() in ("1", "true", "yes"):
        return True
    for var in REQUIRED_ENV.get(action_type, []):
        if not os.getenv(var):
            return True
    return False
