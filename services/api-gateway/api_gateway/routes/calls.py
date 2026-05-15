from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from api_gateway.auth import require_auth
from api_gateway.data_loader import get_call, get_evidence, list_calls
from api_gateway.state_store import add_override, get_note, save_note

router = APIRouter(prefix="/calls", dependencies=[Depends(require_auth)])


@router.get("")
async def calls_list() -> list[dict]:
    return list_calls()


@router.get("/{call_id}")
async def call_detail(call_id: str) -> dict:
    data = get_call(call_id)
    if data is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Call {call_id!r} not found")
    return data


@router.get("/{call_id}/evidence/{dimension}")
async def call_evidence(call_id: str, dimension: str) -> dict:
    result = get_evidence(call_id, dimension)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Call {call_id!r} not found")
    return result


class NoteBody(BaseModel):
    text: str


@router.get("/{call_id}/note")
async def get_call_note(call_id: str) -> dict:
    if get_call(call_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Call {call_id!r} not found")
    return {"call_id": call_id, "text": get_note(call_id) or ""}


@router.post("/{call_id}/note", status_code=status.HTTP_200_OK)
async def save_call_note(call_id: str, body: NoteBody) -> dict:
    if get_call(call_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Call {call_id!r} not found")
    save_note(call_id, body.text)
    return {"call_id": call_id, "text": body.text}


class OverrideBody(BaseModel):
    dimension: str
    ai_score: float | None
    manager_score: float | None
    comment: str
    manager: str = "demo"


@router.post("/{call_id}/override", status_code=status.HTTP_201_CREATED)
async def create_override(call_id: str, body: OverrideBody) -> dict:
    if get_call(call_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Call {call_id!r} not found")
    delta = None
    if body.ai_score is not None and body.manager_score is not None:
        delta = round(body.manager_score - body.ai_score, 2)
    record = {
        "call_id": call_id,
        "dimension": body.dimension,
        "ai_score": body.ai_score,
        "manager_score": body.manager_score,
        "delta": delta,
        "comment": body.comment,
        "manager": body.manager,
        "date": datetime.now(timezone.utc).isoformat(),
    }
    add_override(record)
    return record
