"""Foundation API — Silas (Field Service Dispatcher) Router."""
from datetime import date

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.silas.dispatch import build_dispatch
from app.silas.completion import complete_job
from app.silas.slots import claim_slot

router = APIRouter(prefix="/silas", tags=["silas"])


@router.post("/dispatch/{client_id}")
def dispatch(client_id: str, for_date: str = ""):
    target_date = date.fromisoformat(for_date) if for_date else date.today()
    return build_dispatch(client_id, target_date)


@router.post("/jobs/{job_id}/complete")
def complete(job_id: str):
    try:
        return complete_job(job_id)
    except ValueError as e:
        raise HTTPException(404, str(e))


class ClaimSlotBody(BaseModel):
    contact_id: str


@router.post("/slots/{offer_id}/claim")
def claim(offer_id: str, body: ClaimSlotBody):
    return claim_slot(offer_id, body.contact_id)
