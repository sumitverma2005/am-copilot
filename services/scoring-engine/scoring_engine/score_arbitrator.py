"""Score arbitrator — orchestrates the full evaluation pipeline.

Steps:
  1. Load rubric
  2. Build evaluation prompt
  3. Call LLM (Bedrock or Anthropic, selected via MODEL_PROVIDER env var)
  4. Parse EvaluationResult
  5. Apply compliance override (if compliance flags passed in)
  6. Compute weighted overall score (N/A dimensions excluded)
  7. Return ScoreResult (maps 1:1 to DB schema)
"""
from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from typing import Optional

_logger = logging.getLogger(__name__)

from prompt_library.evaluation.prompt_v1 import (
    PROMPT_VERSION,
    SYSTEM_PROMPT,
    build_evaluation_prompt,
)
from rubric_engine import Rubric

from compliance_engine.detector import ComplianceFlag

from .bedrock_client import BedrockClient
from .anthropic_client import AnthropicClient
from .models import (
    ComplianceFlagRow,
    DimensionResult,
    DimensionScoreRow,
    EvaluationResult,
    EvaluationRow,
    EvidenceAnchorRow,
    ScoreResult,
)
from .rubric_loader import load_rubric_for_scoring

_COMPLIANCE_DIM = "compliance_language"


def _make_llm_client() -> BedrockClient | AnthropicClient:
    """Instantiate the LLM client selected by MODEL_PROVIDER env var.

    MODEL_PROVIDER=bedrock   (default) — production path via AWS Bedrock
    MODEL_PROVIDER=anthropic           — build-window workaround; remove pre-prod
    """
    provider = os.environ.get("MODEL_PROVIDER", "bedrock").lower()
    _logger.info("Scoring engine using MODEL_PROVIDER=%s", provider)
    if provider == "anthropic":
        _logger.warning(
            "MODEL_PROVIDER=anthropic — build-window workaround active; "
            "production target is bedrock."
        )
        return AnthropicClient()
    return BedrockClient()


class ScoreArbitrator:
    def __init__(self, bedrock_client: Optional[BedrockClient] = None) -> None:
        self._bedrock = bedrock_client or _make_llm_client()

    def score(
        self,
        normalized_call: dict,
        compliance_flags: list[ComplianceFlag] | None = None,
    ) -> ScoreResult:
        """Score a normalized call and return a fully arbitrated ScoreResult.

        Args:
            normalized_call:  output of normalizer.normalize()
            compliance_flags: ComplianceFlag objects from compliance_engine (may be empty)

        Returns:
            ScoreResult with fields matching the DB schema.
        """
        compliance_flags = compliance_flags or []
        rubric = load_rubric_for_scoring()
        transcript = normalized_call.get("transcript", [])

        user_prompt = build_evaluation_prompt(transcript, rubric)
        raw_text = self._bedrock.invoke(SYSTEM_PROMPT, user_prompt)
        eval_result = _parse_response(raw_text)

        dim_scores, anchor_rows = _build_dimension_rows(
            eval_result, rubric, compliance_flags
        )
        compliance_triggered = _compliance_override_triggered(dim_scores)
        overall = _calc_overall(dim_scores, rubric, compliance_triggered)

        eval_row = EvaluationRow(
            call_id=normalized_call.get("call_id", ""),
            agent_id=normalized_call.get("agent_id", ""),
            call_timestamp=normalized_call.get("called_at", ""),
            duration_seconds=normalized_call.get("duration", 0),
            scenario_type=None,
            rubric_version=rubric.version,
            prompt_version=PROMPT_VERSION,
            model_id=self._bedrock.model_id,
            overall_score=overall,
            compliance_override_triggered=compliance_triggered,
            confidence_overall=eval_result.overall_confidence,
            manager_summary=eval_result.manager_summary,
            status="scored",
            scored_at=datetime.now(timezone.utc).isoformat(),
        )

        flag_rows = [_flag_to_row(f) for f in compliance_flags]
        return ScoreResult(
            evaluation=eval_row,
            dimension_scores=dim_scores,
            evidence_anchors=anchor_rows,
            compliance_flags=flag_rows,
        )


# ── Helpers ────────────────────────────────────────────────────────────────────

def _parse_response(raw_text: str) -> EvaluationResult:
    clean = raw_text.strip().removeprefix("```json").removesuffix("```").strip()
    data = json.loads(clean)
    return EvaluationResult.model_validate(data)


def _build_dimension_rows(
    eval_result: EvaluationResult,
    rubric: Rubric,
    compliance_flags: list[ComplianceFlagRow],
) -> tuple[list[DimensionScoreRow], list[EvidenceAnchorRow]]:
    has_critical_flag = any(f.severity == "critical" for f in compliance_flags)
    dim_rows: list[DimensionScoreRow] = []
    anchor_rows: list[EvidenceAnchorRow] = []

    for dim_id, result in eval_result.dimension_scores.items():
        dim = rubric.get_dimension(dim_id)
        score = result.score

        # Deterministic compliance override: if critical flag exists, force
        # compliance_language to 0 regardless of what Bedrock returned.
        if dim_id == _COMPLIANCE_DIM and has_critical_flag:
            score = 0

        is_na = score is None
        weighted = None if is_na else round(score * dim.weight, 2)

        dim_rows.append(DimensionScoreRow(
            dimension=dim_id,
            raw_score=score,
            weighted_score=weighted,
            weight=dim.weight,
            confidence=result.confidence,
            ai_rationale=result.rationale,
            coaching_note=result.coaching_note,
            is_na=is_na,
        ))

        for snippet in result.evidence:
            anchor_rows.append(EvidenceAnchorRow(
                dimension=dim_id,
                turn_number=snippet.turn,
                timestamp_seconds=snippet.timestamp_seconds,
                speaker=snippet.speaker,
                text_snippet=snippet.text[:200],
                relevance_rank=snippet.relevance_rank,
            ))

    return dim_rows, anchor_rows


def _compliance_override_triggered(dim_rows: list[DimensionScoreRow]) -> bool:
    for row in dim_rows:
        if row.dimension == _COMPLIANCE_DIM and row.raw_score == 0:
            return True
    return False


def _calc_overall(
    dim_rows: list[DimensionScoreRow],
    rubric: Rubric,
    compliance_triggered: bool,
) -> float:
    override_enabled = os.environ.get("COMPLIANCE_OVERRIDE_ENABLED", "false").lower() == "true"
    if compliance_triggered and override_enabled:
        return 0.0

    weighted_sum = 0.0
    weight_sum = 0.0
    for row in dim_rows:
        if row.is_na:
            continue
        weighted_sum += (row.raw_score or 0) * row.weight
        weight_sum += row.weight

    if weight_sum == 0:
        return 0.0

    return round((weighted_sum / weight_sum) * 20, 2)


def _flag_to_row(flag: ComplianceFlag) -> ComplianceFlagRow:
    """Convert a ComplianceFlag dataclass (from compliance_engine) to a ComplianceFlagRow."""
    return ComplianceFlagRow(
        flag_code=flag.flag_code,
        matched_phrase=flag.matched_phrase,
        turn_number=flag.turn_number,
        timestamp_seconds=flag.timestamp_seconds,
        severity=flag.severity,
    )
