"""
Foundation API — Action Library Router
The generic approval-inbox surface: list/inspect pending actions, edit a
draft before approving, approve (executes immediately), reject.
"""
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.action_library import executor

router = APIRouter(prefix="/actions", tags=["actions"])


@router.get("")
def list_actions(status: Optional[str] = None, agent_id: Optional[str] = None, client_id: Optional[str] = None):
    return executor.list_actions(status=status, agent_id=agent_id, client_id=client_id)


@router.get("/{action_id}")
def get_action(action_id: str):
    action = executor.get_action(action_id)
    if not action:
        raise HTTPException(404, f"action {action_id} not found")
    return action


class DraftUpdate(BaseModel):
    draft: dict


@router.patch("/{action_id}")
def update_draft(action_id: str, body: DraftUpdate):
    action = executor.get_action(action_id)
    if not action:
        raise HTTPException(404, f"action {action_id} not found")
    if action["status"] != "pending":
        raise HTTPException(409, f"action {action_id} is {action['status']}, not pending — can't edit")
    return executor.update_draft(action_id, body.draft)


class ApproveRequest(BaseModel):
    approved_by: str = "dashboard"


@router.post("/{action_id}/approve")
def approve_action(action_id: str, body: ApproveRequest):
    try:
        return executor.approve_action(action_id, body.approved_by)
    except ValueError as e:
        raise HTTPException(409, str(e))


class RejectRequest(BaseModel):
    rejected_by: str = "dashboard"
    reason: Optional[str] = None


@router.post("/{action_id}/reject")
def reject_action(action_id: str, body: RejectRequest):
    action = executor.get_action(action_id)
    if not action:
        raise HTTPException(404, f"action {action_id} not found")
    if action["status"] != "pending":
        raise HTTPException(409, f"action {action_id} is {action['status']}, not pending")
    return executor.reject_action(action_id, body.rejected_by, body.reason)
