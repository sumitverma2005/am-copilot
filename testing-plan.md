# Testing & QA Plan
# AM Copilot — Phase A

**Version:** 1.0
**Status:** Approved
**Last updated:** 2026-05

---

## 1. Overview

Phase A has two distinct testing moments:

| When | What | Pass criterion |
|---|---|---|
| D8 — internal QA | Automated Pytest suite scores 30 synthetic calls against gold-standard labels | AI scores within ±1 of gold labels on ≥80% of calls overall, ≥70% per dimension |
| D13 — post-refinement check | Rescore with rubric-v2, verify success bar still met | Same as D8 but with client's blind grades as the reference |

D8 is fully automated. No manual scoring required.
D13 requires comparing AI scores to Alyssa's D11 blind grades.

---

## 2. D8 automated QA suite

### Location
`tests/gold-standard/test_scoring_agreement.py`

### What it does

1. Loads all 30 synthetic calls from `data/synthetic/`
2. Runs the full evaluation pipeline on each call (scoring + compliance + evidence)
3. Compares AI scores to gold-standard labels in each call's `gold_labels` field
4. Calculates per-call and per-dimension agreement rates
5. Asserts the success bar thresholds
6. Outputs a disagreement report for analysis

### Agreement definition

A score is "in agreement" if the AI score is within ±1 of the gold-standard expected score.

```
gold_label = 4, ai_score = 3 → IN AGREEMENT (delta = 1)
gold_label = 4, ai_score = 2 → NOT IN AGREEMENT (delta = 2)
gold_label = null (N/A), ai_score = null → IN AGREEMENT
gold_label = null (N/A), ai_score = 3 → NOT IN AGREEMENT
```

### Test structure

```python
# tests/gold-standard/test_scoring_agreement.py

import pytest
import json
from pathlib import Path
from services.evaluation_worker.pipeline import run_evaluation_pipeline

SYNTHETIC_DIR = Path("data/synthetic")
OVERALL_AGREEMENT_THRESHOLD = 0.80   # 80%
DIMENSION_AGREEMENT_THRESHOLD = 0.70  # 70%

DIMENSIONS = [
    "empathy_rapport",
    "insurance_verification",
    "clinical_screening",
    "urgency_triage",
    "family_caller_handling",
    "objection_handling",
    "next_step_clarity",
    "compliance_language",
]

def load_synthetic_calls():
    calls = []
    for path in sorted(SYNTHETIC_DIR.glob("syn_*.json")):
        with open(path) as f:
            calls.append(json.load(f))
    return calls

def scores_agree(gold: int | None, ai: int | None) -> bool:
    if gold is None and ai is None:
        return True
    if gold is None or ai is None:
        return False   # one is N/A, other isn't
    return abs(gold - ai) <= 1

class TestScoringAgreement:

    @pytest.fixture(scope="class")
    def evaluation_results(self):
        calls = load_synthetic_calls()
        results = []
        for call in calls:
            ai_result = run_evaluation_pipeline(call)
            results.append({
                "call_id": call["call_id"],
                "gold": call["gold_labels"]["expected_scores"],
                "ai": ai_result.dimension_scores,
                "gold_overall": call["gold_labels"]["expected_overall"],
                "ai_overall": ai_result.overall_score,
            })
        return results

    def test_overall_agreement_rate(self, evaluation_results):
        """At least 80% of calls must have overall score within ±5 of gold label."""
        agreements = sum(
            1 for r in evaluation_results
            if abs(r["gold_overall"] - r["ai_overall"]) <= 5
        )
        rate = agreements / len(evaluation_results)
        assert rate >= OVERALL_AGREEMENT_THRESHOLD, (
            f"Overall agreement {rate:.1%} below threshold {OVERALL_AGREEMENT_THRESHOLD:.0%}. "
            f"Disagreements: {len(evaluation_results) - agreements}/{len(evaluation_results)}"
        )

    @pytest.mark.parametrize("dimension", DIMENSIONS)
    def test_dimension_agreement_rate(self, evaluation_results, dimension):
        """Each dimension must agree on at least 70% of applicable calls."""
        applicable = [
            r for r in evaluation_results
            if r["gold"].get(dimension) is not None
        ]
        if not applicable:
            pytest.skip(f"No applicable calls for dimension: {dimension}")

        agreements = sum(
            1 for r in applicable
            if scores_agree(r["gold"].get(dimension), r["ai"].get(dimension))
        )
        rate = agreements / len(applicable)
        assert rate >= DIMENSION_AGREEMENT_THRESHOLD, (
            f"{dimension}: agreement {rate:.1%} below threshold "
            f"{DIMENSION_AGREEMENT_THRESHOLD:.0%} "
            f"({agreements}/{len(applicable)} calls)"
        )

    def test_compliance_override_correct(self, evaluation_results):
        """All compliance-failure calls must have overall score = 0 if override is active."""
        calls = load_synthetic_calls()
        compliance_failure_calls = [
            c for c in calls
            if c["gold_labels"]["compliance_override_triggered"]
        ]
        for call in compliance_failure_calls:
            result = next(
                r for r in evaluation_results
                if r["call_id"] == call["call_id"]
            )
            assert result["ai_overall"] == 0, (
                f"Call {call['call_id']}: compliance override should set overall to 0, "
                f"got {result['ai_overall']}"
            )

    def test_na_dimensions_excluded(self, evaluation_results):
        """N/A dimensions must not contribute to the weighted average."""
        # Verify family_caller_handling N/A calls don't count family_caller in average
        calls = load_synthetic_calls()
        for call in calls:
            if call["gold_labels"]["expected_scores"]["family_caller_handling"] is None:
                result = next(
                    r for r in evaluation_results
                    if r["call_id"] == call["call_id"]
                )
                # If N/A was correctly handled, the AI score for this dimension is also None
                assert result["ai"].get("family_caller_handling") is None, (
                    f"Call {call['call_id']}: family_caller_handling should be N/A"
                )
```

