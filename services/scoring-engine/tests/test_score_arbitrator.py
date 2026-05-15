"""Tests for ScoreArbitrator — all Bedrock calls mocked."""
from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import pytest

from scoring_engine.models import ScoreResult
from scoring_engine.score_arbitrator import ScoreArbitrator, _calc_overall, _parse_response
from compliance_engine.detector import ComplianceFlag


# ── Fixtures ───────────────────────────────────────────────────────────────────

def _make_dim_response(score: int | None = 4, coaching: str | None = None) -> dict:
    return {
        "score": score,
        "rationale": "Test rationale.",
        "coaching_note": coaching,
        "confidence": 0.9,
        "evidence": [
            {
                "turn": 1,
                "timestamp_seconds": 0,
                "speaker": "agent",
                "text": "Test evidence span.",
                "relevance_rank": 1,
            }
        ],
    }


def _make_bedrock_response(
    scores: dict[str, int | None] | None = None,
    compliance_score: int = 5,
) -> str:
    if scores is None:
        scores = {
            "empathy_rapport": 4,
            "insurance_verification": 4,
            "clinical_screening": 4,
            "urgency_triage": 3,
            "family_caller_handling": None,
            "objection_handling": 4,
            "next_step_clarity": 4,
            "compliance_language": compliance_score,
        }
    dim_scores = {dim: _make_dim_response(score) for dim, score in scores.items()}
    return json.dumps({
        "dimension_scores": dim_scores,
        "manager_summary": "A solid call with good rapport.",
        "overall_confidence": 0.88,
    })


NORMALIZED_CALL = {
    "call_id": "syn_001",
    "agent_id": "AGT-1",
    "called_at": "2026-04-01T00:00:00Z",
    "duration": 180,
    "ctm_sentiment": None,
    "transcript": [
        {"turn": 1, "speaker": "agent", "timestamp_seconds": 0,
         "text": "Thank you for calling Sunrise Recovery Center.", "confidence": None},
        {"turn": 2, "speaker": "caller", "timestamp_seconds": 5,
         "text": "Hi, I need help.", "confidence": None},
    ],
}


def _make_arbitrator(bedrock_response: str) -> ScoreArbitrator:
    mock_client = MagicMock()
    mock_client.invoke.return_value = bedrock_response
    mock_client.model_id = "test-bedrock-model"
    return ScoreArbitrator(bedrock_client=mock_client)


# ── Prompt construction ────────────────────────────────────────────────────────

def test_prompt_contains_transcript_text():
    arb = _make_arbitrator(_make_bedrock_response())
    arb.score(NORMALIZED_CALL)
    call_args = arb._bedrock.invoke.call_args
    user_prompt = call_args[0][1]
    assert "Thank you for calling Sunrise Recovery Center" in user_prompt


def test_prompt_contains_rubric_dimensions():
    arb = _make_arbitrator(_make_bedrock_response())
    arb.score(NORMALIZED_CALL)
    call_args = arb._bedrock.invoke.call_args
    user_prompt = call_args[0][1]
    assert "empathy_rapport" in user_prompt
    assert "compliance_language" in user_prompt


def test_prompt_contains_rubric_scale_anchors():
    arb = _make_arbitrator(_make_bedrock_response())
    arb.score(NORMALIZED_CALL)
    call_args = arb._bedrock.invoke.call_args
    user_prompt = call_args[0][1]
    assert "Exemplary" in user_prompt
    assert "Unacceptable" in user_prompt


def test_system_prompt_sent_correctly():
    arb = _make_arbitrator(_make_bedrock_response())
    arb.score(NORMALIZED_CALL)
    call_args = arb._bedrock.invoke.call_args
    system_prompt = call_args[0][0]
    assert "behavioral-health" in system_prompt
    assert "ONLY valid JSON" in system_prompt


# ── Response parsing ───────────────────────────────────────────────────────────

def test_response_parsed_into_evaluation_result():
    arb = _make_arbitrator(_make_bedrock_response())
    result = arb.score(NORMALIZED_CALL)
    assert isinstance(result, ScoreResult)
    assert len(result.dimension_scores) == 8


def test_dimension_scores_have_correct_fields():
    arb = _make_arbitrator(_make_bedrock_response())
    result = arb.score(NORMALIZED_CALL)
    for row in result.dimension_scores:
        assert hasattr(row, "dimension")
        assert hasattr(row, "raw_score")
        assert hasattr(row, "weight")
        assert hasattr(row, "is_na")


def test_evidence_anchors_extracted():
    arb = _make_arbitrator(_make_bedrock_response())
    result = arb.score(NORMALIZED_CALL)
    assert len(result.evidence_anchors) > 0
    assert all(hasattr(a, "text_snippet") for a in result.evidence_anchors)


def test_markdown_fences_stripped_from_response():
    fenced = "```json\n" + _make_bedrock_response() + "\n```"
    parsed = _parse_response(fenced)
    assert parsed.manager_summary == "A solid call with good rapport."


# ── N/A handling ──────────────────────────────────────────────────────────────

def test_na_dimension_excluded_from_weighted_average():
    """family_caller_handling = None (N/A) must not contribute to the weighted average."""
    arb = _make_arbitrator(_make_bedrock_response())
    result = arb.score(NORMALIZED_CALL)

    na_row = next(r for r in result.dimension_scores if r.dimension == "family_caller_handling")
    assert na_row.is_na is True
    assert na_row.raw_score is None
    assert na_row.weighted_score is None


