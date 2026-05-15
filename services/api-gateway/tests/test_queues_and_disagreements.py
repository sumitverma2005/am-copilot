"""Tests for queue and disagreement endpoints."""
from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(autouse=True)
def bypass_auth(monkeypatch):
    monkeypatch.setenv("DEV_BYPASS_AUTH", "true")
    monkeypatch.setenv("ENVIRONMENT", "development")


@pytest.fixture
def client():
    from api_gateway.main import app
    return TestClient(app)


@pytest.fixture(autouse=True)
def clean_state(tmp_path, monkeypatch):
    """Redirect state files to a temp dir for each test."""
    import api_gateway.state_store as ss
    state_dir = tmp_path / "state"
    state_dir.mkdir()
    monkeypatch.setattr(ss, "_STATE_DIR", state_dir)
    monkeypatch.setattr(ss, "_QUEUE_FILE", state_dir / "queue_state.json")
    monkeypatch.setattr(ss, "_OVERRIDES_FILE", state_dir / "overrides.json")


# ── Coaching queue ──────────────────────────────────────────────────────────────

def test_coaching_queue_returns_list(client):
    r = client.get("/queue/coaching")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_coaching_queue_only_below_threshold(client):
    r = client.get("/queue/coaching")
    for row in r.json():
        assert row["overall_score"] < 70, f"Call {row['call_id']} has score {row['overall_score']} ≥ 70"


def test_coaching_queue_sorted_ascending(client):
    r = client.get("/queue/coaching")
    scores = [row["overall_score"] for row in r.json()]
    assert scores == sorted(scores)


def test_coaching_queue_has_required_fields(client):
    r = client.get("/queue/coaching")
    assert len(r.json()) > 0
    row = r.json()[0]
    for field in ("call_id", "agent_id", "overall_score", "worst_dimension", "call_timestamp", "coached_at"):
        assert field in row, f"Missing field: {field}"


def test_coaching_queue_coached_at_null_initially(client):
    r = client.get("/queue/coaching")
    for row in r.json():
        assert row["coached_at"] is None


def test_mark_coached_returns_200(client):
    r = client.get("/queue/coaching")
    call_id = r.json()[0]["call_id"]
    r2 = client.post(f"/queue/coaching/{call_id}/complete")
    assert r2.status_code == 200
    assert r2.json()["status"] == "coached"


def test_mark_coached_reflects_in_subsequent_get(client):
    r = client.get("/queue/coaching")
    call_id = r.json()[0]["call_id"]
    client.post(f"/queue/coaching/{call_id}/complete")
    r2 = client.get("/queue/coaching")
    row = next(row for row in r2.json() if row["call_id"] == call_id)
    assert row["coached_at"] is not None


def test_mark_coached_404_on_nonexistent(client):
    r = client.post("/queue/coaching/syn_999/complete")
    assert r.status_code == 404


# ── Compliance queue ────────────────────────────────────────────────────────────

def test_compliance_queue_returns_list(client):
    r = client.get("/queue/compliance")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_compliance_queue_only_flagged_calls(client):
    r = client.get("/queue/compliance")
    for row in r.json():
        assert row.get("flag_code") is not None


def test_compliance_queue_has_required_fields(client):
    r = client.get("/queue/compliance")
    assert len(r.json()) > 0
    row = r.json()[0]
    for field in ("call_id", "agent_id", "flag_code", "matched_phrase", "timestamp_seconds", "reviewed_at"):
        assert field in row, f"Missing field: {field}"


def test_mark_reviewed_returns_200(client):
    r = client.get("/queue/compliance")
    call_id = r.json()[0]["call_id"]
    r2 = client.post(f"/queue/compliance/{call_id}/review", json={"comment": "Reviewed and corrected."})
    assert r2.status_code == 200
    assert r2.json()["status"] == "reviewed"


def test_mark_reviewed_reflects_in_subsequent_get(client):
    r = client.get("/queue/compliance")
    call_id = r.json()[0]["call_id"]
    client.post(f"/queue/compliance/{call_id}/review", json={"comment": "Done."})
    r2 = client.get("/queue/compliance")
    row = next(row for row in r2.json() if row["call_id"] == call_id)
    assert row["reviewed_at"] is not None
    assert row["review_comment"] == "Done."


def test_mark_reviewed_404_on_nonexistent(client):
    r = client.post("/queue/compliance/syn_999/review", json={"comment": "x"})
    assert r.status_code == 404


# ── Disagreements ───────────────────────────────────────────────────────────────

def test_disagreements_returns_empty_list_initially(client):
    r = client.get("/disagreements")
    assert r.status_code == 200
    assert r.json() == []


def test_override_creates_disagreement(client):
    payload = {
        "dimension": "empathy_rapport",
        "ai_score": 2.0,
        "manager_score": 3.0,
        "comment": "AI underscored the rapport.",
        "manager": "demo",
    }
    r = client.post("/calls/syn_001/override", json=payload)
    assert r.status_code == 201
    body = r.json()
    assert body["delta"] == 1.0
    assert body["call_id"] == "syn_001"


def test_override_appears_in_disagreement_log(client):
    payload = {
        "dimension": "next_step_clarity",
        "ai_score": 3.0,
        "manager_score": 4.0,
        "comment": "Closer than AI thought.",
        "manager": "demo",
    }
    client.post("/calls/syn_001/override", json=payload)
    r = client.get("/disagreements")
    assert len(r.json()) == 1
    assert r.json()[0]["dimension"] == "next_step_clarity"


def test_override_404_on_missing_call(client):
    payload = {
        "dimension": "empathy_rapport",
        "ai_score": 2.0,
        "manager_score": 3.0,
        "comment": "x",
    }
    r = client.post("/calls/syn_999/override", json=payload)
    assert r.status_code == 404


def test_export_csv_returns_correct_content_type(client):
    r = client.get("/disagreements/export")
    assert r.status_code == 200
    assert "text/csv" in r.headers["content-type"]


def test_export_csv_has_header_row(client):
    r = client.get("/disagreements/export")
    first_line = r.text.splitlines()[0]
    assert "call_id" in first_line
    assert "dimension" in first_line
