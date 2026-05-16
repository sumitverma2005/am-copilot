"""Structural tests for prompt_v2 — no live API calls."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
import yaml

_ROOT = Path(__file__).parents[3]
for _p in [
    _ROOT / "packages" / "rubric-engine",
    _ROOT / "packages" / "prompt-library",
]:
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from rubric_engine import load_rubric
from prompt_library.evaluation.prompt_v1 import (
    PROMPT_VERSION as V1_VERSION,
    SYSTEM_PROMPT as V1_SYSTEM,
    build_evaluation_prompt as build_v1,
    format_rubric as format_rubric_v1,
)
from prompt_library.evaluation.prompt_v2 import (
    PROMPT_VERSION as V2_VERSION,
    SYSTEM_PROMPT as V2_SYSTEM,
    build_evaluation_prompt as build_v2,
    format_rubric as format_rubric_v2,
)

RUBRIC_V1 = load_rubric(_ROOT / "data" / "rubric" / "rubric-v1.yaml")
RUBRIC_V2 = load_rubric(_ROOT / "data" / "rubric" / "rubric-v2.yaml")

SAMPLE_TURNS = [
    {"turn": 1, "speaker": "agent", "timestamp_seconds": 0, "text": "Hello, how can I help?"},
    {"turn": 2, "speaker": "caller", "timestamp_seconds": 5, "text": "I need help with treatment."},
]


# ── Version strings ────────────────────────────────────────────────────────────

def test_v2_version_string_differs_from_v1():
    assert V2_VERSION != V1_VERSION
    assert "v2" in V2_VERSION


def test_v1_version_string():
    assert "v1" in V1_VERSION


# ── System prompt unchanged ────────────────────────────────────────────────────

def test_system_prompt_identical_across_versions():
    assert V1_SYSTEM == V2_SYSTEM


# ── build_evaluation_prompt structure ─────────────────────────────────────────

def test_v2_prompt_contains_rubric_version_header():
    prompt = build_v2(SAMPLE_TURNS, RUBRIC_V2)
    assert "RUBRIC VERSION: rubric-v2" in prompt


def test_v1_prompt_contains_rubric_version_header():
    prompt = build_v1(SAMPLE_TURNS, RUBRIC_V1)
    assert "RUBRIC VERSION: rubric-v1" in prompt


def test_v2_prompt_contains_all_eight_dimension_ids():
    prompt = build_v2(SAMPLE_TURNS, RUBRIC_V2)
    for dim_id in (
        "empathy_rapport", "insurance_verification", "clinical_screening",
        "urgency_triage", "family_caller_handling", "objection_handling",
        "next_step_clarity", "compliance_language",
    ):
        assert dim_id in prompt, f"dimension id {dim_id!r} missing from prompt"


def test_v2_prompt_contains_transcript_turns():
    prompt = build_v2(SAMPLE_TURNS, RUBRIC_V2)
    assert "Hello, how can I help?" in prompt
    assert "AGENT" in prompt
    assert "CALLER" in prompt


def test_v2_prompt_json_schema_present():
    prompt = build_v2(SAMPLE_TURNS, RUBRIC_V2)
    assert '"dimension_scores"' in prompt
    assert '"manager_summary"' in prompt
    assert '"overall_confidence"' in prompt


# ── format_rubric — score_anchors rendered in v2, absent in v1 ────────────────

def test_v2_format_rubric_includes_score_anchors_for_compliance():
    text = format_rubric_v2(RUBRIC_V2)
    assert "Score ANCHORS" in text
    assert "auditor" in text.lower()


def test_v1_format_rubric_has_no_score_anchors_section():
    text = format_rubric_v1(RUBRIC_V1)
    assert "Score ANCHORS" not in text


def test_v2_format_rubric_all_six_anchor_levels_present():
    text = format_rubric_v2(RUBRIC_V2)
    anchors_section = text[text.index("Score ANCHORS"):]
    for level in range(6):
        assert f"    {level}:" in anchors_section, f"Anchor level {level} missing from rendered rubric"


# ── Objection handling definition rendered ────────────────────────────────────

def test_v2_format_rubric_objection_handling_has_definition():
    text = format_rubric_v2(RUBRIC_V2)
    assert "transactional" in text.lower()
    assert "skepticism" in text.lower()


def test_v1_format_rubric_objection_handling_no_definition():
    text = format_rubric_v1(RUBRIC_V1)
    # "skepticism" and "reputational" are v2-only definition additions
    assert "skepticism" not in text.lower()
    assert "reputational" not in text.lower()


# ── Compliance language score_against rendered ────────────────────────────────

def test_v2_compliance_score_against_diagnostic_label_present():
    text = format_rubric_v2(RUBRIC_V2)
    assert "benzo dependence" in text.lower()


def test_v2_compliance_score_against_outcome_promise_present():
    text = format_rubric_v2(RUBRIC_V2)
    assert "guarantee of success" in text.lower()


def test_v2_compliance_score_against_scope_overreach_present():
    text = format_rubric_v2(RUBRIC_V2)
    assert "withdrawal pathways" in text.lower()
