"""API gateway tests — all file-based, no external calls."""
from __future__ import annotations

import os
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


# ── Health ─────────────────────────────────────────────────────────────────────

def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


# ── Call list ──────────────────────────────────────────────────────────────────

def test_calls_list_returns_list(client):
    r = client.get("/calls")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_calls_list_contains_syn_001(client):
    r = client.get("/calls")
    ids = [c["call_id"] for c in r.json()]
    assert "syn_001" in ids


def test_calls_list_row_has_required_fields(client):
    r = client.get("/calls")
    row = next(c for c in r.json() if c["call_id"] == "syn_001")
    for field in ("call_id", "overall_score", "status", "has_compliance_flags"):
        assert field in row, f"Missing field: {field}"


# ── Call detail ────────────────────────────────────────────────────────────────

def test_call_detail_syn_001(client):
    r = client.get("/calls/syn_001")
    assert r.status_code == 200
    data = r.json()
    assert data["evaluation"]["call_id"] == "syn_001"
    assert data["evaluation"]["overall_score"] == 90.0


def test_call_detail_has_dimension_scores(client):
    r = client.get("/calls/syn_001")
    dims = r.json()["dimension_scores"]
    assert len(dims) == 8


def test_call_detail_na_dimension_excluded(client):
    r = client.get("/calls/syn_001")
    family = next(d for d in r.json()["dimension_scores"] if d["dimension"] == "family_caller_handling")
    assert family["is_na"] is True
    assert family["raw_score"] is None


def test_call_detail_404_on_missing(client):
    r = client.get("/calls/syn_999")
    assert r.status_code == 404


# ── Evidence ───────────────────────────────────────────────────────────────────

def test_evidence_returns_anchors(client):
    r = client.get("/calls/syn_001/evidence/empathy_rapport")
    assert r.status_code == 200
    data = r.json()
    assert data["dimension"] == "empathy_rapport"
    assert len(data["anchors"]) > 0


def test_evidence_404_on_missing_call(client):
    r = client.get("/calls/syn_999/evidence/empathy_rapport")
    assert r.status_code == 404


# ── Auth bypass only active in development ─────────────────────────────────────

def test_auth_bypass_ignored_outside_development(monkeypatch):
    monkeypatch.setenv("DEV_BYPASS_AUTH", "true")
    monkeypatch.setenv("ENVIRONMENT", "production")
    from api_gateway.main import app
    c = TestClient(app, raise_server_exceptions=False)
    r = c.get("/calls")
    assert r.status_code == 401


def test_auth_bypass_active_in_development(monkeypatch):
    monkeypatch.setenv("DEV_BYPASS_AUTH", "true")
    monkeypatch.setenv("ENVIRONMENT", "development")
    from api_gateway.main import app
    c = TestClient(app)
    r = c.get("/calls")
    assert r.status_code == 200
