"""Skills router — CRUD + semantic search for foundation.skills"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from models.schemas import SkillCreate, SkillResponse
from db.client import get_db

router = APIRouter()


@router.get("/", response_model=List[dict])
async def list_skills(
    category: Optional[str] = None,
    industry: Optional[str] = None,
    platform: Optional[str] = None,
    limit: int = Query(default=50, le=200),
):
    """List skills with optional filters."""
    db = get_db()
    query = db.schema("foundation").table("skills").select("*").eq("is_active", True)

    if category:
        query = query.eq("category", category)
    if industry:
        query = query.contains("industries", [industry])
    if platform:
        query = query.contains("platforms", [platform])

    result = query.limit(limit).execute()
    return result.data


@router.get("/{slug}", response_model=dict)
async def get_skill(slug: str):
    """Get a single skill by slug."""
    db = get_db()
    result = db.schema("foundation").table("skills").select("*").eq("slug", slug).single().execute()
    if not result.data:
        raise HTTPException(status_code=404, detail=f"Skill '{slug}' not found")
    return result.data


@router.post("/", response_model=dict, status_code=201)
async def create_skill(skill: SkillCreate):
    """Create a new skill."""
    db = get_db()
    result = db.schema("foundation").table("skills").insert(skill.model_dump()).execute()
    return result.data[0]


@router.put("/{slug}", response_model=dict)
async def update_skill(slug: str, skill: SkillCreate):
    """Update an existing skill."""
    db = get_db()
    result = db.schema("foundation").table("skills").update(skill.model_dump()).eq("slug", slug).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail=f"Skill '{slug}' not found")
    return result.data[0]


@router.delete("/{slug}")
async def delete_skill(slug: str):
    """Soft-delete a skill (sets is_active=False)."""
    db = get_db()
    db.schema("foundation").table("skills").update({"is_active": False}).eq("slug", slug).execute()
    return {"message": f"Skill '{slug}' deactivated"}
