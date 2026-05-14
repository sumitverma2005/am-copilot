"""Pydantic v2 models for scoring engine I/O.

EvidenceSnippet, DimensionResult, EvaluationResult — ported verbatim from
docs/prompt-library.md section 2 (Output parsing).

ScoreResult — output of arbitration; fields match the DB schema in TSD section 4
(evaluations + dimension_scores + evidence_anchors tables) for zero-reshaping JSON→DB.
"""
from __future__ import annotations

from typing import Optional
from pydantic import BaseModel


# ── Verbatim from prompt-library.md ───────────────────────────────────────────

class EvidenceSnippet(BaseModel):
    turn: int
    timestamp_seconds: int
    speaker: str
    text: str
    relevance_rank: int


class DimensionResult(BaseModel):
    score: Optional[int]       # None = N/A
    rationale: str
    coaching_note: Optional[str]
    confidence: float
    evidence: list[EvidenceSnippet]


class EvaluationResult(BaseModel):
    dimension_scores: dict[str, DimensionResult]
    manager_summary: str
    overall_confidence: float


# ── Arbitrated output — maps 1:1 to DB tables ─────────────────────────────────

class DimensionScoreRow(BaseModel):
    """Maps to one row in the dimension_scores table."""
    dimension: str
    raw_score: Optional[int]       # 0–5, None = N/A
    weighted_score: Optional[float]  # None when N/A
    weight: float
    confidence: Optional[float]
    ai_rationale: str
    coaching_note: Optional[str]
    is_na: bool


class EvidenceAnchorRow(BaseModel):
    """Maps to one row in the evidence_anchors table."""
    dimension: str
    turn_number: int
    timestamp_seconds: int
    speaker: str
    text_snippet: str              # max 200 chars, as per prompt spec
    relevance_rank: int


class ComplianceFlagRow(BaseModel):
    """Maps to one row in the compliance_flags table."""
    flag_code: str
    matched_phrase: str
    turn_number: int
    timestamp_seconds: int
    severity: str
    reviewed: bool = False


class EvaluationRow(BaseModel):
    """Maps to one row in the evaluations table."""
    call_id: str
    agent_id: str
    call_timestamp: str            # ISO-8601
    duration_seconds: int
    scenario_type: Optional[str]   # synthetic only
    rubric_version: str
    prompt_version: str
    model_id: str
    overall_score: float           # 0–100, NUMERIC(5,2) in DB
    compliance_override_triggered: bool
    confidence_overall: float
    manager_summary: str
    status: str = "scored"
    scored_at: str                 # ISO-8601


class ScoreResult(BaseModel):
    """Full scored record — the flat structure written to data/results/*.json.

    Contains one EvaluationRow + child rows for each related table.
    When adding ORM: read JSON → insert evaluation row → insert child rows.
    No reshaping required.
    """
    evaluation: EvaluationRow
    dimension_scores: list[DimensionScoreRow]
    evidence_anchors: list[EvidenceAnchorRow]
    compliance_flags: list[ComplianceFlagRow]
