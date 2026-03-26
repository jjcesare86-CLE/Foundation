from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from app.db import get_admin_client

router = APIRouter(prefix="/client-profile", tags=["clients"])


class ClientProfileCreate(BaseModel):
    business_name: str
    contact_name: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    industry: Optional[str] = None
    website: Optional[str] = None
    onboarding_platform: Optional[str] = None
    services: list[str] = []
    notes: Optional[str] = None
    onboarding_data: dict = {}


@router.post("")
def create_client_profile(profile: ClientProfileCreate):
    client = get_admin_client()
    result = (
        client.schema("foundation")
        .table("client_profiles")
        .insert(profile.model_dump())
        .execute()
    )
    return result.data[0]
