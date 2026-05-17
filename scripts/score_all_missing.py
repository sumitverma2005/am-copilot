#!/usr/bin/env python3
"""Score all 30 synthetic calls, skipping any that already have a result file.

Usage:
    .venv/bin/python scripts/score_all_missing.py [--dry-run]

Re-runnable: skips calls that already have data/results/<call_id>_result.json.
Reads MODEL_PROVIDER from .env — works with both bedrock and anthropic.

Sequence:
  Phase 1  Score the 25 non-fixture calls (no existing results).
           Shape validation runs on the very first result — stops if it fails.
  Phase 2  Score syn_001 in-memory, validate through ScoreResult.model_validate().
           If validation passes, replace all 5 hand-written fixtures with real
           AI output. If it fails, stop and show the validation error.
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

_ROOT = Path(__file__).parents[1]
for _p in [
    _ROOT / "packages" / "rubric-engine",
    _ROOT / "packages" / "prompt-library",
    _ROOT / "services" / "ctm-integration",
    _ROOT / "services" / "scoring-engine",
    _ROOT / "services" / "compliance-engine",
]:
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from dotenv import load_dotenv
load_dotenv(_ROOT / ".env")

MANIFEST_PATH = _ROOT / "data" / "synthetic" / "manifest.json"
RESULTS_DIR = _ROOT / "data" / "results"

_HAND_WRITTEN = {"syn_001", "syn_004", "syn_006", "syn_019", "syn_030"}
_SHAPE_VALIDATE_CALL = "syn_001"


def already_scored(call_id: str) -> bool:
    return (RESULTS_DIR / f"{call_id}_result.json").exists()


def run_pipeline(call_id: str):
    """Full scoring pipeline for one call. Returns ScoreResult."""
    from ctm_integration.normalizer import normalize
    from ctm_integration.stub_client import StubCTMClient
    from compliance_engine.detector import run_compliance_check
    from scoring_engine.score_arbitrator import ScoreArbitrator

    client = StubCTMClient()
    metadata = client.get_call_metadata(call_id)
    transcript_raw = client.get_call_transcript(call_id)
    normalized = normalize(metadata, transcript_raw)
    compliance = run_compliance_check(normalized["transcript"])
    return ScoreArbitrator().score(normalized, compliance_flags=compliance.flags)


def write_result(call_id: str, result) -> Path:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out = RESULTS_DIR / f"{call_id}_result.json"
    payload = {
        "evaluation": result.evaluation.model_dump(),
        "dimension_scores": [r.model_dump() for r in result.dimension_scores],
        "evidence_anchors": [r.model_dump() for r in result.evidence_anchors],
        "compliance_flags": [r.model_dump() for r in result.compliance_flags],
    }
    out.write_text(json.dumps(payload, indent=2))
    return out


def validate_shape(result) -> tuple[bool, str]:
    """Validate result through ScoreResult schema. Returns (ok, error_msg)."""
    from scoring_engine.models import ScoreResult
    try:
        ScoreResult.model_validate({
            "evaluation": result.evaluation.model_dump(),
            "dimension_scores": [r.model_dump() for r in result.dimension_scores],
            "evidence_anchors": [r.model_dump() for r in result.evidence_anchors],
            "compliance_flags": [r.model_dump() for r in result.compliance_flags],
        })
        return True, ""
    except Exception as exc:
        return False, str(exc)


def score_one(call_id: str, label: str, *, write: bool = True) -> tuple[bool, object | None]:
    """Score a single call. Returns (success, result_or_None)."""
    t0 = time.time()
    print(f"  {label} {call_id}", flush=True)
    try:
        result = run_pipeline(call_id)
        elapsed = time.time() - t0
        score = result.evaluation.overall_score
        model = result.evaluation.model_id
        print(f"       → {score:.0f}/100  {elapsed:.1f}s  [{model}]")
        if write:
            write_result(call_id, result)
        return True, result
    except Exception as exc:
        elapsed = time.time() - t0
        print(f"  ERROR ({elapsed:.1f}s): {exc}")
        return False, None


def main() -> None:
    dry_run = "--dry-run" in sys.argv
    force = "--force" in sys.argv
    provider = os.environ.get("MODEL_PROVIDER", "bedrock")
    rubric_version = os.environ.get("RUBRIC_VERSION", "rubric-v1")
    manifest = json.loads(MANIFEST_PATH.read_text())
    all_ids = [c["call_id"] for c in manifest["calls"]]

    if force:
        new_ids = [c for c in all_ids if c not in _HAND_WRITTEN]
    else:
        new_ids = [c for c in all_ids if c not in _HAND_WRITTEN and not already_scored(c)]
    fixture_ids = sorted(_HAND_WRITTEN)

    print(f"\nAM Copilot — Score All Missing Calls")
    print(f"Provider       : {provider}")
    print(f"Rubric version : {rubric_version}")
    print(f"Force overwrite: {'yes' if force else 'no'}")
    print(f"Total calls    : {len(all_ids)}")
    print(f"Already done   : {sum(1 for c in all_ids if already_scored(c) and c not in _HAND_WRITTEN)}")
    print(f"Phase 1        : {len(new_ids)} calls to score")
    print(f"Phase 2        : {len(fixture_ids)} fixture calls to validate and replace")
    if dry_run:
        print("\nDRY RUN — nothing will be scored.")
        print("Add --force to overwrite all existing results.")
        print("Phase 1 queue:", new_ids)
        print("Phase 2 queue:", fixture_ids)
        return

    t_total = time.time()
    ok_count = 0
    fail_count = 0

    # ── PHASE 1: non-fixture calls ─────────────────────────────────────────────
    if new_ids:
        print(f"\n── Phase 1: {len(new_ids)} new calls ──────────────────────────────────")
        for i, call_id in enumerate(new_ids, start=1):
            ok, result = score_one(call_id, f"[{i}/{len(new_ids)}]")
            if ok:
                ok_count += 1
                if i == 1:
                    valid, err = validate_shape(result)
                    if not valid:
                        print(f"\n  !! Shape validation FAILED on first result — stopping.")
                        print(f"  Error: {err}")
                        print(f"\n  This indicates a ScoreResult schema mismatch. "
                              f"Fix before proceeding with the batch.")
                        sys.exit(1)
                    print(f"  ✓ Shape validated on {call_id} — continuing batch")
            else:
                fail_count += 1
    else:
        print("\nPhase 1: all non-fixture calls already scored — skipping.")

    # ── PHASE 2: fixture calls ─────────────────────────────────────────────────
    print(f"\n── Phase 2: validate shape then replace {len(fixture_ids)} fixtures ────")
    print(f"  Scoring {_SHAPE_VALIDATE_CALL} in-memory for shape validation...")

    ok, validate_result = score_one(_SHAPE_VALIDATE_CALL, "[shape-check]", write=False)
    if not ok:
        print(f"\n  Cannot validate shape — {_SHAPE_VALIDATE_CALL} scoring failed. "
              f"Check API key and retry.")
        sys.exit(1)

    valid, err = validate_shape(validate_result)
    if not valid:
        print(f"\n  !! Shape validation FAILED — stopping. Do not replace fixtures.")
        print(f"  Validation error:\n  {err}")
        sys.exit(1)

    print(f"  ✓ Shape valid — replacing all {len(fixture_ids)} fixture files")
    for i, call_id in enumerate(fixture_ids, start=1):
        ok, result = score_one(call_id, f"[{i}/{len(fixture_ids)}]")
        if ok:
            ok_count += 1
        else:
            fail_count += 1

    # ── Summary ────────────────────────────────────────────────────────────────
    elapsed = time.time() - t_total
    total_attempted = ok_count + fail_count
    print(f"\n{'─' * 60}")
    print(f"  Scored:  {ok_count}/{total_attempted}")
    print(f"  Failed:  {fail_count}")
    print(f"  Time:    {elapsed:.0f}s total  "
          f"({elapsed / max(ok_count, 1):.1f}s/call avg)")
    print(f"  Results: data/results/  ({len(list(RESULTS_DIR.glob('*_result.json')))} files)")
    if fail_count:
        print(f"\n  Script is re-runnable — failed calls will be retried on next run.")
    else:
        print(f"\n  All calls scored. Run: .venv/bin/python scripts/analyze_disagreements.py")
    print()


if __name__ == "__main__":
    main()
