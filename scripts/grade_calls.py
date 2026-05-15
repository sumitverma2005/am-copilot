#!/usr/bin/env python3
"""Interactive CLI to grade 30 synthetic calls against the rubric.

Usage (always run with the project venv):
    .venv/bin/python scripts/grade_calls.py

Controls during grading:
    0-5   Score this dimension
    N     Mark dimension N/A (only allowed where rubric permits)
    s     Skip this call entirely (will reappear next session)
    q     Save progress and quit

Grades are saved to data/human_grades.json after each completed call.
Partial calls (interrupted mid-call) are discarded and restart fresh next session.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

_ROOT = Path(__file__).parents[1]
for _p in [
    _ROOT / "services" / "ctm-integration",
]:
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from ctm_integration.normalizer import normalize
from ctm_integration.stub_client import StubCTMClient

RUBRIC_PATH = _ROOT / "data" / "rubric" / "rubric-v1.yaml"
MANIFEST_PATH = _ROOT / "data" / "synthetic" / "manifest.json"
GRADES_PATH = _ROOT / "data" / "human_grades.json"

DIMENSION_ORDER = [
    "empathy_rapport",
    "insurance_verification",
    "clinical_screening",
    "urgency_triage",
    "family_caller_handling",
    "objection_handling",
    "next_step_clarity",
    "compliance_language",
]


def load_rubric() -> dict:
    return yaml.safe_load(RUBRIC_PATH.read_text())


def get_dim_spec(rubric: dict, dim_id: str) -> dict:
    for d in rubric["dimensions"]:
        if d["id"] == dim_id:
            return d
    raise KeyError(f"Dimension {dim_id!r} not found in rubric")


def load_grades() -> dict:
    if GRADES_PATH.exists():
        return json.loads(GRADES_PATH.read_text())
    return {}


def save_grades(grades: dict) -> None:
    GRADES_PATH.write_text(json.dumps(grades, indent=2))


def is_fully_graded(entry: dict) -> bool:
    return all(d in entry for d in DIMENSION_ORDER)


def fmt_ts(seconds: float) -> str:
    s = int(seconds)
    return f"{s // 60}:{s % 60:02d}"


def print_transcript(normalized: dict) -> None:
    print()
    for t in normalized["transcript"]:
        speaker = t["speaker"].title()
        print(f"[Turn {t['turn']} — {speaker} — {fmt_ts(t['timestamp_seconds'])}]")
        print(t["text"])
        print()


def print_dim_criteria(spec: dict, index: int) -> None:
    print("\n" + "─" * 72)
    weight_str = f"{spec['weight']}×"
    print(f"  DIMENSION [{index}/8]: {spec['name'].upper()}  (weight {weight_str})")
    print()
    print(f"  {spec['description'].strip()}")
    print()
    print("  SCORE FOR:")
    for item in spec.get("score_for", []):
        print(f"    + {item}")
    print()
    print("  SCORE AGAINST:")
    for item in spec.get("score_against", []):
        print(f"    − {item}")
    na_condition = spec.get("na_condition", "").strip()
    if spec.get("na_allowed") and na_condition:
        print(f"\n  N/A condition: {na_condition}")
    print()


def prompt_score(spec: dict) -> tuple[int | None, str]:
    """Prompt for a score. Returns (score, action).

    score: int 0-5, or None (meaning N/A)
    action: 'ok' | 'skip' | 'quit'
    """
    na_allowed = spec.get("na_allowed", False)
    hint = "0-5  N=N/A  s=skip call  q=quit" if na_allowed else "0-5  s=skip call  q=quit"

    while True:
        try:
            raw = input(f"  Score ({hint}): ").strip().lower()
        except EOFError:
            return None, "quit"

        if raw == "q":
            return None, "quit"
        if raw == "s":
            return None, "skip"
        if raw == "n":
            if not na_allowed:
                print(f"  N/A is not allowed for '{spec['name']}'. Enter 0-5.")
                continue
            return None, "ok"
        try:
            score = int(raw)
            if 0 <= score <= 5:
                return score, "ok"
            print("  Enter a number from 0 to 5.")
        except ValueError:
            print(f"  Unrecognized input. {hint}")


def grade_call(call_info: dict, rubric: dict) -> tuple[dict | None, str]:
    """Grade a single call interactively.

    Returns (grades_dict, action) where:
      grades_dict: {dim_id: score_or_None}  — None means N/A
      action: 'ok' | 'skip' | 'quit'
    """
    call_id = call_info["call_id"]

    print("\n" + "═" * 72)
    print(f"  CALL: {call_id}  |  Scenario: {call_info['scenario_type'].upper()}")
    print("═" * 72)

    client = StubCTMClient()
    try:
        metadata = client.get_call_metadata(call_id)
        transcript_raw = client.get_call_transcript(call_id)
        normalized = normalize(metadata, transcript_raw)
    except Exception as exc:
        print(f"\n  ERROR loading transcript: {exc}")
        print("  Skipping this call.")
        return None, "skip"

    agent_name = normalized.get("agent_name") or "?"
    duration = fmt_ts(normalized.get("duration", 0))
    turns = len(normalized["transcript"])
    print(f"\n  Agent: {agent_name}  |  Duration: {duration}  |  Turns: {turns}")

    print_transcript(normalized)

    try:
        input("  ── Press Enter to begin grading ──")
    except EOFError:
        return None, "quit"

    call_grades: dict[str, int | None] = {}

    for idx, dim_id in enumerate(DIMENSION_ORDER, start=1):
        spec = get_dim_spec(rubric, dim_id)
        print_dim_criteria(spec, idx)
        score, action = prompt_score(spec)

        if action == "quit":
            return None, "quit"
        if action == "skip":
            return None, "skip"

        call_grades[dim_id] = score  # None = N/A, int 0-5 = score

    return call_grades, "ok"


def main() -> None:
    rubric = load_rubric()
    manifest = json.loads(MANIFEST_PATH.read_text())
    all_calls: list[dict] = manifest["calls"]
    grades = load_grades()

    pending = [c for c in all_calls if not is_fully_graded(grades.get(c["call_id"], {}))]
    done_count = len(all_calls) - len(pending)

    print("\n" + "═" * 72)
    print("  AM Copilot — Human Grading CLI")
    print("═" * 72)
    print(f"\n  Calls total:     {len(all_calls)}")
    print(f"  Already graded:  {done_count}")
    print(f"  Remaining:       {len(pending)}")
    print(f"  Grades file:     {GRADES_PATH}")
    print()
    print("  Controls: 0-5=score  N=N/A  s=skip call  q=quit & save")
    print()

    if not pending:
        print("  All calls graded.")
        print("  Run: .venv/bin/python scripts/analyze_disagreements.py")
        return

    try:
        input("  Press Enter to start grading...")
    except (EOFError, KeyboardInterrupt):
        return

    for i, call_info in enumerate(pending):
        position = done_count + i + 1
        print(f"\n  [{position}/{len(all_calls)}]", end="")

        try:
            call_grades, action = grade_call(call_info, rubric)
        except KeyboardInterrupt:
            print("\n\n  Interrupted. Progress saved.")
            break

        if action == "ok" and call_grades is not None:
            grades[call_info["call_id"]] = {
                "graded_at": datetime.now(timezone.utc).isoformat(),
                **call_grades,
            }
            save_grades(grades)
            print(f"\n  ✓ Saved grades for {call_info['call_id']}.")
        elif action == "skip":
            print(f"\n  Skipped {call_info['call_id']} (will reappear next session).")
        elif action == "quit":
            print("\n  Saving and exiting...")
            break

    graded_total = sum(
        1 for c in all_calls if is_fully_graded(grades.get(c["call_id"], {}))
    )
    print(f"\n  Graded: {graded_total}/{len(all_calls)} calls")
    if graded_total < len(all_calls):
        print("  Resume:  .venv/bin/python scripts/grade_calls.py")
    else:
        print("  Analyze: .venv/bin/python scripts/analyze_disagreements.py")


if __name__ == "__main__":
    main()
