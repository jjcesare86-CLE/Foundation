from fastapi import APIRouter, HTTPException
from app.db import get_client

router = APIRouter(prefix="/brand", tags=["brand"])


@router.get("/{business_slug}")
def get_brand(business_slug: str):
    client = get_client()
    result = (
        client.schema("foundation")
        .table("brand_profiles")
        .select("*")
        .eq("business_slug", business_slug)
        .maybe_single()
        .execute()
    )
    if not result.data:
        raise HTTPException(status_code=404, detail="Brand profile not found")
    return result.data
