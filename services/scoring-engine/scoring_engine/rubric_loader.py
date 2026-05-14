"""Rubric loader for the scoring engine.

Thin wrapper — delegates entirely to rubric_engine.load_rubric().
Resolves the rubric file path from RUBRIC_VERSION env var.
Does not duplicate any rubric logic.
"""
from __future__ import annotations

import os
from pathlib import Path

from rubric_engine import Rubric, load_rubric

_RUBRIC_DIR = Path(__file__).parents[3] / "data" / "rubric"


def load_rubric_for_scoring() -> Rubric:
    """Load the active rubric version as set by RUBRIC_VERSION env var."""
    version = os.environ.get("RUBRIC_VERSION", "rubric-v1")
    path = _RUBRIC_DIR / f"{version}.yaml"
    return load_rubric(path)
