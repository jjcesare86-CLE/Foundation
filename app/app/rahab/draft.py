"""Haiku draft generation for review responses, using the tone matrix from Rahab's system prompt."""
from app.llm_router import llm_call, TaskTier

DRAFT_SYSTEM = """You are Rahab, drafting a public review response for {business_name}.

TONE MATRIX:
- 4-5 stars: specific gratitude (reference a detail from their review), invite back.
- 3 stars: thank + acknowledge the miss + one concrete improvement note.
- 1-2 stars: acknowledge, apologize for the experience (not admit fault on disputed
  facts), take it offline: "{owner_first} would like to make this right — please call
  {business_phone}."

Never argue. Never admit fault on disputed facts. Never promise refunds unless told to.
Write 2-4 sentences, warm and specific, sounding like a thoughtful owner, not a PR bot.
Output ONLY the response text — no preamble, no quotes around it."""


def draft_review_response(
    review_text: str,
    rating: int,
    reviewer_name: str,
    business_name: str,
    owner_first: str,
    business_phone: str,
) -> str:
    system = DRAFT_SYSTEM.format(business_name=business_name, owner_first=owner_first, business_phone=business_phone)
    user_msg = f"Reviewer: {reviewer_name or 'a customer'}\nRating: {rating} stars\nReview: {review_text or '(no text)'}"
    return llm_call(
        messages=[{"role": "user", "content": user_msg}],
        tier=TaskTier.FAST,
        system=system,
        max_tokens=300,
        project="foundation",
        agent_name="rahab-reputation",
        task_type="rahab:draft_review_response",
    ).strip()
