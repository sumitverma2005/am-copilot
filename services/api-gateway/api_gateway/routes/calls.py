from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from api_gateway.auth import require_auth
from api_gateway.data_loader import get_call, get_evidence, list_calls

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
