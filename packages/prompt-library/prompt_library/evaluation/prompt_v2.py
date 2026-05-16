"""Evaluation prompt — prompt-v2.

Mirrors prompt_v1.py with one change: format_rubric renders score_anchors
when present on a dimension (added for compliance_language in rubric-v2).
All other wording, output format, and JSON schema are unchanged.

Do NOT modify wording, structure, or output format.
Increment to prompt_v3.py on any change.
"""
from __future__ import annotations

PROMPT_VERSION = "prompt-v2"

SYSTEM_PROMPT = (
    "You are an expert admissions call quality evaluator for a behavioral-health treatment centre.\n"
    "\n"
    "You evaluate intake calls against a structured rubric and produce scores with evidence.\n"
    "You are precise, fair, and grounded in the transcript — you never infer beyond what was said.\n"
    "\n"
    "Output format: You must return ONLY valid JSON matching the schema below. No preamble,\n"
    "no explanation, no markdown. Just the JSON object."
)


def build_evaluation_prompt(transcript_turns: list[dict], rubric: object) -> str:
    """Build the user-turn evaluation prompt.

    Args:
        transcript_turns: list of normalized turn dicts (turn, speaker, timestamp_seconds, text)
        rubric:           loaded Rubric object from rubric_engine

    Returns:
        Formatted user-turn string. System prompt is separate (SYSTEM_PROMPT constant).
    """
    transcript_text = format_transcript(transcript_turns)
    rubric_text = format_rubric(rubric)

    return f"""
Evaluate the following admissions intake call transcript against the rubric provided.

RUBRIC:
{rubric_text}

TRANSCRIPT:
{transcript_text}

INSTRUCTIONS:
- Score each applicable dimension 0–5 using the rubric anchors
- Use null for dimensions that are not applicable to this call
- Identify 1–3 transcript spans that support each score
- Each span must include the turn number, timestamp, speaker, and quoted text
- Provide a brief rationale (1–2 sentences) for each dimension score
- Provide a coaching note (1 sentence) for dimensions scoring below 4
- Rate your confidence in each score: high (0.85–1.0), medium (0.65–0.84), low (0.0–0.64)

Return ONLY this JSON structure:

{{
  "dimension_scores": {{
    "empathy_rapport": {{
      "score": <int 0-5 or null>,
      "rationale": "<string>",
      "coaching_note": "<string or null>",
      "confidence": <float 0.0-1.0>,
      "evidence": [
        {{
          "turn": <int>,
          "timestamp_seconds": <int>,
          "speaker": "<agent|caller>",
          "text": "<quoted span, max 200 chars>",
          "relevance_rank": <int 1-3>
        }}
      ]
    }},
    "insurance_verification": {{ ... }},
    "clinical_screening": {{ ... }},
    "urgency_triage": {{ ... }},
    "family_caller_handling": {{ ... }},
    "objection_handling": {{ ... }},
    "next_step_clarity": {{ ... }},
    "compliance_language": {{ ... }}
  }},
  "manager_summary": "<2–3 sentence plain-English summary of this call for a manager>",
  "overall_confidence": <float 0.0-1.0>
}}
"""


def format_transcript(turns: list[dict]) -> str:
    """Mechanical formatting of normalized transcript turns to a text block.

    Format (verbatim from prompt-library.md section 6):
        [0000s] AGENT: text
        [0045s] CALLER: text
    """
    lines = []
    for turn in turns:
        speaker = turn["speaker"].upper()
        ts = turn["timestamp_seconds"]
        text = turn["text"]
        lines.append(f"[{int(ts):04d}s] {speaker}: {text}")
    return "\n".join(lines)


def format_rubric(rubric: object) -> str:
    """Mechanical formatting of a Rubric object to a compact text block.

    Renders rubric content exactly as defined in rubric-v2.yaml:
    - scoring scale levels with their anchors
    - each dimension's id, weight, na_allowed, description, score_for, score_against
    - score_anchors when present (added in rubric-v2 for compliance_language)

    No instructions, no rewording, no editorializing. Data only.
    """
    lines: list[str] = []

    lines.append(f"RUBRIC VERSION: {rubric.version}")
    lines.append("")

    lines.append("SCORING SCALE:")
    for level in sorted(rubric.scoring_scale.levels, key=lambda l: l.score, reverse=True):
        lines.append(f"  {level.score} ({level.label}): {level.anchor}")
    lines.append(f"  N/A: {rubric.scoring_scale.na_rule}")
    lines.append("")

    lines.append("DIMENSIONS:")
    for dim in rubric.dimensions:
        na_str = "yes" if dim.na_allowed else "no"
        lines.append(f"\n[{dim.id}]  name={dim.name!r}  weight={dim.weight}  na_allowed={na_str}")
        lines.append(f"  Description: {dim.description.strip()}")
        lines.append("  Score FOR:")
        for item in dim.score_for:
            lines.append(f"    - {item}")
        lines.append("  Score AGAINST:")
        for item in dim.score_against:
            lines.append(f"    - {item}")
        if dim.score_anchors:
            lines.append("  Score ANCHORS (per level):")
            for level in sorted(dim.score_anchors.keys(), reverse=True):
                lines.append(f"    {level}: {dim.score_anchors[level]}")
        if dim.na_condition:
            lines.append(f"  N/A condition: {dim.na_condition}")

    return "\n".join(lines)
