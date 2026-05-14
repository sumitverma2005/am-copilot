"""Tests for packages/rubric-engine."""
import copy
from pathlib import Path

import pytest
from pydantic import ValidationError

from rubric_engine import Dimension, Rubric, load_rubric
from rubric_engine.schema import ScoringScale, ScaleLevel, ComplianceOverride

RUBRIC_PATH = Path(__file__).parents[3] / "data" / "rubric" / "rubric-v1.yaml"

VALID_LEVELS = [
    {"score": 5, "label": "Exemplary", "anchor": "Best possible."},
    {"score": 4, "label": "Strong", "anchor": "Good."},
    {"score": 3, "label": "Acceptable", "anchor": "Adequate."},
    {"score": 2, "label": "Needs improvement", "anchor": "Gaps present."},
    {"score": 1, "label": "Poor", "anchor": "Significant problems."},
    {"score": 0, "label": "Unacceptable", "anchor": "Actively wrong."},
]

VALID_DIMENSION = {
    "id": "test_dim",
    "name": "Test dimension",
    "weight": 1.0,
    "na_allowed": True,
    "description": "A test dimension.",
    "score_for": ["Good behaviour A"],
    "score_against": ["Bad behaviour B"],
}


# ── Fixture helpers ────────────────────────────────────────────────────────────

def _make_rubric(**overrides) -> dict:
    base = {
        "version": "rubric-test",
        "description": "Test rubric",
        "scoring_scale": {
            "levels": copy.deepcopy(VALID_LEVELS),
            "na_label": "N/A",
            "na_rule": "Excluded from average.",
        },
        "overall_score_formula": "(sum weighted) / (sum weights) * 20",
        "compliance_override": {
            "pending_client_signoff": True,
            "rule": "Score 0 on compliance → overall 0.",
        },
        "dimensions": [copy.deepcopy(VALID_DIMENSION)],
    }
    base.update(overrides)
    return base


# ── Test 1: valid rubric-v1.yaml loads cleanly ────────────────────────────────

def test_load_real_rubric_succeeds():
    rubric = load_rubric(RUBRIC_PATH)
    assert rubric.version == "rubric-v1"
    assert len(rubric.dimensions) == 8


def test_all_eight_dimension_ids_present():
    rubric = load_rubric(RUBRIC_PATH)
    ids = {d.id for d in rubric.dimensions}
    expected = {
        "empathy_rapport",
        "insurance_verification",
        "clinical_screening",
        "urgency_triage",
        "family_caller_handling",
        "objection_handling",
        "next_step_clarity",
        "compliance_language",
    }
    assert ids == expected


def test_weights_match_spec():
    rubric = load_rubric(RUBRIC_PATH)
    weights = {d.id: d.weight for d in rubric.dimensions}
    assert weights["empathy_rapport"] == 1.5
    assert weights["compliance_language"] == 1.5
    for dim_id in ("insurance_verification", "clinical_screening", "urgency_triage",
                   "family_caller_handling", "objection_handling", "next_step_clarity"):
        assert weights[dim_id] == 1.0


def test_get_dimension_by_id():
    rubric = load_rubric(RUBRIC_PATH)
    dim = rubric.get_dimension("empathy_rapport")
    assert dim.id == "empathy_rapport"


def test_get_dimension_by_display_name():
    rubric = load_rubric(RUBRIC_PATH)
    dim = rubric.get_dimension("Compliance language")
    assert dim.id == "compliance_language"


def test_get_dimension_missing_raises_key_error():
    rubric = load_rubric(RUBRIC_PATH)
    with pytest.raises(KeyError, match="nonexistent_dim"):
        rubric.get_dimension("nonexistent_dim")


# ── Test 2: missing required field raises a clear error ───────────────────────

def test_missing_version_raises_clear_error():
    data = _make_rubric()
    del data["version"]
    with pytest.raises((ValidationError, ValueError)) as exc_info:
        Rubric.model_validate(data)
    assert "version" in str(exc_info.value).lower()


def test_missing_dimension_weight_raises_clear_error():
    data = _make_rubric()
    del data["dimensions"][0]["weight"]
    with pytest.raises((ValidationError, ValueError)) as exc_info:
        Rubric.model_validate(data)
    assert "weight" in str(exc_info.value).lower()


