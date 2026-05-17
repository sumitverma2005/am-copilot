#!/usr/bin/env python3
"""Compare human grades to AI scores and write a calibration analysis doc.

Usage:
    .venv/bin/python scripts/analyze_disagreements.py
        human_grades.json  +  v1 AI results  →  docs/d8-analysis.md

    .venv/bin/python scripts/analyze_disagreements.py --v2
        human_grades_v2.json  +  v1 AI results  →  docs/d8-analysis-v2.md

    .venv/bin/python scripts/analyze_disagreements.py --ai-version v2
        human_grades.json  +  v2 AI results  →  docs/d10-analysis.md

    .venv/bin/python scripts/analyze_disagreements.py --v2 --ai-version v2
        human_grades_v2.json  +  v2 AI results  →  docs/d10-analysis-v2.md

Flags are orthogonal:
    --v2              Switch human grades file (v1=human_grades.json, v2=human_grades_v2.json)
    --ai-version v2   Tag the output for v2 AI scores (changes output path and report title)
                      AI results are always read from data/results/*_result.json

Reads:
    data/human_grades.json  (or human_grades_v2.json with --v2)
    data/results/*_result.json
    data/rubric/rubric-v1.yaml

Writes:
    docs/d8-analysis.md   (default)
    docs/d8-analysis-v2.md  (--v2)
    docs/d10-analysis.md    (--ai-version v2)
    docs/d10-analysis-v2.md (--v2 --ai-version v2)
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean

import yaml

_ROOT = Path(__file__).parents[1]
RESULTS_DIR = _ROOT / "data" / "results"
GRADES_PATH = _ROOT / "data" / "human_grades.json"
RUBRIC_PATH = _ROOT / "data" / "rubric" / "rubric-v1.yaml"
OUTPUT_PATH = _ROOT / "docs" / "d8-analysis.md"

# Agreement criteria
AGREE_DIM = 1        # |human - ai| ≤ 1 on 0-5 scale
AGREE_OVERALL = 10   # |human_overall - ai_overall| ≤ 10 on 0-100

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


def load_rubric() -> tuple[dict, dict]:
    """Returns (weights, labels) dicts keyed by dimension id."""
    rubric = yaml.safe_load(RUBRIC_PATH.read_text())
    weights = {d["id"]: d["weight"] for d in rubric["dimensions"]}
    labels = {d["id"]: d["name"] for d in rubric["dimensions"]}
    return weights, labels


def load_ai_results() -> dict[str, dict]:
    results: dict[str, dict] = {}
    for path in sorted(RESULTS_DIR.glob("*_result.json")):
        data = json.loads(path.read_text())
        call_id = data["evaluation"]["call_id"]
        data["_dim_index"] = {d["dimension"]: d for d in data["dimension_scores"]}
        results[call_id] = data
    return results


def compute_human_overall(human_call: dict, weights: dict) -> float | None:
    """Rubric formula: sum(raw * weight) / sum(applicable weights) * 20."""
    weighted_sum = 0.0
    weight_sum = 0.0
    for dim_id in DIMENSION_ORDER:
        if dim_id not in human_call:
            continue
        score = human_call[dim_id]
        if score is None:
            continue
        w = weights[dim_id]
        weighted_sum += score * w
        weight_sum += w
    if weight_sum == 0:
        return None
    return round(weighted_sum / weight_sum * 20, 1)


def pct(num: int, denom: int) -> str:
    if denom == 0:
        return "—"
    return f"{round(100 * num / denom)}%"


def bias_label(avg_signed: float) -> str:
    if avg_signed > 0.2:
        return "Human↑"
    if avg_signed < -0.2:
        return "AI↑"
    return "≈equal"


def bias_note(avg_signed: float) -> str:
    if avg_signed > 0.2:
        return (
            "Human consistently scores higher than AI. "
            "Rubric high-end anchors may be too strict, or AI is missing evidence "
            "that a human listener would catch."
        )
    if avg_signed < -0.2:
        return (
            "AI consistently scores higher than human. "
            "Criteria may be too loose, or AI rewards the presence of keywords "
            "rather than execution quality."
        )
    return (
        "No consistent directional bias — disagreements are scattered. "
        "Anchor wording for this dimension is likely ambiguous at the boundary scores."
    )


def generate_report(
    grades: dict,
    ai_results: dict,
    comparable: list[str],
    dim_stats: dict,
    call_rows: list[dict],
    overall_agreements: int,
    overall_total: int,
    labels: dict,
    report_title: str = "D8 Calibration Analysis",
) -> str:
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    out: list[str] = []

    def line(s: str = "") -> None:
        out.append(s)

    line(f"# {report_title} — {today}")
    line()
    line("| | |")
    line("|---|---|")
    line(f"| Calls graded (human) | {len(grades)} |")
    line(f"| Calls with AI scores | {len(ai_results)} |")
    line(f"| Comparable (both)    | {len(comparable)} |")
    line()

    # ── Overall score agreement ────────────────────────────────────────────────
    line("## Overall Score Agreement (target: ≥80%)")
    line()
    if overall_total:
        rate = overall_agreements / overall_total
        status = "✓ PASS" if rate >= 0.80 else "✗ FAIL"
        line(
            f"{overall_agreements}/{overall_total} calls within ±10 points — "
            f"**{pct(overall_agreements, overall_total)}** — **{status}**"
        )
    else:
        line("No comparable calls with computable overall scores.")
    line()

    # ── Per-dimension table ────────────────────────────────────────────────────
    line("## Per-Dimension Agreement (target: ≥70%, criterion: |delta| ≤ 1)")
    line()
    line("| Dimension | Compared | Agreement | Avg \\|delta\\| | Bias | Status |")
    line("|---|---|---|---|---|---|")

    failing_dims: list[str] = []
    for dim_id in DIMENSION_ORDER:
        s = dim_stats[dim_id]
        label = labels[dim_id]
        if s["total"] == 0:
            line(f"| {label} | 0 | — | — | — | — |")
            continue
        rate = s["agreements"] / s["total"]
        avg_abs = mean(abs(d) for d in s["deltas"])
        avg_signed = mean(s["deltas"])
        status = "✓ PASS" if rate >= 0.70 else "✗ FAIL"
        if rate < 0.70:
            failing_dims.append(dim_id)
        line(
            f"| {label} | {s['total']} | {pct(s['agreements'], s['total'])} "
            f"| {avg_abs:.1f} | {bias_label(avg_signed)} | {status} |"
        )
    line()

    # ── Failing dimensions ─────────────────────────────────────────────────────
    line("## Dimensions Needing D9 Rubric Work")
    line()
    if not failing_dims:
        line("All dimensions passed the ≥70% threshold. Rubric v1 is well-calibrated.")
        line()
    else:
        for dim_id in failing_dims:
            s = dim_stats[dim_id]
            label = labels[dim_id]
            rate = s["agreements"] / s["total"]
            avg_abs = mean(abs(d) for d in s["deltas"])
            avg_signed = mean(s["deltas"])
            line(f"### {label}")
            line(f"- Agreement: {pct(s['agreements'], s['total'])} (target: ≥70%)")
            line(f"- Avg |delta|: {avg_abs:.1f}")
            line(f"- Avg signed delta (human − AI): {avg_signed:+.2f}")
            line(f"- {bias_note(avg_signed)}")
            line()

    # ── Per-dimension outlier calls ────────────────────────────────────────────
    line("## Outlier Calls (|delta| > 1 on any dimension)")
    line()
    outliers = [r for r in call_rows if r["max_dim_delta"] > 1]
    outliers.sort(key=lambda r: r["max_dim_delta"], reverse=True)

    if not outliers:
        line("No per-dimension deltas exceeded 1 point.")
        line()
    else:
        line("| Call | Dimension | Human | AI | Delta |")
        line("|---|---|---|---|---|")
        for row in outliers:
            sorted_dims = sorted(
                row["dim_deltas"].items(),
                key=lambda kv: abs(kv[1]),
                reverse=True,
            )
            for dim_id, delta in sorted_dims:
                if abs(delta) > 1:
                    label = labels[dim_id]
                    h = row["dim_human"][dim_id]
                    a = row["dim_ai"][dim_id]
                    sign = "+" if delta > 0 else ""
                    line(f"| {row['call_id']} | {label} | {h} | {a:.0f} | {sign}{delta} |")
        line()

    # ── Overall score outliers ─────────────────────────────────────────────────
    overall_outliers = [
        r for r in call_rows
        if "overall_delta" in r and abs(r["overall_delta"]) > 10
    ]
    if overall_outliers:
        line("## Overall Score Outliers (|delta| > 10 points)")
        line()
        line("| Call | Human Overall | AI Overall | Delta |")
        line("|---|---|---|---|")
        for row in sorted(overall_outliers, key=lambda r: abs(r["overall_delta"]), reverse=True):
            sign = "+" if row["overall_delta"] > 0 else ""
            line(
                f"| {row['call_id']} | {row['human_overall']:.0f} "
                f"| {row['ai_overall']:.0f} | {sign}{row['overall_delta']:.0f} |"
            )
        line()

    # ── Patterns and recommendations ──────────────────────────────────────────
    line("## Patterns and D9 Recommendations")
    line()
    if not failing_dims:
        line(
            "All dimensions are within calibration thresholds. "
            "D9 can focus on minor anchor refinement for dimensions "
            "closest to the 70% floor."
        )
        line()
    else:
        line(
            f"{len(failing_dims)} dimension(s) require rubric refinement on D9. "
            "Suggested focus per dimension:"
        )
        line()
        for dim_id in failing_dims:
            s = dim_stats[dim_id]
            avg_signed = mean(s["deltas"])
            label = labels[dim_id]
            if avg_signed > 0.2:
                action = "Raise the AI's effective bar — tighten score_for language, add stronger negative anchors, or add concrete behavioral examples to the 4 and 5 anchors."
            elif avg_signed < -0.2:
                action = "Lower the AI's effective bar — clarify that quality of execution matters, not just presence of keywords. Add 'score against' examples for hollow language."
            else:
                action = "Disambiguate the 2/3 and 3/4 boundary anchors — the disagreements are scattered, suggesting the middle scores are ambiguous."
            line(f"- **{label}**: {action}")
        line()

    line("---")
    line(f"*Generated by analyze_disagreements.py · {today}*")
    line()

    return "\n".join(out)


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze human vs AI score agreement.")
    parser.add_argument(
        "--v2",
        action="store_true",
        help="Use human_grades_v2.json instead of human_grades.json",
    )
    parser.add_argument(
        "--ai-version",
        choices=["v1", "v2"],
        default="v1",
        help="Tag for the AI scoring version; v2 routes output to docs/d10-analysis*.md",
    )
    args = parser.parse_args()

    human_suffix = "-v2" if args.v2 else ""
    grades_path = _ROOT / "data" / (
        "human_grades_v2.json" if args.v2 else "human_grades.json"
    )

    if args.ai_version == "v2":
        output_path = _ROOT / "docs" / f"d10-analysis{human_suffix}.md"
        report_title = "D10 Calibration Analysis (rubric-v2 AI scores)"
    else:
        output_path = _ROOT / "docs" / f"d8-analysis{human_suffix}.md"
        report_title = "D8 Calibration Analysis"

    if not grades_path.exists():
        fname = grades_path.name
        hint = "regrade_dimensions.py" if args.v2 else "grade_calls.py"
        print(f"No grades file found ({fname}). Run {hint} first.")
        return

    weights, labels = load_rubric()
    grades: dict = json.loads(grades_path.read_text())
    ai_results = load_ai_results()

    comparable = sorted(set(grades) & set(ai_results))
    if not comparable:
        print("No overlap between graded calls and AI results.")
        print(f"  Graded:     {sorted(grades)}")
        print(f"  AI results: {sorted(ai_results)}")
        return

    dim_stats: dict[str, dict] = {
        d: {"agreements": 0, "total": 0, "deltas": []} for d in DIMENSION_ORDER
    }
    call_rows: list[dict] = []
    overall_agreements = 0
    overall_total = 0

    for call_id in comparable:
        human = grades[call_id]
        dim_index: dict = ai_results[call_id]["_dim_index"]

        row: dict = {
            "call_id": call_id,
            "dim_deltas": {},
            "dim_human": {},
            "dim_ai": {},
            "max_dim_delta": 0,
        }

        for dim_id in DIMENSION_ORDER:
            human_score = human.get(dim_id)            # None = N/A
            ai_dim = dim_index.get(dim_id, {})
            ai_score = None if ai_dim.get("is_na") else ai_dim.get("raw_score")

            if human_score is not None and ai_score is not None:
                delta = human_score - ai_score
                dim_stats[dim_id]["total"] += 1
                dim_stats[dim_id]["agreements"] += int(abs(delta) <= AGREE_DIM)
                dim_stats[dim_id]["deltas"].append(delta)
                row["dim_deltas"][dim_id] = delta
                row["dim_human"][dim_id] = human_score
                row["dim_ai"][dim_id] = ai_score
                row["max_dim_delta"] = max(row["max_dim_delta"], abs(delta))

        human_overall = compute_human_overall(human, weights)
        ai_overall = ai_results[call_id]["evaluation"]["overall_score"]
        if human_overall is not None:
            overall_delta = human_overall - ai_overall
            row["human_overall"] = human_overall
            row["ai_overall"] = ai_overall
            row["overall_delta"] = overall_delta
            overall_total += 1
            if abs(overall_delta) <= AGREE_OVERALL:
                overall_agreements += 1

        call_rows.append(row)

    md = generate_report(
        grades, ai_results, comparable,
        dim_stats, call_rows,
        overall_agreements, overall_total,
        labels,
        report_title=report_title,
    )
    output_path.write_text(md)

    # ── Console summary ────────────────────────────────────────────────────────
    print(f"\nReport → {output_path}")
    print()
    print(f"  Comparable calls : {len(comparable)}")
    if overall_total:
        print(f"  Overall agreement: {pct(overall_agreements, overall_total)} (target ≥80%)")
    print()
    print("  Per-dimension:")
    for dim_id in DIMENSION_ORDER:
        s = dim_stats[dim_id]
        if s["total"] == 0:
            print(f"    {labels[dim_id]:<35}  no data")
            continue
        rate = s["agreements"] / s["total"]
        flag = "  ✗ NEEDS WORK" if rate < 0.70 else ""
        print(f"    {labels[dim_id]:<35}  {pct(s['agreements'], s['total'])}{flag}")


if __name__ == "__main__":
    main()
