"""CTM REST API client.

Authentication: HTTP Basic Auth (Access Key + Secret Key), per CTM API docs.
Credentials are read from environment variables — never hardcoded.

Environment variables required:
    CTM_API_KEY     — CTM Access Key (Basic Auth username)
    CTM_API_SECRET  — CTM Secret Key (Basic Auth password)
    CTM_BASE_URL    — e.g. https://api.calltrackingmetrics.com
    CTM_ACCOUNT_ID  — CTM account identifier
"""
from __future__ import annotations

import os

import httpx


class CTMApiError(Exception):
    def __init__(self, status_code: int, message: str) -> None:
        self.status_code = status_code
        super().__init__(f"CTM API error {status_code}: {message}")


class CTMClient:
    def __init__(self) -> None:
        api_key = os.environ["CTM_API_KEY"]
        api_secret = os.environ["CTM_API_SECRET"]
        base_url = os.environ["CTM_BASE_URL"].rstrip("/")
        self._account_id = os.environ["CTM_ACCOUNT_ID"]
        self._client = httpx.Client(
            base_url=base_url,
            auth=(api_key, api_secret),
            timeout=30.0,
        )

    def get_call_metadata(self, call_id: str) -> dict:
        """Fetch call metadata from GET /api/v1/accounts/{account_id}/calls/{call_id}."""
        url = f"/api/v1/accounts/{self._account_id}/calls/{call_id}"
        response = self._client.get(url)
        self._raise_for_status(response)
        return response.json()

    def get_call_transcript(self, call_id: str) -> dict:
        """Fetch transcript from GET /api/v1/accounts/{account_id}/calls/{call_id}/transcription.json."""
        url = f"/api/v1/accounts/{self._account_id}/calls/{call_id}/transcription.json"
        response = self._client.get(url)
        self._raise_for_status(response)
        return response.json()

    def _raise_for_status(self, response: httpx.Response) -> None:
        if response.status_code >= 400:
            raise CTMApiError(response.status_code, response.text[:200])

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> CTMClient:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()
