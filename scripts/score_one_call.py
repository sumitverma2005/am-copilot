#!/usr/bin/env python3
"""Score a single synthetic call end-to-end and write the result to data/results/.

Usage:
    python scripts/score_one_call.py [call_id]

    call_id defaults to syn_001.

Pipeline:
    StubCTMClient → normalize → compliance check → ScoreArbitrator → JSON result

The result JSON maps 1:1 to the DB schema (evaluations + dimension_scores +
evidence_anchors + compliance_flags). When the ORM layer is added, insertion
is a direct read → insert with no reshaping.
"""
import json
import os
import sys
from pathlib import Path

# Load .env before importing anything that reads env vars
from dotenv import load_dotenv
load_dotenv(Path(__file__).parents[1] / ".env")

# Add service/package paths (mirrors pyproject.toml pythonpath for script usage)
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

from ctm_integration.normalizer import normalize
from ctm_integration.stub_client import StubCTMClient
from compliance_engine.detector import run_compliance_check
from scoring_engine.score_arbitrator import ScoreArbitrator

RESULTS_DIR = _ROOT / "data" / "results"


def main(call_id: str = "syn_001") -> None:
    print(f"\n{'='*60}")
    print(f"  AM Copilot — scoring {call_id}")
    print(f"{'='*60}\n")

    # ── Step 1: fetch via stub client ──────────────────────────────
    print(f"[1/4] Fetching call via StubCTMClient...")
    client = StubCTMClient()
    metadata = client.get_call_metadata(call_id)
    transcript_raw = client.get_call_transcript(call_id)
    print(f"      agent: {metadata['agent']['name']}  "
          f"duration: {metadata['duration']}s  "
          f"turns: {len(transcript_raw['outline'])}")

    # ── Step 2: normalize ──────────────────────────────────────────
    print(f"\n[2/4] Normalizing...")
    normalized = normalize(metadata, transcript_raw)
    print(f"      {len(normalized['transcript'])} turns normalized")

    # ── Step 3: compliance check (deterministic, before Bedrock) ───
    print(f"\n[3/4] Running compliance check...")
    compliance_result = run_compliance_check(normalized["transcript"])
    if compliance_result.flags:
        for flag in compliance_result.flags:
            print(f"      FLAG {flag.flag_code} ({flag.severity}) "
                  f"turn {flag.turn_number}: {flag.matched_phrase!r}")
    else:
        print(f"      No compliance violations detected.")
    if compliance_result.escalation_required:
        print(f"      *** ESCALATION REQUIRED ***")

    # ── Step 4: score via Bedrock ──────────────────────────────────
    print(f"\n[4/4] Scoring via Bedrock (model: {os.environ.get('BEDROCK_MODEL_ID', '?')})...")
    print(f"      This call hits the live API — one call, not a batch.")
    arbitrator = ScoreArbitrator()
    result = arbitrator.score(normalized, compliance_flags=compliance_result.flags)

    # Attach escalation_required to evaluation row (not in DB schema but useful in JSON)
    eval_dict = result.evaluation.model_dump()
    eval_dict["escalation_required"] = compliance_result.escalation_required

    # ── Write result ───────────────────────────────────────────────
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = RESULTS_DIR / f"{call_id}_result.json"

    output = {
        "evaluation": eval_dict,
        "dimension_scores": [r.model_dump() for r in result.dimension_scores],
        "evidence_anchors": [r.model_dump() for r in result.evidence_anchors],
        "compliance_flags": [r.model_dump() for r in result.compliance_flags],
    }
    out_path.write_text(json.dumps(output, indent=2))

    # ── Print summary ──────────────────────────────────────────────
    print(f"\n{'─'*60}")
    print(f"  OVERALL SCORE:    {result.evaluation.overall_score:.0f} / 100")
    print(f"  COMPLIANCE:       {'TRIGGERED' if result.evaluation.compliance_override_triggered else 'Clean'}")
    print(f"  CONFIDENCE:       {result.evaluation.overall_confidence:.2f}")
    print(f"  RUBRIC:           {result.evaluation.rubric_version}")
    print(f"  PROMPT:           {result.evaluation.prompt_version}")
    print(f"\n  Dimension scores:")
    for dim in result.dimension_scores:
        score_str = "N/A" if dim.is_na else str(dim.raw_score)
        print(f"    {dim.dimension:<30} {score_str:>3}  (w={dim.weight})")
    print(f"\n  Manager summary:")
    print(f"    {result.evaluation.manager_summary}")
    print(f"\n  Result written → {out_path}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    call_id = sys.argv[1] if len(sys.argv) > 1 else "syn_001"
    main(call_id)
