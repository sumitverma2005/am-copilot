"""Tests for StubCTMClient — verifies both stub methods return correct CTM-shaped responses."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[1]))

from ctm_integration.stub_client import StubCTMClient
from ctm_integration.constants import CHANNEL_TO_ROLE

SYNTHETIC_DIR = Path(__file__).parents[3] / "data" / "synthetic"
CALL_ID = "syn_001"


@pytest.fixture
def client():
    return StubCTMClient(synthetic_dir=SYNTHETIC_DIR)


# ── get_call_metadata ──────────────────────────────────────────────────────────

def test_metadata_has_id(client):
    meta = client.get_call_metadata(CALL_ID)
    assert meta["id"] == CALL_ID


def test_metadata_has_agent_object(client):
    meta = client.get_call_metadata(CALL_ID)
    assert "agent" in meta
    assert "name" in meta["agent"]
    assert "id" in meta["agent"]


def test_metadata_has_duration(client):
    meta = client.get_call_metadata(CALL_ID)
    assert isinstance(meta["duration"], int)
    assert meta["duration"] > 0


def test_metadata_has_no_audio_field(client):
    """Recording URL must never appear, even in the stub."""
    meta = client.get_call_metadata(CALL_ID)
    assert "audio" not in meta


def test_metadata_called_at_is_string(client):
    meta = client.get_call_metadata(CALL_ID)
    assert isinstance(meta["called_at"], str)
    assert meta["called_at"]


# ── get_call_transcript ────────────────────────────────────────────────────────

def test_transcript_has_outline(client):
    trans = client.get_call_transcript(CALL_ID)
    assert "outline" in trans
    assert len(trans["outline"]) > 0


def test_transcript_outline_has_required_fields(client):
    trans = client.get_call_transcript(CALL_ID)
    required = {"channel", "text", "s", "e", "confidence"}
    for turn in trans["outline"]:
        assert required.issubset(turn.keys()), f"Missing fields in turn: {turn}"


def test_transcript_confidence_is_none_for_synthetic(client):
    """Synthetic transcripts are written, not transcribed — confidence is genuinely N/A."""
    trans = client.get_call_transcript(CALL_ID)
    for turn in trans["outline"]:
        assert turn["confidence"] is None


def test_transcript_channels_use_known_values(client):
    """All channel values must be in CHANNEL_TO_ROLE."""
    trans = client.get_call_transcript(CALL_ID)
    for turn in trans["outline"]:
        assert turn["channel"] in CHANNEL_TO_ROLE, (
            f"channel={turn['channel']} not in CHANNEL_TO_ROLE — stub and normalizer would disagree"
        )


def test_transcript_has_callid(client):
    trans = client.get_call_transcript(CALL_ID)
    assert trans["callid"] == CALL_ID


def test_transcript_words_is_empty_list(client):
    """words[] is dropped per normalizer rules — stub should not populate it."""
    trans = client.get_call_transcript(CALL_ID)
    for turn in trans["outline"]:
        assert turn["words"] == []


# ── Round-trip: stub → normalizer ─────────────────────────────────────────────

def test_stub_output_normalizes_cleanly(client):
    """Full round-trip: stub methods → normalize() → valid internal format."""
    from ctm_integration.normalizer import normalize

    meta = client.get_call_metadata(CALL_ID)
    trans = client.get_call_transcript(CALL_ID)
    result = normalize(meta, trans)

    assert result["call_id"] == CALL_ID
    assert len(result["transcript"]) > 0
    for turn in result["transcript"]:
        assert turn["speaker"] in ("agent", "caller")
        assert isinstance(turn["turn"], int)
        assert isinstance(turn["text"], str)


# ── Error handling ─────────────────────────────────────────────────────────────

def test_missing_call_id_raises_file_not_found(client):
    with pytest.raises(FileNotFoundError, match="nonexistent_999"):
        client.get_call_metadata("nonexistent_999")
