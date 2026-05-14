"""Stub CTM client for Phase A (CTM_MODE=stub).

Reads synthetic JSON files and presents the same two-method interface as CTMClient,
splitting each bundled file into the two responses real CTM returns.

The outline[] array produced here uses the same CHANNEL_TO_ROLE convention as
normalizer.py — both import from constants.py so they can never diverge.
"""
from __future__ import annotations

import json
from pathlib import Path

from .constants import CHANNEL_TO_ROLE

# Reverse map: role → channel (for building synthetic outline[])
_ROLE_TO_CHANNEL = {role: ch for ch, role in CHANNEL_TO_ROLE.items()}

_DEFAULT_SYNTHETIC_DIR = Path(__file__).parents[3] / "data" / "synthetic"


class StubCTMClient:
    def __init__(self, synthetic_dir: Path | None = None) -> None:
        self._dir = synthetic_dir or _DEFAULT_SYNTHETIC_DIR

    def get_call_metadata(self, call_id: str) -> dict:
        """Return the metadata half of the synthetic file, shaped like CTM endpoint 1."""
        data = self._load(call_id)
        meta = data["metadata"]
        return {
            "id": call_id,
            "sid": call_id,
            "account_id": "stub-account",
            "duration": meta["duration_seconds"],
            "talk_time": meta["duration_seconds"],
            "ring_time": 0,
            "hold_time": 0,
            "direction": "inbound",
            "caller_number": "+10000000000",
            "tracking_number": meta.get("tracking_number", "+10000000001"),
            "contact_number": "+10000000000",
            "called_at": data.get("generated_at", "2026-04-01T00:00:00Z"),
            "unix_time": 1743465600,
            "dial_status": "completed",
            "call_status": "completed",
            "status": "completed",
            "source": meta.get("campaign_source", "stub"),
            "agent": {
                "id": meta["agent_id"],
                "name": meta["agent_name"],
                "email": f"{meta['agent_id'].lower()}@stub.example.com",
            },
            "agent_id": meta["agent_id"],
            "notes": "",
            "tag_list": [],
            # audio is intentionally omitted — never simulate a recording URL
            "legs": [],
        }

    def get_call_transcript(self, call_id: str) -> dict:
        """Return the transcript half, shaped like CTM transcription.json endpoint.

        Builds outline[] from the synthetic transcript[], mapping speaker→channel
        via _ROLE_TO_CHANNEL. confidence is None (synthetic = written, not transcribed).
        """
        data = self._load(call_id)
        outline = []
        for turn in data["transcript"]:
            channel = _ROLE_TO_CHANNEL.get(turn["speaker"], 1)
            outline.append({
                "vendor": "stub",
                "speaker": turn["speaker"],
                "gender": "U",
                "text": turn["text"],
                "offset": turn["turn"] - 1,
                "channel": channel,
                "s": float(turn["timestamp_seconds"]),
                "e": float(turn["timestamp_seconds"]) + 5.0,  # synthetic — no real end time
                "start_fmt": _fmt_time(turn["timestamp_seconds"]),
                "end_fmt": _fmt_time(turn["timestamp_seconds"] + 5),
                "confidence": None,
                "words": [],
            })
        return {
            "callid": call_id,
            "versions": [1],
            "text": "\n".join(
                f"{t['speaker'].title()}: {t['text']}" for t in data["transcript"]
            ),
            "sentiment": None,
            "outline": outline,
        }

    def _load(self, call_id: str) -> dict:
        matches = list(self._dir.glob(f"{call_id}_*.json"))
        if not matches:
            raise FileNotFoundError(f"No synthetic file found for call_id={call_id!r} in {self._dir}")
        return json.loads(matches[0].read_text())


def _fmt_time(seconds: float) -> str:
    s = int(seconds)
    h, rem = divmod(s, 3600)
    m, sec = divmod(rem, 60)
    return f"{h:02d}:{m:02d}:{sec:02d}.00"
