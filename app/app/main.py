import os

from fastapi import FastAPI, Depends, Security, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import APIKeyHeader

from app.routers import skills, brand, clients, templates, employees, voice_employee_builder, research, actions, rahab, zacchaeus, silas
from app.foundation_agents import router as agents_router
from app.gemini_voice_proxy import router as voice_router
from app.voice_edit.router import router as voice_edit_router
from app.routers.pricing import pricing_router
from app.rahab.action_types import register_rahab_actions
from app.silas.action_types import register_silas_actions


app = FastAPI(
    title="Foundation API",
    description="Shared API layer for Automation Nation, VoiceMIO, and Jubilant Careers",
    version="1.0.0",
)

# ── CORS ─────────────────────────────────────────────────────────────────
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "").split(",")
# Fallback for dev: if empty, allow localhost
if not ALLOWED_ORIGINS or ALLOWED_ORIGINS == [""]:
    ALLOWED_ORIGINS = ["http://localhost:3000", "http://localhost:8080"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── API key gate (internal/admin endpoints only) ────────────────────────
API_KEY_HEADER = APIKeyHeader(name="X-Foundation-API-Key", auto_error=False)
FOUNDATION_API_KEY = os.getenv("FOUNDATION_API_KEY")


async def require_api_key(api_key: str = Security(API_KEY_HEADER)):
    if not FOUNDATION_API_KEY:
        # Key not configured = fail closed, not open
        raise HTTPException(503, "API key not configured on server")
    if api_key != FOUNDATION_API_KEY:
        raise HTTPException(403, "Invalid API key")
    return api_key


# USAGE: add `dependencies=[Depends(require_api_key)]` to any router or
# individual endpoint that should be protected. Public endpoints (like
# /public/agents, /dock/bootstrap with its own JWT auth) stay open.
# Example:
#   app.include_router(admin_router, dependencies=[Depends(require_api_key)])
#   app.include_router(ops_router, prefix="/ops", dependencies=[Depends(require_api_key)])
#
# NOTE: /connections, /dock, and /public routers still don't exist. /ops
# and /admin don't either, but /rahab (cron-only triggers) and /actions
# (the approval inbox) are internal in the same spirit, so they're gated
# below even though the spec's own list didn't name them explicitly.

# Register each agent's action-library handlers before any request can hit them.
register_rahab_actions()
register_silas_actions()

app.include_router(skills.router)
app.include_router(brand.router)
app.include_router(clients.router)
app.include_router(templates.router)
app.include_router(employees.router)
app.include_router(voice_employee_builder.router)
app.include_router(agents_router)
app.include_router(voice_router)
app.include_router(voice_edit_router, prefix="/voice-edit")
app.include_router(pricing_router)
app.include_router(research.router)
app.include_router(actions.router, dependencies=[Depends(require_api_key)])
app.include_router(rahab.router, dependencies=[Depends(require_api_key)])
app.include_router(zacchaeus.router, dependencies=[Depends(require_api_key)])
app.include_router(silas.router, dependencies=[Depends(require_api_key)])

@app.get("/health")
def health():
    return {"status": "ok"}
