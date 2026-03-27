from fastapi import FastAPI
from app.routers import skills, agents, brand, clients, templates, employees

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

@app.get("/health")
def health():
    return {"status": "ok"}