---

## 3. Additional test suites

### Compliance engine tests
`tests/compliance/test_rules.py`

```python
# Every regex rule must fire on the phrase it's designed to catch
# and must NOT fire on clean alternatives

RULE_FIXTURES = [
    # (phrase, flag_code, should_match)
    ("it sounds like you have a dependency problem", "DIAG_CLAIM", True),
    ("I can hear this has been really hard", "DIAG_CLAIM", False),
    ("our program will get you better", "OUTCOME_GUARANTEE", True),
    ("many of our clients make significant progress", "OUTCOME_GUARANTEE", False),
    ("I think you need residential treatment", "CLINICAL_SCOPE", True),
    ("our admissions team will assess the right level of care for you", "CLINICAL_SCOPE", False),
]
```

### Scoring engine unit tests
`tests/scoring/test_score_arbitrator.py`

```python
# N/A exclusion
def test_na_excluded_from_weighted_average():
    scores = {
        "empathy_rapport": 4,        # weight 1.5
        "insurance_verification": 3,  # weight 1.0
        "family_caller_handling": None,  # N/A — excluded
        ...
    }
    result = calculate_weighted_score(scores)
    # family_caller_handling weight must not appear in denominator

# Compliance override
def test_compliance_override_zeroes_overall():
    scores = {"compliance_language": 0, "empathy_rapport": 5, ...}
    result = calculate_weighted_score(scores, compliance_override=True)
    assert result == 0

# Score formula
def test_weighted_average_calculation():
    # Worked example from rubric-spec.md section 5
    scores = {
        "empathy_rapport": 4,
        "insurance_verification": 3,
        "clinical_screening": 4,
        "urgency_triage": 3,
        "family_caller_handling": None,
        "objection_handling": 4,
        "next_step_clarity": 5,
        "compliance_language": 4,
    }
    assert calculate_weighted_score(scores) == 78
```

---

## 4. D13 — post-refinement regression check

After D12 rubric refinement:

1. Rescore all 30 calls with rubric-v2 and prompt-v2 (if changed)
2. Compare new AI scores against Alyssa's D11 blind grades (not gold labels)
3. Assert ≥80% overall agreement, ≥70% per dimension
4. Also verify rubric-v2 did not regress the D8 wins:
   - Run D8 suite against rubric-v2 scores
   - Agreement rate must not drop below D8 baseline by more than 5 percentage points

### D13 script

```bash
pytest tests/gold-standard/test_scoring_agreement.py \
  --rubric-version rubric-v2 \
  --reference client_grades_d11.json \
  -v --tb=short
```

The `--reference` flag switches the agreement comparison from gold labels to
Alyssa's D11 grades. Both references must independently meet the success bar.

---

## 5. Test execution

```bash
# Run full test suite
pytest tests/ -v

# Run only D8 QA suite
pytest tests/gold-standard/ -v

# Run compliance rule tests only
pytest tests/compliance/ -v

# Run with coverage
pytest tests/ --cov=services --cov-report=term-missing
```

---

## 6. CI integration

```yaml
# .github/workflows/ci.yml
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -r requirements-dev.txt
      - run: pytest tests/ -v --tb=short
```

Gold-standard tests (`tests/gold-standard/`) are excluded from CI because they
require a live Bedrock connection. They run manually on D8 and D13 only.

```yaml
# In pytest.ini or pyproject.toml
[pytest]
markers =
    bedrock: marks tests that require a live Bedrock connection (deselect with -m "not bedrock")
```
