"""Brands router — brand profile CRUD for foundation.brand_profiles"""

from fastapi import APIRouter, HTTPException
from typing import List
from models.schemas import BrandProfileCreate
from db.client import get_db

router = APIRouter()


@router.get("/", response_model=List[dict])
async def list_brands():
    db = get_db()
    result = db.schema("foundation").table("brand_profiles").select("*").execute()
    return result.data


@router.get("/{business_slug}", response_model=dict)
async def get_brand(business_slug: str):
    db = get_db()
    result = db.schema("foundation").table("brand_profiles").select("*").eq("business_slug", business_slug).single().execute()
    if not result.data:
        raise HTTPException(status_code=404, detail=f"Brand '{business_slug}' not found")
    return result.data


@router.post("/", response_model=dict, status_code=201)
async def create_brand(brand: BrandProfileCreate):
    db = get_db()
    result = db.schema("foundation").table("brand_profiles").insert(brand.model_dump()).execute()
    return result.data[0]


@router.put("/{business_slug}", response_model=dict)
async def update_brand(business_slug: str, brand: BrandProfileCreate):
    db = get_db()
    result = db.schema("foundation").table("brand_profiles").update(brand.model_dump()).eq("business_slug", business_slug).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail=f"Brand '{business_slug}' not found")
    return result.data[0]