def test_na_dimension_weight_excluded_from_denominator():
    """Overall score must not include N/A dimension weight in denominator."""
    # All dims score 5, family_caller = None (N/A, weight 1.0)
    # Applicable: 7 dims. Expected overall ≈ 5 * (sum applicable weights) / (sum applicable weights) * 20 = 100
    scores = {
        "empathy_rapport": 5,      # weight 1.5
        "insurance_verification": 5,
        "clinical_screening": 5,
        "urgency_triage": 5,
        "family_caller_handling": None,  # N/A — excluded
        "objection_handling": 5,
        "next_step_clarity": 5,
        "compliance_language": 5,  # weight 1.5
    }
    arb = _make_arbitrator(_make_bedrock_response(scores=scores))
    result = arb.score(NORMALIZED_CALL)
    assert result.evaluation.overall_score == 100.0


# ── Compliance override ────────────────────────────────────────────────────────

def test_compliance_flag_forces_compliance_language_to_zero(monkeypatch):
    """Critical compliance flag must override compliance_language score to 0."""
    monkeypatch.delenv("COMPLIANCE_OVERRIDE_ENABLED", raising=False)
    flag = ComplianceFlag(
        flag_code="DIAG_CLAIM",
        matched_phrase="you have addiction",
        turn_number=3,
        timestamp_seconds=30,
        severity="critical",
        description="Diagnostic claim",
    )
    # Bedrock returns compliance_language=4, but flag must force it to 0
    arb = _make_arbitrator(_make_bedrock_response(compliance_score=4))
    result = arb.score(NORMALIZED_CALL, compliance_flags=[flag])

    comp_row = next(r for r in result.dimension_scores if r.dimension == "compliance_language")
    assert comp_row.raw_score == 0
    assert result.evaluation.compliance_override_triggered is True


def test_no_compliance_flag_leaves_compliance_score_intact(monkeypatch):
    monkeypatch.delenv("COMPLIANCE_OVERRIDE_ENABLED", raising=False)
    arb = _make_arbitrator(_make_bedrock_response(compliance_score=4))
    result = arb.score(NORMALIZED_CALL, compliance_flags=[])

    comp_row = next(r for r in result.dimension_scores if r.dimension == "compliance_language")
    assert comp_row.raw_score == 4
    assert result.evaluation.compliance_override_triggered is False


def test_compliance_override_enabled_forces_overall_to_zero(monkeypatch):
    """When COMPLIANCE_OVERRIDE_ENABLED=true and compliance_language=0 → overall=0."""
    monkeypatch.setenv("COMPLIANCE_OVERRIDE_ENABLED", "true")
    flag = ComplianceFlag(
        flag_code="DIAG_CLAIM", matched_phrase="x",
        turn_number=1, timestamp_seconds=0, severity="critical", description="d",
    )
    arb = _make_arbitrator(_make_bedrock_response(compliance_score=5))
    result = arb.score(NORMALIZED_CALL, compliance_flags=[flag])
    assert result.evaluation.overall_score == 0.0


def test_compliance_override_disabled_does_not_zero_overall(monkeypatch):
    """When COMPLIANCE_OVERRIDE_ENABLED=false (Phase A default), overall is not forced to 0."""
    monkeypatch.setenv("COMPLIANCE_OVERRIDE_ENABLED", "false")
    flag = ComplianceFlag(
        flag_code="DIAG_CLAIM", matched_phrase="x",
        turn_number=1, timestamp_seconds=0, severity="critical", description="d",
    )
    arb = _make_arbitrator(_make_bedrock_response(compliance_score=5))
    result = arb.score(NORMALIZED_CALL, compliance_flags=[flag])
    assert result.evaluation.overall_score > 0


# ── Overall score calculation ──────────────────────────────────────────────────

def test_overall_score_matches_rubric_formula():
    """Verify (sum weighted_scores) / (sum weights) * 20 rounding."""
    # empathy=5 (w=1.5), compliance=5 (w=1.5), all others=4 (w=1.0×6=6.0)
    # weighted_sum = 5*1.5 + 5*1.5 + 4*6 = 7.5 + 7.5 + 24 = 39
    # weight_sum = 1.5 + 1.5 + 6 = 9
    # overall = (39/9) * 20 = 86.67 → rounds to 86.67
    scores = {
        "empathy_rapport": 5,
        "insurance_verification": 4,
        "clinical_screening": 4,
        "urgency_triage": 4,
        "family_caller_handling": 4,
        "objection_handling": 4,
        "next_step_clarity": 4,
        "compliance_language": 5,
    }
    arb = _make_arbitrator(_make_bedrock_response(scores=scores))
    result = arb.score(NORMALIZED_CALL)
    assert result.evaluation.overall_score == pytest.approx(86.67, abs=0.01)


# ── ScoreResult DB-ready shape ─────────────────────────────────────────────────

def test_score_result_has_evaluation_row():
    arb = _make_arbitrator(_make_bedrock_response())
    result = arb.score(NORMALIZED_CALL)
    assert result.evaluation.call_id == "syn_001"
    assert result.evaluation.status == "scored"
    assert result.evaluation.rubric_version == "rubric-v1"


def test_score_result_compliance_flags_stored():
    flag = ComplianceFlag(
        flag_code="DIAG_CLAIM", matched_phrase="x",
        turn_number=1, timestamp_seconds=0, severity="critical", description="d",
    )
    arb = _make_arbitrator(_make_bedrock_response())
    result = arb.score(NORMALIZED_CALL, compliance_flags=[flag])
    assert len(result.compliance_flags) == 1
    assert result.compliance_flags[0].flag_code == "DIAG_CLAIM"