def test_missing_dimension_name_raises_clear_error():
    data = _make_rubric()
    del data["dimensions"][0]["name"]
    with pytest.raises((ValidationError, ValueError)) as exc_info:
        Rubric.model_validate(data)
    assert "name" in str(exc_info.value).lower()


# ── Test 3: invalid weight values ─────────────────────────────────────────────

@pytest.mark.parametrize("bad_weight", [0, -1, -0.5])
def test_zero_or_negative_weight_rejected(bad_weight):
    data = _make_rubric()
    data["dimensions"][0]["weight"] = bad_weight
    with pytest.raises((ValidationError, ValueError)) as exc_info:
        Rubric.model_validate(data)
    assert "weight" in str(exc_info.value).lower()


def test_weight_above_five_rejected():
    data = _make_rubric()
    data["dimensions"][0]["weight"] = 6.0
    with pytest.raises((ValidationError, ValueError)) as exc_info:
        Rubric.model_validate(data)
    assert "weight" in str(exc_info.value).lower()


def test_weight_of_1_5_accepted():
    data = _make_rubric()
    data["dimensions"][0]["weight"] = 1.5
    rubric = Rubric.model_validate(data)
    assert rubric.dimensions[0].weight == 1.5


# ── Test 4: malformed scale levels ────────────────────────────────────────────

def test_missing_score_level_rejected():
    data = _make_rubric()
    # Remove score level 3 — now 5 levels, missing score 3
    data["scoring_scale"]["levels"] = [
        lvl for lvl in VALID_LEVELS if lvl["score"] != 3
    ]
    with pytest.raises((ValidationError, ValueError)) as exc_info:
        Rubric.model_validate(data)
    msg = str(exc_info.value).lower()
    assert "missing" in msg or "level" in msg or "3" in msg


def test_duplicate_score_level_rejected():
    data = _make_rubric()
    # Add a second entry for score 4
    extra = {"score": 4, "label": "Strong (duplicate)", "anchor": "Dupe."}
    data["scoring_scale"]["levels"] = copy.deepcopy(VALID_LEVELS) + [extra]
    with pytest.raises((ValidationError, ValueError)) as exc_info:
        Rubric.model_validate(data)
    msg = str(exc_info.value).lower()
    assert "duplicate" in msg or "4" in msg


# ── Test 5: N/A flag handling ─────────────────────────────────────────────────

def test_na_score_on_na_allowed_dimension_passes():
    rubric = load_rubric(RUBRIC_PATH)
    dim = rubric.get_dimension("objection_handling")
    assert dim.na_allowed is True
    dim.validate_score(None)  # must not raise


def test_na_score_on_non_na_dimension_raises():
    rubric = load_rubric(RUBRIC_PATH)
    dim = rubric.get_dimension("empathy_rapport")
    assert dim.na_allowed is False
    with pytest.raises(ValueError, match="empathy_rapport"):
        dim.validate_score(None)


def test_na_score_on_compliance_language_raises():
    rubric = load_rubric(RUBRIC_PATH)
    dim = rubric.get_dimension("compliance_language")
    assert dim.na_allowed is False
    with pytest.raises(ValueError, match="compliance_language"):
        dim.validate_score(None)


def test_valid_integer_score_passes():
    rubric = load_rubric(RUBRIC_PATH)
    dim = rubric.get_dimension("empathy_rapport")
    for score in range(6):
        dim.validate_score(score)  # must not raise


def test_out_of_range_score_raises():
    rubric = load_rubric(RUBRIC_PATH)
    dim = rubric.get_dimension("empathy_rapport")
    with pytest.raises(ValueError, match="out of range"):
        dim.validate_score(6)
    with pytest.raises(ValueError, match="out of range"):
        dim.validate_score(-1)


# ── Test 6: empty score_for / score_against rejected ──────────────────────────

def test_empty_score_for_rejected():
    data = _make_rubric()
    data["dimensions"][0]["score_for"] = []
    with pytest.raises((ValidationError, ValueError)):
        Rubric.model_validate(data)


def test_empty_score_against_rejected():
    data = _make_rubric()
    data["dimensions"][0]["score_against"] = []
    with pytest.raises((ValidationError, ValueError)):
        Rubric.model_validate(data)
