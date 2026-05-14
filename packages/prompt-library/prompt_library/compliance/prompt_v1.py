"""Compliance contextual reasoning prompt — prompt-v1.

Ported verbatim from docs/prompt-library.md section 3.
Do NOT modify wording, structure, or output format.
Increment to prompt_v2.py on any change.

IMPORTANT: This prompt runs AFTER the deterministic compliance pass has flagged a phrase.
The LLM cannot un-flag what the rules engine flagged. It only explains the context.
"""
from __future__ import annotations

PROMPT_VERSION = "prompt-v1"


def build_compliance_reasoning_prompt(
    flagged_phrase: str,
    flag_code: str,
    context_turns: list[dict],
    flag_description: str,
) -> str:
    """Build the compliance contextual reasoning prompt.

    Args:
        flagged_phrase:   the exact matched phrase from the transcript
        flag_code:        e.g. 'DIAG_CLAIM'
        context_turns:    3 turns before and after the flagged turn
        flag_description: human-readable description from the rule definition

    Returns:
        Formatted prompt string (no separate system prompt for this call).
    """
    context_text = _format_turns(context_turns)

    return f"""
A compliance detection system has flagged the following phrase in an admissions intake call:

FLAGGED PHRASE: "{flagged_phrase}"
FLAG TYPE: {flag_code} — {flag_description}

SURROUNDING CONTEXT (3 turns before and after):
{context_text}

Provide a brief contextual explanation (2–3 sentences) of:
1. Why this phrase is a compliance concern in a behavioral-health admissions context
2. What the agent should have said instead

Return ONLY this JSON:
{{
  "contextual_explanation": "<string>",
  "suggested_alternative": "<string>"
}}
"""


def _format_turns(turns: list[dict]) -> str:
    lines = []
    for turn in turns:
        speaker = turn["speaker"].upper()
        ts = turn["timestamp_seconds"]
        text = turn["text"]
        lines.append(f"[{int(ts):04d}s] {speaker}: {text}")
    return "\n".join(lines)
