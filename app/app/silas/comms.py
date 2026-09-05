"""Haiku-drafted customer texts: night-before confirmation, dispatch ETA."""
from app.llm_router import llm_call, TaskTier

COMMS_SYSTEM = """You are Silas, texting a customer for {business_name}. Calm, warm, brief
-- one to two sentences, no jargon. ETAs are always a window, never an exact time."""


def draft_eta_text(job_type: str, eta_window: str, business_name: str) -> str:
    user_msg = f"Draft an 'on our way' text. Job: {job_type}. ETA window: {eta_window}."
    return llm_call(
        messages=[{"role": "user", "content": user_msg}],
        tier=TaskTier.FAST,
        system=COMMS_SYSTEM.format(business_name=business_name),
        max_tokens=150,
        project="foundation",
        agent_name="silas-dispatch",
        task_type="silas:eta_text",
    ).strip()


def draft_confirmation_text(job_type: str, date_str: str, business_name: str) -> str:
    user_msg = f"Draft a night-before confirmation text. Job: {job_type}. Date: {date_str}."
    return llm_call(
        messages=[{"role": "user", "content": user_msg}],
        tier=TaskTier.FAST,
        system=COMMS_SYSTEM.format(business_name=business_name),
        max_tokens=150,
        project="foundation",
        agent_name="silas-dispatch",
        task_type="silas:confirmation_text",
    ).strip()
