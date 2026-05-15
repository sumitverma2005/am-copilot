"""Tests for AnthropicClient — all API calls mocked, no live network."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import anthropic as anthropic_sdk
import httpx
import pytest

from scoring_engine.anthropic_client import AnthropicClient, AnthropicThrottledError


# ── Helpers ────────────────────────────────────────────────────────────────────

def _make_api_response(text: str) -> MagicMock:
    response = MagicMock()
    response.content = [MagicMock(text=text)]
    return response


def _rate_limit_error() -> anthropic_sdk.RateLimitError:
    req = httpx.Request("POST", "https://api.anthropic.com/v1/messages")
    resp = httpx.Response(429, request=req)
    return anthropic_sdk.RateLimitError("rate limited", response=resp, body={})


def _auth_error() -> anthropic_sdk.AuthenticationError:
    req = httpx.Request("POST", "https://api.anthropic.com/v1/messages")
    resp = httpx.Response(401, request=req)
    return anthropic_sdk.AuthenticationError("bad key", response=resp, body={})


@pytest.fixture
def mock_messages(monkeypatch):
    """Patch anthropic.Anthropic so no real HTTP calls are made."""
    mock_msgs = MagicMock()
    mock_inner = MagicMock()
    mock_inner.messages = mock_msgs
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    with patch("scoring_engine.anthropic_client.anthropic.Anthropic", return_value=mock_inner):
        yield mock_msgs


# ── Happy path ─────────────────────────────────────────────────────────────────

def test_invoke_returns_text(mock_messages):
    mock_messages.create.return_value = _make_api_response("Scored successfully.")
    client = AnthropicClient()
    result = client.invoke("system prompt", "user prompt")
    assert result == "Scored successfully."


def test_invoke_passes_system_and_user(mock_messages):
    mock_messages.create.return_value = _make_api_response("ok")
    client = AnthropicClient()
    client.invoke("SYSTEM", "USER")
    kwargs = mock_messages.create.call_args[1]
    assert kwargs["system"] == "SYSTEM"
    assert kwargs["messages"] == [{"role": "user", "content": "USER"}]


def test_invoke_uses_configured_model(mock_messages, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_MODEL_ID", "claude-sonnet-4-5-20250929")
    mock_messages.create.return_value = _make_api_response("ok")
    client = AnthropicClient()
    client.invoke("s", "u")
    assert mock_messages.create.call_args[1]["model"] == "claude-sonnet-4-5-20250929"


# ── model_id property ──────────────────────────────────────────────────────────

def test_model_id_reads_from_env(mock_messages, monkeypatch):
    monkeypatch.setenv("ANTHROPIC_MODEL_ID", "claude-custom-model")
    client = AnthropicClient()
    assert client.model_id == "claude-custom-model"


def test_model_id_has_correct_default(mock_messages, monkeypatch):
    monkeypatch.delenv("ANTHROPIC_MODEL_ID", raising=False)
    client = AnthropicClient()
    assert client.model_id == "claude-sonnet-4-5-20250929"


# ── Retry on rate limit ────────────────────────────────────────────────────────

def test_retries_on_rate_limit_then_succeeds(mock_messages):
    mock_messages.create.side_effect = [
        _rate_limit_error(),
        _rate_limit_error(),
        _make_api_response("OK after retries"),
    ]
    with patch("scoring_engine.anthropic_client.time.sleep"):
        client = AnthropicClient()
        result = client.invoke("s", "u")
    assert result == "OK after retries"
    assert mock_messages.create.call_count == 3


def test_sleeps_between_retries(mock_messages):
    mock_messages.create.side_effect = [
        _rate_limit_error(),
        _make_api_response("ok"),
    ]
    with patch("scoring_engine.anthropic_client.time.sleep") as mock_sleep:
        client = AnthropicClient()
        client.invoke("s", "u")
    mock_sleep.assert_called_once_with(2)


def test_raises_throttled_error_after_all_retries(mock_messages):
    mock_messages.create.side_effect = _rate_limit_error()
    with patch("scoring_engine.anthropic_client.time.sleep"):
        client = AnthropicClient()
        with pytest.raises(AnthropicThrottledError):
            client.invoke("s", "u")
    assert mock_messages.create.call_count == 3


def test_throttled_error_wraps_original_cause(mock_messages):
    original = _rate_limit_error()
    mock_messages.create.side_effect = original
    with patch("scoring_engine.anthropic_client.time.sleep"):
        client = AnthropicClient()
        with pytest.raises(AnthropicThrottledError) as exc_info:
            client.invoke("s", "u")
    assert exc_info.value.__cause__ is original


# ── Non-throttle errors bubble immediately ────────────────────────────────────

def test_non_throttle_error_bubbles_immediately(mock_messages):
    mock_messages.create.side_effect = _auth_error()
    with patch("scoring_engine.anthropic_client.time.sleep"):
        client = AnthropicClient()
        with pytest.raises(anthropic_sdk.AuthenticationError):
            client.invoke("s", "u")
    assert mock_messages.create.call_count == 1


def test_non_throttle_error_does_not_sleep(mock_messages):
    mock_messages.create.side_effect = _auth_error()
    with patch("scoring_engine.anthropic_client.time.sleep") as mock_sleep:
        client = AnthropicClient()
        with pytest.raises(anthropic_sdk.AuthenticationError):
            client.invoke("s", "u")
    mock_sleep.assert_not_called()
