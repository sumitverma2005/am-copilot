"""Tests for normalizer.normalize()."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1]))

from ctm_integration.normalizer import normalize
from ctm_integration.constants import CHANNEL_TO_ROLE


def _make_metadata(**overrides) -> dict:
    base = {
        "id": "call-001",
        "called_at": "2026-04-01T10:00:00Z",
        "duration": 180,
        "agent_id": "AGT-1",
        "agent": {"id": "AGT-1", "name": "Alice Smith", "email": "alice@example.com"},
    }
    base.update(overrides)
    return base


def _make_transcript_entry(channel: int, text: str, s: float = 0.0, confidence: float | None = 0.9) -> dict:
    return {
        "vendor": "g",
        "speaker": "Test User",
        "gender": "U",
        "text": text,
        "offset": 0,
        "channel": channel,
        "s": s,
        "e": s + 3.0,
        "start_fmt": "00:00:00",
        "end_fmt": "00:00:03.00",
        "confidence": confidence,
        "words": [["hello", 0.9, 0, 0.2]],
    }


def _make_transcript_response(outline: list) -> dict:
    return {"callid": "call-001", "versions": [1], "text": "blob", "sentiment": 2, "outline": outline}


# ── Field mapping ──────────────────────────────────────────────────────────────

def test_call_id_copied():
    result = normalize(_make_metadata(id="abc-123"), _make_transcript_response([]))
    assert result["call_id"] == "abc-123"


def test_agent_name_and_id_copied():
    result = normalize(_make_metadata(), _make_transcript_response([]))
    assert result["agent_id"] == "AGT-1"
    assert result["agent_name"] == "Alice Smith"


def test_duration_copied():
    result = normalize(_make_metadata(duration=300), _make_transcript_response([]))
    assert result["duration"] == 300


def test_called_at_copied():
    result = normalize(_make_metadata(), _make_transcript_response([]))
    assert result["called_at"] == "2026-04-01T10:00:00Z"


def test_ctm_sentiment_carried_as_reference():
    result = normalize(_make_metadata(), _make_transcript_response([]).__class__.__call__(
        {"callid": "x", "versions": [1], "text": "", "sentiment": 3, "outline": []}
    ) if False else {"callid": "x", "versions": [1], "text": "", "sentiment": 3, "outline": []})
    assert result["ctm_sentiment"] == 3


# ── Channel → role mapping ─────────────────────────────────────────────────────

def test_channel_2_maps_to_agent():
    outline = [_make_transcript_entry(channel=2, text="How can I help?")]
    result = normalize(_make_metadata(), _make_transcript_response(outline))
    assert result["transcript"][0]["speaker"] == "agent"


def test_channel_1_maps_to_caller():
    outline = [_make_transcript_entry(channel=1, text="I need help.")]
    result = normalize(_make_metadata(), _make_transcript_response(outline))
    assert result["transcript"][0]["speaker"] == "caller"


def test_turn_numbers_are_sequential_1_indexed():
    outline = [
        _make_transcript_entry(channel=2, text="Hello", s=0.0),
        _make_transcript_entry(channel=1, text="Hi there", s=3.0),
        _make_transcript_entry(channel=2, text="How can I help?", s=6.0),
    ]
    result = normalize(_make_metadata(), _make_transcript_response(outline))
    assert [t["turn"] for t in result["transcript"]] == [1, 2, 3]


def test_timestamp_seconds_from_s_field():
    outline = [_make_transcript_entry(channel=2, text="Hello", s=12.5)]
    result = normalize(_make_metadata(), _make_transcript_response(outline))
    assert result["transcript"][0]["timestamp_seconds"] == 12.5


# ── Dropped fields ─────────────────────────────────────────────────────────────

def test_words_field_dropped():
    outline = [_make_transcript_entry(channel=2, text="Hello")]
    result = normalize(_make_metadata(), _make_transcript_response(outline))
    assert "words" not in result["transcript"][0]


def test_vendor_field_dropped():
    outline = [_make_transcript_entry(channel=2, text="Hello")]
    result = normalize(_make_metadata(), _make_transcript_response(outline))
    assert "vendor" not in result["transcript"][0]


def test_gender_field_dropped():
    outline = [_make_transcript_entry(channel=2, text="Hello")]
    result = normalize(_make_metadata(), _make_transcript_response(outline))
    assert "gender" not in result["transcript"][0]


def test_no_audio_field_in_output():
    meta = _make_metadata()
    meta["audio"] = "https://recordings.example.com/rec.mp3"
    result = normalize(meta, _make_transcript_response([]))
    assert "audio" not in result


# ── Confidence handling ────────────────────────────────────────────────────────

def test_confidence_carried_through():
    outline = [_make_transcript_entry(channel=2, text="Hello", confidence=0.817)]
    result = normalize(_make_metadata(), _make_transcript_response(outline))
    assert result["transcript"][0]["confidence"] == 0.817


def test_none_confidence_passes_through():
    outline = [_make_transcript_entry(channel=2, text="Hello", confidence=None)]
    result = normalize(_make_metadata(), _make_transcript_response(outline))
    assert result["transcript"][0]["confidence"] is None


# ── Edge cases ─────────────────────────────────────────────────────────────────

def test_empty_outline_produces_empty_transcript():
    result = normalize(_make_metadata(), _make_transcript_response([]))
    assert result["transcript"] == []


def test_missing_outline_key_produces_empty_transcript():
    result = normalize(_make_metadata(), {"callid": "x", "versions": [1], "text": "", "sentiment": None})
    assert result["transcript"] == []


def test_channel_to_role_constant_matches_normalizer_behaviour():
    """Ensure CHANNEL_TO_ROLE in constants.py agrees with what normalize() actually does."""
    for channel, expected_role in CHANNEL_TO_ROLE.items():
        outline = [_make_transcript_entry(channel=channel, text="test")]
        result = normalize(_make_metadata(), _make_transcript_response(outline))
        assert result["transcript"][0]["speaker"] == expected_role
