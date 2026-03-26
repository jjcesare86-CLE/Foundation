"""
Foundation API — Shared layer for Automation Nation, VoiceMIO, Jubilant Careers
Deploy to Render. All platforms call this single service.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os

from routers import skills, agents, brands, templates, clients
from db.client import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(
    title="Foundation API",
    description="Shared skill/agent/brand layer for all John's platforms",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow all platforms to call this
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://automaition-nation.onrender.com",
        "https://an-sales-pipeline.onrender.com",
        "https://voicemio.com",
        "https://blast-video-api-jr06.onrender.com",
        "http://localhost:3000",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(skills.router,    prefix="/skills",    tags=["Skills"])
app.include_router(agents.router,    prefix="/agents",    tags=["Agents"])
app.include_router(brands.router,    prefix="/brands",    tags=["Brands"])
app.include_router(templates.router, prefix="/templates", tags=["Templates"])
app.include_router(clients.router,   prefix="/clients",   tags=["Clients"])

@app.get("/")
async def root():
    return {
        "service": "Foundation API",
        "version": "1.0.0",
        "status": "operational",
        "platforms": ["automation-nation", "voicemio", "jubilant-careers"],
    }

@app.get("/health")
async def health():
    return {"status": "ok"}
