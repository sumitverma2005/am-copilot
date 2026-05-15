from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from api_gateway.auth import require_auth
from api_gateway.data_loader import list_coaching_queue, list_compliance_queue
from api_gateway.state_store import (
    get_coached,
    get_reviewed,
    mark_coached,
    mark_reviewed,
)

router = APIRouter(dependencies=[Depends(require_auth)])


# ── Coaching queue ─────────────────────────────────────────────────────────────

@router.get("/queue/coaching")
async def coaching_queue() -> list[dict]:
    calls = list_coaching_queue()
    coached = get_coached()
    for row in calls:
        state = coached.get(row["call_id"])
        row["coached_at"] = state["at"] if state else None
        row["coached_by"] = state["by"] if state else None
    return calls


@router.post("/queue/coaching/{call_id}/complete", status_code=status.HTTP_200_OK)
async def complete_coaching(call_id: str) -> dict:
    queue = list_coaching_queue()
    if not any(r["call_id"] == call_id for r in queue):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Call {call_id!r} not in coaching queue")
    mark_coached(call_id)
    return {"call_id": call_id, "status": "coached"}


# ── Compliance queue ───────────────────────────────────────────────────────────

@router.get("/queue/compliance")
async def compliance_queue() -> list[dict]:
    rows = list_compliance_queue()
    reviewed = get_reviewed()
    for row in rows:
        state = reviewed.get(row["call_id"])
        row["reviewed_at"] = state["at"] if state else None
        row["reviewed_by"] = state["by"] if state else None
        row["review_comment"] = state["comment"] if state else None
    return rows


class ReviewBody(BaseModel):
    comment: str


@router.post("/queue/compliance/{call_id}/review", status_code=status.HTTP_200_OK)
async def complete_review(call_id: str, body: ReviewBody) -> dict:
    queue = list_compliance_queue()
    if not any(r["call_id"] == call_id for r in queue):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Call {call_id!r} not in compliance queue")
    mark_reviewed(call_id, body.comment)
    return {"call_id": call_id, "status": "reviewed"}
