#!/usr/bin/env python3
"""Targeted re-grade CLI: 5 calls × 3 failing dimensions = 15 judgments.

Re-grades urgency_triage, objection_handling, compliance_language only.
Saves to data/human_grades_v2.json — v1 grades are never modified.

Usage:
    .venv/bin/python scripts/regrade_dimensions.py

Controls:
    0-5   New score for this dimension
    N     Mark N/A (only where rubric permits)
    k     Keep original v1 grade unchanged
    q     Save completed calls and quit (partial call is discarded)
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml

_ROOT = Path(__file__).parents[1]
for _p in [_ROOT / "services" / "ctm-integration"]:
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from ctm_integration.normalizer import normalize
from ctm_integration.stub_client import StubCTMClient

RUBRIC_PATH = _ROOT / "data" / "rubric" / "rubric-v1.yaml"
MANIFEST_PATH = _ROOT / "data" / "synthetic" / "manifest.json"
GRADES_V1_PATH = _ROOT / "data" / "human_grades.json"
GRADES_V2_PATH = _ROOT / "data" / "human_grades_v2.json"

TARGET_CALLS = ["syn_001", "syn_002", "syn_028", "syn_029", "syn_030"]
TARGET_DIMS = ["urgency_triage", "objection_handling", "compliance_language"]

ALL_DIMS = [
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
    raise KeyError(f"Dimension {dim_id!r} not found")


def load_grades(path: Path) -> dict:
    if path.exists():
        return json.loads(path.read_text())
    return {}


def save_grades(grades: dict, path: Path) -> None:
    path.write_text(json.dumps(grades, indent=2))


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


def print_dim_criteria(spec: dict, index: int, total: int) -> None:
    print("\n" + "─" * 72)
    print(f"  DIMENSION [{index}/{total}]: {spec['name'].upper()}")
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


def prompt_regrade(spec: dict, original: int | None) -> tuple[int | None, str]:
    """Prompt for a re-grade. Returns (score, action).

    score: int 0-5 | None (N/A) | original value (keep)
    action: 'ok' | 'quit'
    """
    na_allowed = spec.get("na_allowed", False)
    orig_display = "N/A" if original is None else str(original)
    print(f"  Your original grade: {orig_display}")

    hint_parts = ["0-5"]
    if na_allowed:
        hint_parts.append("N=N/A")
    hint_parts += ["k=keep", "q=quit"]
    hint = "  ".join(hint_parts)

    while True:
        try:
            raw = input(f"  New score ({hint}): ").strip().lower()
        except EOFError:
            return None, "quit"

        if raw == "q":
            return None, "quit"
        if raw == "k":
            return original, "ok"
        if raw == "n":
            if not na_allowed:
                print(f"  N/A not allowed for '{spec['name']}'. Enter 0-5 or k.")
                continue
            return None, "ok"
        try:
            score = int(raw)
            if 0 <= score <= 5:
                return score, "ok"
            print("  Enter a number from 0 to 5.")
        except ValueError:
            print(f"  Unrecognized input. Valid: {hint}")


def regrade_call(
    call_info: dict, rubric: dict, v1_entry: dict
) -> tuple[dict | None, str]:
    """Re-grade the 3 target dims for one call interactively.

    Returns (new_scores, action):
      new_scores: {dim_id: score} for TARGET_DIMS only, or None
      action: 'ok' | 'skip' | 'quit'
    """
    call_id = call_info["call_id"]
    scenario = call_info.get("scenario_type", "unknown").upper()

    print("\n" + "═" * 72)
    print(f"  CALL: {call_id}  |  Scenario: {scenario}")
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
        input("  ── Press Enter to begin re-grading ──")
    except EOFError:
        return None, "quit"

    new_scores: dict[str, int | None] = {}

    for idx, dim_id in enumerate(TARGET_DIMS, start=1):
        spec = get_dim_spec(rubric, dim_id)
        print_dim_criteria(spec, idx, len(TARGET_DIMS))
        original = v1_entry.get(dim_id)
        score, action = prompt_regrade(spec, original)

        if action == "quit":
            return None, "quit"

        new_scores[dim_id] = score

    return new_scores, "ok"


def build_v2_entry(v1_entry: dict, new_scores: dict) -> dict:
    """5 unchanged dims copied from v1 + 3 re-graded dims + updated timestamp."""
    entry: dict = {"graded_at": datetime.now(timezone.utc).isoformat()}
    for dim_id in ALL_DIMS:
        if dim_id in new_scores:
            entry[dim_id] = new_scores[dim_id]
        else:
            entry[dim_id] = v1_entry.get(dim_id)
    return entry


def main() -> None:
    rubric = load_rubric()
    manifest = json.loads(MANIFEST_PATH.read_text())
    call_index: dict[str, dict] = {c["call_id"]: c for c in manifest["calls"]}

    v1_grades = load_grades(GRADES_V1_PATH)
    v2_grades = load_grades(GRADES_V2_PATH)

    pending = [c for c in TARGET_CALLS if c not in v2_grades]
    done_count = len(TARGET_CALLS) - len(pending)

    print("\n" + "═" * 72)
    print("  AM Copilot — Targeted Re-grade CLI")
    print("═" * 72)
    print(f"\n  Target calls:  {', '.join(TARGET_CALLS)}")
    print(f"  Dimensions:    {', '.join(TARGET_DIMS)}")
    print(f"  Already done:  {done_count}/{len(TARGET_CALLS)}")
    print(f"  Remaining:     {len(pending)}")
    print(f"  Output file:   {GRADES_V2_PATH}")
    print()
    print("  Controls: 0-5=score  N=N/A  k=keep original  q=quit & save")
    print("  Note: q discards the current call's partial answers.")
    print()

    if not pending:
        print("  All target calls re-graded.")
        print("  Run: .venv/bin/python scripts/analyze_disagreements.py --v2")
        return

    try:
        input("  Press Enter to start...")
    except (EOFError, KeyboardInterrupt):
        return

    for i, call_id in enumerate(pending):
        call_info = call_index.get(call_id)
        if call_info is None:
            print(f"\n  WARNING: {call_id} not found in manifest, skipping.")
            continue

        v1_entry = v1_grades.get(call_id, {})
        position = done_count + i + 1
        print(f"\n  [{position}/{len(TARGET_CALLS)}]", end="")

        try:
            new_scores, action = regrade_call(call_info, rubric, v1_entry)
        except KeyboardInterrupt:
            print("\n\n  Interrupted. Progress saved.")
            break

        if action == "ok" and new_scores is not None:
            v2_grades[call_id] = build_v2_entry(v1_entry, new_scores)
            save_grades(v2_grades, GRADES_V2_PATH)
            print(f"\n  ✓ Saved re-grades for {call_id}.")
        elif action == "quit":
            print("\n  Saving completed calls and exiting...")
            break

    done_total = len(v2_grades)
    print(f"\n  Re-graded: {done_total}/{len(TARGET_CALLS)} calls")
    if done_total < len(TARGET_CALLS):
        print("  Resume:  .venv/bin/python scripts/regrade_dimensions.py")
    else:
        print("  Analyze: .venv/bin/python scripts/analyze_disagreements.py --v2")


if __name__ == "__main__":
    main()
