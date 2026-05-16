"""Tests for rubric-v2.yaml — loads, validates, and contains only the expected changes."""
from pathlib import Path

import pytest

from rubric_engine import load_rubric

RUBRIC_V1_PATH = Path(__file__).parents[3] / "data" / "rubric" / "rubric-v1.yaml"
RUBRIC_V2_PATH = Path(__file__).parents[3] / "data" / "rubric" / "rubric-v2.yaml"

UNCHANGED_DIMS = [
    "empathy_rapport",
    "insurance_verification",
    "clinical_screening",
    "urgency_triage",
    "family_caller_handling",
    "next_step_clarity",
]


# ── Basic load ─────────────────────────────────────────────────────────────────

def test_rubric_v2_loads_cleanly():
    rubric = load_rubric(RUBRIC_V2_PATH)
    assert rubric.version == "rubric-v2"
    assert len(rubric.dimensions) == 8


def test_rubric_v2_all_dimension_ids_present():
    rubric = load_rubric(RUBRIC_V2_PATH)
    ids = {d.id for d in rubric.dimensions}
    expected = {
        "empathy_rapport", "insurance_verification", "clinical_screening",
        "urgency_triage", "family_caller_handling", "objection_handling",
        "next_step_clarity", "compliance_language",
    }
    assert ids == expected


def test_rubric_v2_weights_unchanged():
    rubric = load_rubric(RUBRIC_V2_PATH)
    weights = {d.id: d.weight for d in rubric.dimensions}
    assert weights["empathy_rapport"] == 1.5
    assert weights["compliance_language"] == 1.5
    for dim_id in ("insurance_verification", "clinical_screening", "urgency_triage",
                   "family_caller_handling", "objection_handling", "next_step_clarity"):
        assert weights[dim_id] == 1.0


# ── Six passing dimensions are unchanged ──────────────────────────────────────

def test_six_passing_dims_score_for_unchanged():
    v1 = load_rubric(RUBRIC_V1_PATH)
    v2 = load_rubric(RUBRIC_V2_PATH)
    for dim_id in UNCHANGED_DIMS:
        assert v1.get_dimension(dim_id).score_for == v2.get_dimension(dim_id).score_for, (
            f"{dim_id}.score_for changed in v2 — only objection_handling and "
            "compliance_language should differ"
        )


def test_six_passing_dims_score_against_unchanged():
    v1 = load_rubric(RUBRIC_V1_PATH)
    v2 = load_rubric(RUBRIC_V2_PATH)
    for dim_id in UNCHANGED_DIMS:
        assert v1.get_dimension(dim_id).score_against == v2.get_dimension(dim_id).score_against


def test_six_passing_dims_description_unchanged():
    v1 = load_rubric(RUBRIC_V1_PATH)
    v2 = load_rubric(RUBRIC_V2_PATH)
    for dim_id in UNCHANGED_DIMS:
        assert v1.get_dimension(dim_id).description == v2.get_dimension(dim_id).description


# ── Objection handling — definition added, criteria unchanged ─────────────────

def test_objection_handling_description_expanded():
    v1 = load_rubric(RUBRIC_V1_PATH)
    v2 = load_rubric(RUBRIC_V2_PATH)
    v2_desc = v2.get_dimension("objection_handling").description
    assert len(v2_desc) > len(v1.get_dimension("objection_handling").description)
    assert "transactional" in v2_desc.lower()
    assert "emotional" in v2_desc.lower()
    assert "reputational" in v2_desc.lower()
    assert "skepticism" in v2_desc.lower()


def test_objection_handling_score_for_unchanged():
    v1 = load_rubric(RUBRIC_V1_PATH)
    v2 = load_rubric(RUBRIC_V2_PATH)
    assert (v1.get_dimension("objection_handling").score_for ==
            v2.get_dimension("objection_handling").score_for)


def test_objection_handling_score_against_unchanged():
    v1 = load_rubric(RUBRIC_V1_PATH)
    v2 = load_rubric(RUBRIC_V2_PATH)
    assert (v1.get_dimension("objection_handling").score_against ==
            v2.get_dimension("objection_handling").score_against)


def test_objection_handling_no_score_anchors():
    rubric = load_rubric(RUBRIC_V2_PATH)
    assert rubric.get_dimension("objection_handling").score_anchors is None


# ── Compliance language — full rewrite ────────────────────────────────────────

def test_compliance_language_description_changed():
    v1 = load_rubric(RUBRIC_V1_PATH)
    v2 = load_rubric(RUBRIC_V2_PATH)
    assert (v1.get_dimension("compliance_language").description !=
            v2.get_dimension("compliance_language").description)
    assert "three failure modes" in v2.get_dimension("compliance_language").description.lower()


def test_compliance_language_score_for_expanded():
    rubric = load_rubric(RUBRIC_V2_PATH)
    score_for = rubric.get_dimension("compliance_language").score_for
    assert len(score_for) == 5
    joined = " ".join(score_for).lower()
    assert "diagnostic" in joined
    assert "outcome" in joined
    assert "scope" in joined


def test_compliance_language_score_against_expanded():
    rubric = load_rubric(RUBRIC_V2_PATH)
    score_against = rubric.get_dimension("compliance_language").score_against
    assert len(score_against) == 6
    joined = " ".join(score_against).lower()
    assert "diagnostic" in joined
    assert "outcome" in joined
    assert "scope" in joined


def test_compliance_language_score_anchors_present():
    rubric = load_rubric(RUBRIC_V2_PATH)
    anchors = rubric.get_dimension("compliance_language").score_anchors
    assert anchors is not None
    assert set(anchors.keys()) == {0, 1, 2, 3, 4, 5}


def test_compliance_language_anchor_content():
    rubric = load_rubric(RUBRIC_V2_PATH)
    anchors = rubric.get_dimension("compliance_language").score_anchors
    assert "auditor" in anchors[1].lower()
    assert "direct diagnostic" in anchors[0].lower() or "unauthorized" in anchors[0].lower()
    assert "boundary discipline" in anchors[5].lower() or "perfect" in anchors[5].lower()


def test_compliance_language_na_still_disallowed():
    rubric = load_rubric(RUBRIC_V2_PATH)
    dim = rubric.get_dimension("compliance_language")
    assert dim.na_allowed is False
    with pytest.raises(ValueError):
        dim.validate_score(None)


def test_compliance_language_compliance_override_trigger_preserved():
    rubric = load_rubric(RUBRIC_V2_PATH)
    dim = rubric.get_dimension("compliance_language")
    assert dim.compliance_override_trigger is True
