"""Clients router — client profile management"""

import uuid
from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from models.schemas import ClientProfileCreate
from db.client import get_db

router = APIRouter()


@router.get("/", response_model=List[dict])
async def list_clients(
    source_platform: Optional[str] = None,
    onboarding_status: Optional[str] = None,
    industry: Optional[str] = None,
    limit: int = Query(default=50, le=200),
):
    db = get_db()
    query = db.schema("foundation").table("client_profiles").select("*")
    if source_platform:
        query = query.eq("source_platform", source_platform)
    if onboarding_status:
        query = query.eq("onboarding_status", onboarding_status)
    if industry:
        query = query.eq("industry", industry)
    result = query.limit(limit).execute()
    return result.data


@router.get("/{client_id}", response_model=dict)
async def get_client(client_id: str):
    db = get_db()
    result = db.schema("foundation").table("client_profiles").select("*").eq("client_id", client_id).single().execute()
    if not result.data:
        raise HTTPException(status_code=404, detail=f"Client '{client_id}' not found")
    return result.data


@router.post("/", response_model=dict, status_code=201)
async def create_client(client: ClientProfileCreate):
    db = get_db()
    data = client.model_dump()
    # Auto-generate client_id if not provided
    if not data.get("client_id"):
        data["client_id"] = f"CLT-{str(uuid.uuid4())[:8].upper()}"
    # Auto-generate business_slug if not provided
    if not data.get("business_slug"):
        data["business_slug"] = data["business_name"].lower().replace(" ", "-")
    result = db.schema("foundation").table("client_profiles").insert(data).execute()
    return result.data[0]


@router.patch("/{client_id}", response_model=dict)
async def update_client(client_id: str, updates: dict):
    """Partial update — pass only the fields you want to change."""
    db = get_db()
    result = db.schema("foundation").table("client_profiles").update(updates).eq("client_id", client_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail=f"Client '{client_id}' not found")
    return result.data[0]


@router.patch("/{client_id}/onboarding")
async def update_onboarding(client_id: str, status: str, completed_task: Optional[str] = None):
    """Update onboarding status and optionally mark a task complete."""
    db = get_db()
    updates = {"onboarding_status": status}
    if completed_task:
        # Append to completed_tasks array
        client = db.schema("foundation").table("client_profiles").select("completed_tasks").eq("client_id", client_id).single().execute()
        tasks = client.data.get("completed_tasks", [])
        if completed_task not in tasks:
            tasks.append(completed_task)
        updates["completed_tasks"] = tasks
    result = db.schema("foundation").table("client_profiles").update(updates).eq("client_id", client_id).execute()
    return result.data[0]
