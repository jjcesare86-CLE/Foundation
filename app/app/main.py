from fastapi import FastAPI
from app.routers import skills, agents, brand, clients, templates, employees, voice_employee_builder, research
from app.foundation_agents import router as agents_router
from app.gemini_voice_proxy import router as voice_router
from app.voice_edit.router import router as voice_edit_router
from app.routers.pricing import pricing_router


app = FastAPI(
    title="Foundation API",
    description="Shared API layer for Automation Nation, VoiceMIO, and Jubilant Careers",
    version="1.0.0",
)

app.include_router(skills.router)
app.include_router(agents.router)
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

@app.get("/health")
def health():
    return {"status": "ok"}
