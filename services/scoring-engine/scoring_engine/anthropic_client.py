"""Anthropic direct API client — drop-in replacement for BedrockClient.

Build-window workaround: used when AWS Bedrock quotas are exhausted.
Switch via MODEL_PROVIDER env var. Remove before production.

Environment variables:
    ANTHROPIC_API_KEY   — Anthropic API key (required)
    ANTHROPIC_MODEL_ID  — model string (default: claude-sonnet-4-5-20250929)

Retry strategy: 3 attempts with 2s / 4s / 8s exponential backoff on
RateLimitError — mirrors BedrockClient exactly.
"""
from __future__ import annotations

import os
import time

import anthropic

_DEFAULT_MODEL = "claude-sonnet-4-5-20250929"
_MAX_TOKENS = 4096


class AnthropicThrottledError(Exception):
    """Raised when all retry attempts are exhausted due to rate limiting."""


class AnthropicClient:
    _MAX_RETRIES = 3
    _BACKOFF_SECONDS = [2, 4, 8]

    def __init__(self) -> None:
        api_key = os.environ["ANTHROPIC_API_KEY"]
        self._model_id = os.environ.get("ANTHROPIC_MODEL_ID", _DEFAULT_MODEL)
        self._client = anthropic.Anthropic(api_key=api_key)

    @property
    def model_id(self) -> str:
        return self._model_id

    def invoke(self, system: str, user: str) -> str:
        """Call Anthropic and return the model's text response.

        Retries on RateLimitError with exponential backoff.
        Raises AnthropicThrottledError if all retries exhausted.
        Non-throttle errors bubble up immediately.
        """
        last_error: Exception | None = None
        for attempt, wait in enumerate(self._BACKOFF_SECONDS, start=1):
            try:
                response = self._client.messages.create(
                    model=self._model_id,
                    max_tokens=_MAX_TOKENS,
                    system=system,
                    messages=[{"role": "user", "content": user}],
                )
                return response.content[0].text
            except anthropic.RateLimitError as e:
                last_error = e
                if attempt < self._MAX_RETRIES:
                    time.sleep(wait)
                # for loop continues to next attempt

        raise AnthropicThrottledError(
            f"Anthropic rate-limited after {self._MAX_RETRIES} attempts."
        ) from last_error
