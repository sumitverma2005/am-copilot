from __future__ import annotations

import csv
import io
from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from api_gateway.auth import require_auth
from api_gateway.state_store import add_override, get_overrides

router = APIRouter(dependencies=[Depends(require_auth)])

_CSV_FIELDS = ["call_id", "dimension", "ai_score", "manager_score", "delta", "comment", "manager", "date"]


@router.get("/disagreements")
async def list_disagreements() -> list[dict]:
    return get_overrides()


@router.get("/disagreements/export")
async def export_disagreements() -> StreamingResponse:
    rows = get_overrides()
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=_CSV_FIELDS, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)
    buf.seek(0)
    return StreamingResponse(
        iter([buf.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=disagreements.csv"},
    )


class OverrideBody(BaseModel):
    dimension: str
    ai_score: float | None
    manager_score: float | None
    comment: str
    manager: str = "demo"
