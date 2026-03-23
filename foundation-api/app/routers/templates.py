from fastapi import APIRouter, Query
from typing import Optional
from app.db import get_client

router = APIRouter(prefix="/templates", tags=["templates"])


@router.get("")
def list_templates(
    template_type: Optional[str] = Query(None, alias="type"),
    industry: Optional[str] = Query(None),
    limit: int = Query(20, le=100),
):
    client = get_client()
    query = client.schema("foundation").table("templates").select("*")

    if template_type:
        query = query.eq("template_type", template_type)
    if industry:
        query = query.eq("industry", industry)

    return query.limit(limit).execute().data
