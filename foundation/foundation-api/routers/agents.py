"""Agents router — CRUD for foundation.agents"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from models.schemas import AgentCreate
from db.client import get_db

router = APIRouter()


@router.get("/", response_model=List[dict])
async def list_agents(
    agent_type: Optional[str] = None,
    platform: Optional[str] = None,
    industry: Optional[str] = None,
    limit: int = Query(default=50, le=200),
):
    db = get_db()
    query = db.schema("foundation").table("agents").select("*").eq("is_active", True)

    if agent_type:
        query = query.eq("agent_type", agent_type)
    if platform:
        query = query.contains("platforms", [platform])
    if industry:
        query = query.contains("industries", [industry])

    result = query.limit(limit).execute()
    return result.data


@router.get("/{slug}", response_model=dict)
async def get_agent(slug: str):
    db = get_db()
    result = db.schema("foundation").table("agents").select("*").eq("slug", slug).single().execute()
    if not result.data:
        raise HTTPException(status_code=404, detail=f"Agent '{slug}' not found")
    return result.data


@router.post("/", response_model=dict, status_code=201)
async def create_agent(agent: AgentCreate):
    db = get_db()
    result = db.schema("foundation").table("agents").insert(agent.model_dump()).execute()
    return result.data[0]


@router.put("/{slug}", response_model=dict)
async def update_agent(slug: str, agent: AgentCreate):
    db = get_db()
    result = db.schema("foundation").table("agents").update(agent.model_dump()).eq("slug", slug).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail=f"Agent '{slug}' not found")
    return result.data[0]


@router.delete("/{slug}")
async def delete_agent(slug: str):
    db = get_db()
    db.schema("foundation").table("agents").update({"is_active": False}).eq("slug", slug).execute()
    return {"message": f"Agent '{slug}' deactivated"}
