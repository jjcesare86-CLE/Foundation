from fastapi import APIRouter, Query
from typing import Optional
from app.db import get_client

router = APIRouter(prefix="/skills", tags=["skills"])


@router.get("")
def list_skills(
    category: Optional[str] = Query(None),
    industry: Optional[str] = Query(None),
    limit: int = Query(20, le=100),
):
    client = get_client()
    query = client.schema("foundation").table("skills").select("*")

    if category:
        query = query.eq("category", category)
    if industry:
        query = query.contains("tags", [industry])

    return query.limit(limit).execute().data
