# Prompt Library Specification
# AM Copilot — Phase A

**Version:** 1.0
**Status:** Approved
**Last updated:** 2026-05

---

## 1. Versioning rules

- Every prompt has a version: `prompt-v1`, `prompt-v2`, etc.
- Prompt version is stored on every evaluation record alongside rubric version and model ID
- Never edit a prompt in place — always create a new version file
- Increment version on any change to wording, structure, or output format
- The active version is controlled by the `PROMPT_VERSION` environment variable

---

## 2. Prompt 1 — Call evaluation (main scoring prompt)

**File:** `packages/prompt-library/evaluation/prompt-v1.py`
**Used by:** `services/scoring-engine/scorer.py`
**Model:** Claude Sonnet 4.5 via Bedrock
**Version:** prompt-v1

### Purpose
Score a call transcript across all 8 rubric dimensions. Return structured JSON.

### System prompt

```
You are an expert admissions call quality evaluator for a behavioral-health treatment centre.

You evaluate intake calls against a structured rubric and produce scores with evidence.
You are precise, fair, and grounded in the transcript — you never infer beyond what was said.

Output format: You must return ONLY valid JSON matching the schema below. No preamble,
no explanation, no markdown. Just the JSON object.
```

### User prompt template

```python
def build_evaluation_prompt(transcript_turns: list[dict], rubric: dict) -> str:
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
```

### Output parsing

```python
import json
from pydantic import BaseModel

class EvidenceSnippet(BaseModel):
    turn: int
    timestamp_seconds: int
    speaker: str
    text: str
    relevance_rank: int

class DimensionResult(BaseModel):
    score: int | None        # None = N/A
    rationale: str
    coaching_note: str | None
    confidence: float
    evidence: list[EvidenceSnippet]

class EvaluationResult(BaseModel):
    dimension_scores: dict[str, DimensionResult]
    manager_summary: str
    overall_confidence: float

def parse_evaluation_response(raw_text: str) -> EvaluationResult:
    # Strip any accidental markdown fences
    clean = raw_text.strip().removeprefix("```json").removesuffix("```").strip()
    data = json.loads(clean)
    return EvaluationResult(**data)
```

---

## 3. Prompt 2 — Compliance contextual reasoning

**File:** `packages/prompt-library/compliance/prompt-v1.py`
**Used by:** `services/compliance-engine/detector.py`
**Model:** Claude Sonnet 4.5 via Bedrock
**Version:** prompt-v1

### Purpose
After the deterministic compliance pass has identified a flagged phrase, this prompt
provides contextual reasoning for the evidence record. It does NOT determine whether
a violation occurred — that is decided by the deterministic rules.

### Important
This prompt runs AFTER the regex/rules engine has already flagged a phrase.
The LLM cannot un-flag what the rules engine flagged. It only explains the context.

### Prompt template

```python
def build_compliance_reasoning_prompt(
    flagged_phrase: str,
    flag_code: str,
    context_turns: list[dict],   # 3 turns before and after the flagged turn
    flag_description: str
) -> str:
    context_text = format_turns(context_turns)

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
```

---

## 4. Prompt 3 — Evidence extraction (standalone)

**File:** `packages/prompt-library/evidence/prompt-v1.py`
**Used by:** `services/evidence-engine/extractor.py`
**Version:** prompt-v1

### Purpose
For dimensions where the main evaluation prompt produced low-confidence evidence,
this prompt re-runs evidence extraction with tighter focus.

Only invoked when a dimension's evidence confidence is below 0.65.

### Prompt template

```python
def build_evidence_extraction_prompt(
    dimension: str,
    dimension_description: str,
    score: int,
    transcript_turns: list[dict]
) -> str:
    transcript_text = format_transcript(transcript_turns)

    return f"""
You are extracting evidence from a call transcript to support a specific quality score.

DIMENSION: {dimension}
DESCRIPTION: {dimension_description}
SCORE ASSIGNED: {score}/5

TRANSCRIPT:
{transcript_text}

Find 1–3 transcript spans that most directly support this score of {score}.
Focus on the most specific, quotable evidence. Prefer agent turns that show the behaviour
being scored (or its absence).

Return ONLY this JSON:
{{
  "evidence": [
    {{
      "turn": <int>,
      "timestamp_seconds": <int>,
      "speaker": "<agent|caller>",
      "text": "<quoted span, max 200 chars>",
      "relevance_rank": <int 1-3>,
      "explanation": "<1 sentence: why this span supports the score>"
    }}
  ]
}}
"""
```

---

## 5. Compliance detection rules (deterministic — no LLM)

These rules run in `services/compliance-engine/rules.py` before any LLM call.
A regex match on any of these patterns assigns a score of 0 to Dimension 8.

```python
import re

COMPLIANCE_RULES = [
    {
        "flag_code": "DIAG_CLAIM",
        "severity": "critical",
        "patterns": [
            r"\b(you have|sounds like you have|it sounds like|you['']re dealing with)\b.{0,30}\b(addiction|dependency|disorder|disease|condition)\b",
            r"\bI think you (have|are|might be)\b.{0,20}\b(addict|dependent|alcoholic)\b",
            r"\bwhat you('re| are) describing (is|sounds like)\b",
            r"\bthat('s| is) (classic|typical|textbook)\b",
        ],
        "description": "Agent made a diagnostic claim about the caller or patient"
    },
    {
        "flag_code": "OUTCOME_GUARANTEE",
        "severity": "critical",
        "patterns": [
            r"\b(we('ll| will)|you('ll| will)) (be fine|get better|recover|be cured|be okay)\b",
            r"\bour program (cures|fixes|treats|heals)\b",
            r"\bguarantee\b.{0,30}\b(recovery|outcome|result|success)\b",
            r"\b(30|60|90)[ -]day.{0,20}(cure|fix|solution|guarantee)\b",
        ],
        "description": "Agent made a treatment outcome guarantee"
    },
    {
        "flag_code": "CLINICAL_SCOPE",
        "severity": "critical",
        "patterns": [
            r"\bI (think|believe|recommend) you need\b.{0,30}\b(residential|detox|inpatient|outpatient|IOP|PHP)\b",
            r"\bbased on what you('ve| have) told me.{0,20}(you need|you should)\b",
            r"\byou (definitely|clearly|obviously) need\b",
        ],
        "description": "Agent recommended a specific level of care — clinical scope violation"
    }
]

CRISIS_ESCALATION_TRIGGERS = [
    r"\b(suicid|kill myself|end my life|don['']t want to (live|be here))\b",
    r"\b(overdos(ed|ing)|took too many|took a lot of)\b",
    r"\b(shaking|withdrawal|can['']t stop)\b.{0,20}\b(bad|severe|really)\b",
]
```

---

## 6. Format utilities

```python
def format_transcript(turns: list[dict]) -> str:
    lines = []
    for turn in turns:
        speaker = turn['speaker'].upper()
        ts = turn['timestamp_seconds']
        text = turn['text']
        lines.append(f"[{ts:04d}s] {speaker}: {text}")
    return "\n".join(lines)

def format_rubric(rubric: dict) -> str:
    # Converts rubric YAML to a compact text block for the prompt
    # See packages/rubric-engine/formatter.py
    pass
```
