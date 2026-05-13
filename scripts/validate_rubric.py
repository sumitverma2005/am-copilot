"""
Validate that data/rubric/rubric-v1.yaml loads cleanly and has the expected structure.
Usage: python scripts/validate_rubric.py
"""
import sys
from pathlib import Path
import yaml

RUBRIC_PATH = Path(__file__).parent.parent / "data" / "rubric" / "rubric-v1.yaml"

REQUIRED_TOP_KEYS = {"version", "dimensions", "scoring_scale", "overall_score_formula"}
REQUIRED_DIMENSION_KEYS = {"id", "name", "weight", "na_allowed"}


def main() -> None:
    if not RUBRIC_PATH.exists():
        print(f"ERROR: {RUBRIC_PATH} not found", file=sys.stderr)
        sys.exit(1)

    with open(RUBRIC_PATH) as f:
        rubric = yaml.safe_load(f)

    missing_top = REQUIRED_TOP_KEYS - rubric.keys()
    if missing_top:
        print(f"ERROR: missing top-level keys: {missing_top}", file=sys.stderr)
        sys.exit(1)

    dimensions = rubric["dimensions"]
    print(f"Rubric version : {rubric['version']}")
    print(f"Status         : {rubric.get('status', 'N/A')}")
    print(f"Dimensions     : {len(dimensions)}")
    print()

    total_weight = 0.0
    for dim in dimensions:
        missing = REQUIRED_DIMENSION_KEYS - dim.keys()
        if missing:
            print(f"ERROR: dimension '{dim.get('id', '?')}' missing keys: {missing}", file=sys.stderr)
            sys.exit(1)
        na_flag = "N/A allowed" if dim["na_allowed"] else "always scored"
        override = "  [compliance override trigger]" if dim.get("compliance_override_trigger") else ""
        print(f"  {dim['id']:<30} weight={dim['weight']}  {na_flag}{override}")
        total_weight += dim["weight"]

    print()
    print(f"Total weight (all dims scored): {total_weight}")
    print()
    print("rubric-v1.yaml loaded successfully.")


if __name__ == "__main__":
    main()
