"""Bedrock client — boto3 wrapper for Claude Sonnet 4.5 invocations.

Environment variables:
    BEDROCK_MODEL_ID  — e.g. us.anthropic.claude-sonnet-4-5-20251001-v1:0
    AWS_PROFILE       — named profile in ~/.aws/credentials
    AWS_REGION        — e.g. us-east-1 (default: us-east-1)

Retry strategy: 3 attempts with 2s / 4s / 8s exponential backoff on
ThrottlingException. This handles the new-account daily token limit bursts
without crashing the pipeline.
"""
from __future__ import annotations

import json
import os
import time

import boto3
from botocore.exceptions import ClientError


class BedrockThrottledError(Exception):
    """Raised when all retry attempts are exhausted due to throttling."""


class BedrockClient:
    _MAX_RETRIES = 3
    _BACKOFF_SECONDS = [2, 4, 8]
    _MAX_TOKENS = 4096

    def __init__(self) -> None:
        profile = os.environ.get("AWS_PROFILE", "am-copilot-dev")
        region = os.environ.get("AWS_REGION", "us-east-1")
        self._model_id = os.environ["BEDROCK_MODEL_ID"]
        session = boto3.Session(profile_name=profile, region_name=region)
        self._bedrock = session.client("bedrock-runtime")

    @property
    def model_id(self) -> str:
        return self._model_id

    def invoke(self, system: str, user: str) -> str:
        """Call Bedrock and return the model's text response.

        Retries on ThrottlingException with exponential backoff.
        Raises BedrockThrottledError if all retries exhausted.
        """
        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": self._MAX_TOKENS,
            "system": system,
            "messages": [{"role": "user", "content": user}],
        })

        last_error: Exception | None = None
        for attempt, wait in enumerate(self._BACKOFF_SECONDS, start=1):
            try:
                response = self._bedrock.invoke_model(
                    modelId=self._model_id,
                    body=body,
                    contentType="application/json",
                    accept="application/json",
                )
                result = json.loads(response["body"].read())
                return result["content"][0]["text"]
            except ClientError as e:
                if e.response["Error"]["Code"] in ("ThrottlingException", "TooManyRequestsException"):
                    last_error = e
                    if attempt < self._MAX_RETRIES:
                        time.sleep(wait)
                    continue
                raise

        raise BedrockThrottledError(
            f"Bedrock throttled after {self._MAX_RETRIES} attempts. "
            "Daily token quota may be exhausted — wait and retry."
        ) from last_error
