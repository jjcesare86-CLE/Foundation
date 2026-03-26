"""Pydantic schemas for Foundation API"""

from pydantic import BaseModel, Field
from typing import Optional, List, Any
from uuid import UUID
from datetime import datetime


# ── SKILLS ──────────────────────────────────────────────────
class SkillBase(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    category: str
    subcategory: Optional[str] = None
    prompt_template: Optional[str] = None
    config: dict = {}
    industries: List[str] = []
    platforms: List[str] = []
    version: str = "1.0.0"

class SkillCreate(SkillBase):
    pass

class SkillResponse(SkillBase):
    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True


# ── AGENTS ──────────────────────────────────────────────────
class AgentBase(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    agent_type: str
    system_prompt: Optional[str] = None
    tools: List[Any] = []
    model: str = "claude-sonnet-4-20250514"
    temperature: float = 0.7
    max_tokens: int = 2048
    config: dict = {}
    platforms: List[str] = []
    industries: List[str] = []
    version: str = "1.0.0"

class AgentCreate(AgentBase):
    pass

class AgentResponse(AgentBase):
    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True


# ── BRANDS ──────────────────────────────────────────────────
class BrandProfileBase(BaseModel):
    business_slug: str
    business_name: str
    tagline: Optional[str] = None
    description: Optional[str] = None
    logo_url: Optional[str] = None
    primary_color: Optional[str] = None
    secondary_color: Optional[str] = None
    accent_color: Optional[str] = None
    bg_color: Optional[str] = None
    text_color: Optional[str] = None
    heading_font: Optional[str] = None
    body_font: Optional[str] = None
    tone_keywords: List[str] = []
    voice_style: Optional[str] = None
    avoid_words: List[str] = []
    website_url: Optional[str] = None
    support_email: Optional[str] = None
    phone: Optional[str] = None
    address: dict = {}
    social_links: dict = {}
    mission: Optional[str] = None
    vision: Optional[str] = None
    values: List[str] = []
    target_audience: Optional[str] = None
    usp: Optional[str] = None
    config: dict = {}

class BrandProfileCreate(BrandProfileBase):
    pass

class BrandProfileResponse(BrandProfileBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True


# ── TEMPLATES ───────────────────────────────────────────────
class TemplateBase(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    template_type: str
    industry: Optional[str] = None
    platform: Optional[str] = None
    content: Optional[str] = None
    variables: List[Any] = []
    config: dict = {}
    tags: List[str] = []

class TemplateCreate(TemplateBase):
    pass

class TemplateResponse(TemplateBase):
    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True


# ── CLIENT PROFILES ─────────────────────────────────────────
class ClientProfileBase(BaseModel):
    business_name: str
    business_slug: Optional[str] = None
    industry: Optional[str] = None
    sub_industry: Optional[str] = None
    owner_name: Optional[str] = None
    owner_email: Optional[str] = None
    owner_phone: Optional[str] = None
    business_email: Optional[str] = None
    business_phone: Optional[str] = None
    address: dict = {}
    source_platform: Optional[str] = None
    stripe_customer_id: Optional[str] = None
    ghl_location_id: Optional[str] = None
    vapi_assistant_id: Optional[str] = None
    brand: dict = {}
    tier: Optional[str] = None
    active_services: List[str] = []
    onboarding_status: str = "pending"
    onboarding_data: dict = {}
    notes: Optional[str] = None
    tags: List[str] = []
    config: dict = {}

class ClientProfileCreate(ClientProfileBase):
    pass

class ClientProfileResponse(ClientProfileBase):
    id: UUID
    client_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    class Config:
        from_attributes = True


# ── SEMANTIC SEARCH ─────────────────────────────────────────
class SemanticSearchRequest(BaseModel):
    query: str
    table: str = "skills"           # 'skills' | 'agents' | 'templates'
    limit: int = Field(default=5, le=20)
    filters: dict = {}
