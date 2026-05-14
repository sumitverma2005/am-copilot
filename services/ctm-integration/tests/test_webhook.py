"""Tests for CTM webhook receiver."""
from __future__ import annotations

import hashlib
import hmac
import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).parents[1]))

from ctm_integration.webhook import router

app = FastAPI()
app.include_router(router)
client = TestClient(app, raise_server_exceptions=False)

WEBHOOK_SECRET = "test-secret-abc"
CALL_ID = "syn_001"


def _sig(body: bytes, secret: str = WEBHOOK_SECRET) -> str:
    return hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()


def _payload(call_id: str = CALL_ID) -> bytes:
    return json.dumps({"call_id": call_id}).encode()


def _stub_enqueue(call_id, normalized_call):
    return "mock-message-id-123"


# ── Signature verification ─────────────────────────────────────────────────────

def test_valid_signature_accepted(monkeypatch):
    monkeypatch.setenv("CTM_WEBHOOK_SECRET", WEBHOOK_SECRET)
    monkeypatch.setenv("CTM_MODE", "stub")

    body = _payload()
    with patch("ctm_integration.queue.enqueue", side_effect=_stub_enqueue):
        response = client.post(
            "/webhooks/ctm/call-complete",
            content=body,
            headers={"X-CTM-Signature": _sig(body), "Content-Type": "application/json"},
        )
    assert response.status_code == 200


def test_invalid_signature_returns_401(monkeypatch):
    monkeypatch.setenv("CTM_WEBHOOK_SECRET", WEBHOOK_SECRET)
    body = _payload()
    response = client.post(
        "/webhooks/ctm/call-complete",
        content=body,
        headers={"X-CTM-Signature": "bad-sig", "Content-Type": "application/json"},
    )
    assert response.status_code == 401


def test_missing_signature_header_returns_401(monkeypatch):
    monkeypatch.setenv("CTM_WEBHOOK_SECRET", WEBHOOK_SECRET)
    body = _payload()
    response = client.post(
        "/webhooks/ctm/call-complete",
        content=body,
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 401


def test_no_secret_configured_skips_check(monkeypatch):
    monkeypatch.delenv("CTM_WEBHOOK_SECRET", raising=False)
    monkeypatch.setenv("CTM_MODE", "stub")

    body = _payload()
    with patch("ctm_integration.queue.enqueue", side_effect=_stub_enqueue):
        response = client.post(
            "/webhooks/ctm/call-complete",
            content=body,
            headers={"Content-Type": "application/json"},
        )
    assert response.status_code == 200


# ── Missing call_id ────────────────────────────────────────────────────────────

def test_missing_call_id_returns_400(monkeypatch):
    monkeypatch.delenv("CTM_WEBHOOK_SECRET", raising=False)
    monkeypatch.setenv("CTM_MODE", "stub")

    body = json.dumps({"something_else": "value"}).encode()
    response = client.post(
        "/webhooks/ctm/call-complete",
        content=body,
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 400


# ── Successful enqueue ─────────────────────────────────────────────────────────

def test_successful_request_returns_queued_status(monkeypatch):
    monkeypatch.delenv("CTM_WEBHOOK_SECRET", raising=False)
    monkeypatch.setenv("CTM_MODE", "stub")

    body = _payload()
    with patch("ctm_integration.queue.enqueue", side_effect=_stub_enqueue):
        response = client.post(
            "/webhooks/ctm/call-complete",
            content=body,
            headers={"Content-Type": "application/json"},
        )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "queued"
    assert data["call_id"] == CALL_ID
    assert data["message_id"] == "mock-message-id-123"


def test_transcript_ready_route_works(monkeypatch):
    monkeypatch.delenv("CTM_WEBHOOK_SECRET", raising=False)
    monkeypatch.setenv("CTM_MODE", "stub")

    body = _payload()
    with patch("ctm_integration.queue.enqueue", side_effect=_stub_enqueue):
        response = client.post(
            "/webhooks/ctm/transcript-ready",
            content=body,
            headers={"Content-Type": "application/json"},
        )
    assert response.status_code == 200
    assert response.json()["status"] == "queued"


def test_enqueue_called_with_call_id_and_normalized_call(monkeypatch):
    monkeypatch.delenv("CTM_WEBHOOK_SECRET", raising=False)
    monkeypatch.setenv("CTM_MODE", "stub")

    captured = {}

    def mock_enqueue(call_id, normalized_call):
        captured["call_id"] = call_id
        captured["normalized_call"] = normalized_call
        return "msg-xyz"

    body = _payload("syn_002")
    with patch("ctm_integration.queue.enqueue", side_effect=mock_enqueue):
        response = client.post(
            "/webhooks/ctm/call-complete",
            content=body,
            headers={"Content-Type": "application/json"},
        )

    assert response.status_code == 200
    assert captured["call_id"] == "syn_002"
    assert "transcript" in captured["normalized_call"]
    assert len(captured["normalized_call"]["transcript"]) > 0
