from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, field_validator, model_validator


class ScaleLevel(BaseModel):
    score: int
    label: str
    anchor: str


class ScoringScale(BaseModel):
    levels: list[ScaleLevel]
    na_label: str
    na_rule: str

    @model_validator(mode="after")
    def _validate_levels(self) -> "ScoringScale":
        scores = [lvl.score for lvl in self.levels]
        seen: set[int] = set()
        duplicates: list[int] = []
        for s in scores:
            if s in seen:
                duplicates.append(s)
            seen.add(s)
        if duplicates:
            raise ValueError(
                f"scoring_scale.levels has duplicate score values: {sorted(set(duplicates))}. "
                "Each score (0–5) must appear exactly once."
            )
        missing = sorted(set(range(6)) - seen)
        if missing:
            raise ValueError(
                f"scoring_scale.levels is missing required score levels: {missing}. "
                "All six levels (0, 1, 2, 3, 4, 5) must be defined."
            )
        return self


class ComplianceOverride(BaseModel):
    pending_client_signoff: bool
    rule: str


class Dimension(BaseModel):
    id: str
    name: str
    weight: float
    na_allowed: bool
    description: str
    score_for: list[str]
    score_against: list[str]
    na_condition: Optional[str] = None
    compliance_override_trigger: bool = False
    prohibited_phrases_detected_by: Optional[str] = None

    @field_validator("weight")
    @classmethod
    def _validate_weight(cls, v: float) -> float:
        if v <= 0:
            raise ValueError(
                f"weight must be greater than 0, got {v}. "
                "Use the multiplier value from the rubric spec (e.g. 1.0 or 1.5)."
            )
        if v > 5.0:
            raise ValueError(
                f"weight must be 5.0 or less, got {v}. "
                "Check the rubric spec — no dimension has a weight above 1.5."
            )
        return v

    @field_validator("score_for", "score_against")
    @classmethod
    def _validate_non_empty(cls, v: list[str], info) -> list[str]:
        if not v:
            raise ValueError(
                f"'{info.field_name}' must contain at least one item. "
                "Add the behavioural indicators from the rubric spec."
            )
        return v

    def validate_score(self, score: Optional[int]) -> None:
        """Raise ValueError if score is invalid for this dimension."""
        if score is None:
            if not self.na_allowed:
                raise ValueError(
                    f"Dimension '{self.id}' ({self.name}) does not allow N/A. "
                    "This dimension must be scored on every call."
                )
        elif not (0 <= score <= 5):
            raise ValueError(
                f"Score {score} is out of range for dimension '{self.id}' ({self.name}). "
                "Valid scores are 0–5, or None for N/A (if the dimension allows it)."
            )


class Rubric(BaseModel):
    version: str
    description: str
    scoring_scale: ScoringScale
    overall_score_formula: str
    compliance_override: ComplianceOverride
    dimensions: list[Dimension]

    def get_dimension(self, name: str) -> Dimension:
        """Return a Dimension by id or display name. Raises KeyError if not found."""
        for dim in self.dimensions:
            if dim.id == name or dim.name == name:
                return dim
        available = [d.id for d in self.dimensions]
        raise KeyError(
            f"No dimension with id or name '{name}'. "
            f"Available dimension ids: {available}"
        )
