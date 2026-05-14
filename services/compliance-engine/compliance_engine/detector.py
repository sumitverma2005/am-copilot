"""Compliance detector — deterministic rule engine.

Runs BEFORE any LLM call. Deterministic results are authoritative.
LLM provides contextual reasoning for evidence records only (see compliance prompt).

Speaker identification uses the normalized `speaker` field, which is set by the
normalizer via CHANNEL_TO_ROLE. This is the single source of truth for agent vs caller
and the only place that needs updating when Phase B channel verification completes.
"""
from __future__ import annotations

from dataclasses import dataclass

from .rules import _COMPILED_RULES, _COMPILED_ESCALATION


@dataclass
class ComplianceFlag:
    flag_code: str
    matched_phrase: str
    turn_number: int
    timestamp_seconds: int
    severity: str
    description: str


@dataclass
class ComplianceResult:
    flags: list[ComplianceFlag]
    escalation_required: bool


def run_compliance_check(transcript: list[dict]) -> ComplianceResult:
    """Run all deterministic compliance rules against a normalized transcript.

    Compliance rules check agent turns only — callers cannot commit compliance violations.
    Escalation triggers check all turns — a caller describing a crisis must be flagged.

    Args:
        transcript: list of normalized turn dicts (turn, speaker, timestamp_seconds, text)

    Returns:
        ComplianceResult with any flags found and escalation status.
    """
    flags: list[ComplianceFlag] = []
    escalation_required = False

    for turn in transcript:
        text = turn["text"]
        turn_number = turn["turn"]
        ts = int(turn.get("timestamp_seconds", 0))
        speaker = turn["speaker"]  # "agent" or "caller" — set by normalizer via CHANNEL_TO_ROLE

        # Compliance rules: agent turns only
        if speaker == "agent":
            for rule in _COMPILED_RULES:
                for pattern in rule["patterns"]:
                    match = pattern.search(text)
                    if match:
                        flags.append(ComplianceFlag(
                            flag_code=rule["flag_code"],
                            matched_phrase=match.group(0),
                            turn_number=turn_number,
                            timestamp_seconds=ts,
                            severity=rule["severity"],
                            description=rule["description"],
                        ))
                        break  # one flag per rule per turn is enough

        # Escalation triggers: all turns (caller disclosures matter most)
        for pattern in _COMPILED_ESCALATION:
            if pattern.search(text):
                escalation_required = True
                break

    return ComplianceResult(flags=flags, escalation_required=escalation_required)
