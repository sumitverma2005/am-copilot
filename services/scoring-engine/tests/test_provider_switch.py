"""Tests for MODEL_PROVIDER env var → correct LLM client instantiation."""
from __future__ import annotations

from unittest.mock import patch

import pytest


def test_anthropic_provider_returns_anthropic_client(monkeypatch):
    monkeypatch.setenv("MODEL_PROVIDER", "anthropic")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    with patch("scoring_engine.anthropic_client.anthropic.Anthropic"):
        from scoring_engine.score_arbitrator import _make_llm_client
        from scoring_engine.anthropic_client import AnthropicClient
        client = _make_llm_client()
    assert isinstance(client, AnthropicClient)


def test_bedrock_provider_returns_bedrock_client(monkeypatch):
    monkeypatch.setenv("MODEL_PROVIDER", "bedrock")
    monkeypatch.setenv("BEDROCK_MODEL_ID", "us.anthropic.claude-sonnet-4-5-20250929-v1:0")
    with patch("scoring_engine.bedrock_client.boto3.Session"):
        from scoring_engine.score_arbitrator import _make_llm_client
        from scoring_engine.bedrock_client import BedrockClient
        client = _make_llm_client()
    assert isinstance(client, BedrockClient)


def test_default_provider_is_bedrock(monkeypatch):
    monkeypatch.delenv("MODEL_PROVIDER", raising=False)
    monkeypatch.setenv("BEDROCK_MODEL_ID", "us.anthropic.claude-sonnet-4-5-20250929-v1:0")
    with patch("scoring_engine.bedrock_client.boto3.Session"):
        from scoring_engine.score_arbitrator import _make_llm_client
        from scoring_engine.bedrock_client import BedrockClient
        client = _make_llm_client()
    assert isinstance(client, BedrockClient)


def test_provider_value_is_case_insensitive(monkeypatch):
    monkeypatch.setenv("MODEL_PROVIDER", "ANTHROPIC")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    with patch("scoring_engine.anthropic_client.anthropic.Anthropic"):
        from scoring_engine.score_arbitrator import _make_llm_client
        from scoring_engine.anthropic_client import AnthropicClient
        client = _make_llm_client()
    assert isinstance(client, AnthropicClient)
