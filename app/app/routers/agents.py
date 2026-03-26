from fastapi import APIRouter, Query
from typing import Optional
from app.db import get_client

router = APIRouter(prefix="/agents", tags=["agents"])


@router.get("")
def list_agents(
    agent_type: Optional[str] = Query(None, alias="type"),
    platform: Optional[str] = Query(None),
    limit: int = Query(20, le=100),
):
    client = get_client()
    query = client.schema("foundation").table("agents").select("*").eq("is_active", True)

    if agent_type:
        query = query.eq("agent_type", agent_type)
    if platform:
        query = query.eq("platform", platform)

    return query.limit(limit).execute().data
