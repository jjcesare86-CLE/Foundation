"""Registers Silas's action types with the shared action library."""
from app.action_library.registry import register_action_type


def _execute_invoicing_notify(draft: dict, payload: dict, demo: bool) -> dict:
    # Purely informational -- the durable agent_actions row IS the notification
    # (Joanna's invoicing flow queries agent_actions where action_type=
    # 'invoicing_notify' and status='executed'). No external call either way.
    return {"ok": True}


def _execute_approve_reschedule(draft: dict, payload: dict, demo: bool) -> dict:
    """Weather-conflict reschedule, approved by the owner. Messaging the
    affected customer and opening new slot offers is the same GHL-messaging
    gap noted elsewhere (rahab/ghl_client.py) -- bookkeeping (marking which
    jobs got rescheduled) always happens; the actual SMS send is mocked in
    demo mode and TODO'd for real mode pending a generic GHL messaging
    helper (today's rahab.ghl_client is review-reply-specific)."""
    if demo:
        return {"ok": True, "would_have": f"message customer about reschedule: {draft.get('proposed_slot', '(unspecified)')}"}
    return {"ok": False, "detail": "live GHL reschedule messaging not implemented yet"}


def register_silas_actions() -> None:
    register_action_type("invoicing_notify", _execute_invoicing_notify)
    register_action_type("approve_reschedule", _execute_approve_reschedule, required_env=["GHL_API_KEY"])
