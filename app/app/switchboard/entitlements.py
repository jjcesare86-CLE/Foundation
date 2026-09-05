"""
Entitlement mask: which agents a workspace has unlocked. See the migration
note on client_agent_entitlements — this table is Foundation's own, seeded
manually until a real pricing/billing engine writes to it.
"""
from app.database import supabase


def get_entitlement_mask(client_id: str) -> dict[str, bool]:
    """{agent_slug: unlocked} for every active agent. Missing rows default
    to locked — an agent is only unlocked by an explicit row, never by
    absence, so a new agent release is locked-by-default (matches the
    'perpetual merchandising shelf' framing in §2.2: new agents show up
    grayed until sold, not silently free)."""
    agents = (
        supabase.schema("foundation").table("ai_employees")
        .select("id").eq("is_active", True).execute().data
    )
    rows = (
        supabase.schema("foundation").table("client_agent_entitlements")
        .select("agent_slug,unlocked").eq("client_id", client_id).execute().data
    )
    unlocked = {r["agent_slug"]: r["unlocked"] for r in rows}
    return {a["id"]: unlocked.get(a["id"], False) for a in agents}


def is_unlocked(client_id: str, agent_slug: str) -> bool:
    row = (
        supabase.schema("foundation").table("client_agent_entitlements")
        .select("unlocked").eq("client_id", client_id).eq("agent_slug", agent_slug)
        .execute().data
    )
    return bool(row and row[0]["unlocked"])
