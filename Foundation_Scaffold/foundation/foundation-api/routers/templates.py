"""Templates router"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from models.schemas import TemplateCreate
from db.client import get_db

router = APIRouter()


@router.get("/", response_model=List[dict])
async def list_templates(
    template_type: Optional[str] = None,
    industry: Optional[str] = None,
    platform: Optional[str] = None,
    limit: int = Query(default=50, le=200),
):
    db = get_db()
    query = db.schema("foundation").table("templates").select("*").eq("is_active", True)
    if template_type:
        query = query.eq("template_type", template_type)
    if industry:
        query = query.eq("industry", industry)
    if platform:
        query = query.eq("platform", platform)
    result = query.limit(limit).execute()
    return result.data


@router.get("/{slug}", response_model=dict)
async def get_template(slug: str):
    db = get_db()
    result = db.schema("foundation").table("templates").select("*").eq("slug", slug).single().execute()
    if not result.data:
        raise HTTPException(status_code=404, detail=f"Template '{slug}' not found")
    return result.data


@router.post("/", response_model=dict, status_code=201)
async def create_template(template: TemplateCreate):
    db = get_db()
    result = db.schema("foundation").table("templates").insert(template.model_dump()).execute()
    return result.data[0]
