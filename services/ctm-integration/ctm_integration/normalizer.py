"""CTM → internal format normalizer.

Pure function: no I/O, no side effects. Takes the two raw CTM API dicts and
returns the internal normalized call format consumed by all downstream services.

Drop rules (per README): audio, words, vendor, gender, top-level text blob.
Keep rules: channel (mapped to speaker), text, s (→ timestamp_seconds), confidence, sentiment.
"""
from __future__ import annotations

from .constants import CHANNEL_TO_ROLE


def normalize(metadata: dict, transcript: dict) -> dict:
    """Merge CTM metadata + transcription dicts into the internal normalized format.

    Args:
        metadata:   Response from GET .../calls/{id}
        transcript: Response from GET .../calls/{id}/transcription.json

    Returns:
        Internal normalized call dict ready for scoring pipeline.
    """
    outline = transcript.get("outline") or []
    turns = []
    for i, entry in enumerate(outline, start=1):
        channel = entry.get("channel")
        speaker = CHANNEL_TO_ROLE.get(channel, _fallback_speaker(entry))
        turns.append({
            "turn": i,
            "speaker": speaker,
            "timestamp_seconds": float(entry.get("s", 0)),
            "text": entry.get("text", ""),
            "confidence": entry.get("confidence"),  # None is valid — synthetic / low-quality
        })

    agent = metadata.get("agent") or {}
    return {
        "call_id": str(metadata.get("id", "")),
        "called_at": metadata.get("called_at", ""),
        "duration": metadata.get("duration", 0),
        "agent_id": str(metadata.get("agent_id") or agent.get("id", "")),
        "agent_name": agent.get("name", ""),
        "ctm_sentiment": transcript.get("sentiment"),  # reference only — scoring engine ignores this
        "transcript": turns,
    }


def _fallback_speaker(entry: dict) -> str:
    """Last-resort speaker label when channel is missing or unmapped.

    Uses the raw speaker string lowercased. Should never happen with real CTM data
    once the channel mapping is verified in Phase B.
    """
    raw = entry.get("speaker", "unknown")
    return raw.lower()
