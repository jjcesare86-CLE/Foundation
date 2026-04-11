from fastapi import FastAPI
from app.routers import skills, agents, brand, clients, templates, employees, voice_employee_builder
from .foundation_agents import router as agents_router
from .gemini_voice_proxy import router as voice_router


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

@app.get("/health")
def health():
    return {"status": "ok"}
