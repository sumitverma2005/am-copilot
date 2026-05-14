"""Compliance detection rules — deterministic, no LLM.

Ported verbatim from docs/prompt-library.md section 5.
Do NOT add, remove, or modify patterns without creating a new versioned rules file.
A regex match on any COMPLIANCE_RULES pattern assigns compliance_language score = 0.
"""
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

# Pre-compiled patterns — compiled once at import time for performance
_COMPILED_RULES = [
    {
        "flag_code": rule["flag_code"],
        "severity": rule["severity"],
        "description": rule["description"],
        "patterns": [re.compile(p, re.IGNORECASE) for p in rule["patterns"]],
    }
    for rule in COMPLIANCE_RULES
]

_COMPILED_ESCALATION = [re.compile(p, re.IGNORECASE) for p in CRISIS_ESCALATION_TRIGGERS]
