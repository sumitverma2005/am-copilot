"""Load scored call results from data/results/*.json.

Phase A source of truth. When the ORM layer is added, replace
_load_result() with a DB read — callers are unchanged.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

_RESULTS_DIR = Path(__file__).parents[3] / "data" / "results"


def _load_result(call_id: str) -> Optional[dict]:
    path = _RESULTS_DIR / f"{call_id}_result.json"
    if not path.exists():
        return None
    return json.loads(path.read_text())


def list_calls() -> list[dict]:
    """Return summary rows for all scored calls."""
    rows = []
    for path in sorted(_RESULTS_DIR.glob("*_result.json")):
        data = json.loads(path.read_text())
        ev = data["evaluation"]
        dim_scores = data.get("dimension_scores", [])
        flags = data.get("compliance_flags", [])

        applicable = [d for d in dim_scores if not d.get("is_na")]
        worst_dim = min(applicable, key=lambda d: d["raw_score"] or 0, default=None)

        rows.append({
            "call_id": ev["call_id"],
            "agent_id": ev["agent_id"],
            "call_timestamp": ev["call_timestamp"],
            "duration_seconds": ev["duration_seconds"],
            "scenario_type": ev.get("scenario_type"),
            "overall_score": ev["overall_score"],
            "compliance_override_triggered": ev["compliance_override_triggered"],
            "status": ev["status"],
            "worst_dimension": worst_dim["dimension"] if worst_dim else None,
            "has_compliance_flags": len(flags) > 0,
        })
    return rows


def get_call(call_id: str) -> Optional[dict]:
    return _load_result(call_id)


def get_evidence(call_id: str, dimension: str) -> Optional[list[dict]]:
    data = _load_result(call_id)
    if data is None:
        return None
    anchors = [
        a for a in data.get("evidence_anchors", [])
        if a["dimension"] == dimension
    ]
    dim_scores = data.get("dimension_scores", [])
    dim_row = next((d for d in dim_scores if d["dimension"] == dimension), None)
    return {
        "call_id": call_id,
        "dimension": dimension,
        "anchors": anchors,
        "dim_score": dim_row,
    }
