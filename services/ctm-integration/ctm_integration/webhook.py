"""CTM webhook receiver — FastAPI router.

Handles two CTM webhook events:
  POST /webhooks/ctm/call-complete    — fired when a call ends
  POST /webhooks/ctm/transcript-ready — fired when async transcription finishes

Both routes: verify HMAC-SHA256 signature → fetch both CTM endpoints → normalize → enqueue.

HMAC signature verification:
  Header:  X-CTM-Signature
  Method:  HMAC-SHA256 of the raw request body
  Secret:  CTM_WEBHOOK_SECRET environment variable

PHASE B VERIFICATION REQUIRED: Confirm CTM's exact signature scheme (header name,
HMAC algorithm, encoding) against CTM webhook documentation before going live.
Implemented here as standard HMAC-SHA256 of the raw body — the most common pattern —
but this must be validated against a real CTM webhook delivery.

Environment variables required:
    CTM_WEBHOOK_SECRET — shared secret from CTM webhook configuration
    CTM_MODE           — "stub" (Phase A default) or "live"
    EVALUATION_QUEUE_URL, AWS_REGION — consumed by queue.py
"""
from __future__ import annotations

import hashlib
import hmac
import os

from fastapi import APIRouter, HTTPException, Request, Response

from .client import CTMClient
from .normalizer import normalize
from . import queue as _queue
from .stub_client import StubCTMClient

router = APIRouter(prefix="/webhooks/ctm", tags=["webhooks"])


def _get_client() -> CTMClient | StubCTMClient:
    if os.environ.get("CTM_MODE", "stub") == "stub":
        return StubCTMClient()
    return CTMClient()


def _verify_signature(body: bytes, header: str | None) -> None:
    """Raise 401 if the CTM HMAC-SHA256 signature does not match.

    PHASE B VERIFICATION REQUIRED: validate this implementation against
    CTM's documented webhook signature scheme before going live.
    """
    secret = os.environ.get("CTM_WEBHOOK_SECRET", "")
    if not secret:
        return  # signature check disabled (local dev without secret configured)
    if not header:
        raise HTTPException(status_code=401, detail="Missing X-CTM-Signature header")
    expected = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, header):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")


async def _handle_event(request: Request) -> dict:
    body = await request.body()
    _verify_signature(body, request.headers.get("X-CTM-Signature"))

    payload = await request.json() if body else {}
    call_id = str(payload.get("call_id") or payload.get("id") or "")
    if not call_id:
        raise HTTPException(status_code=400, detail="Missing call_id in webhook payload")

    ctm_client = _get_client()
    try:
        metadata = ctm_client.get_call_metadata(call_id)
        transcript = ctm_client.get_call_transcript(call_id)
    finally:
        if hasattr(ctm_client, "close"):
            ctm_client.close()

    normalized = normalize(metadata, transcript)
    message_id = _queue.enqueue(call_id, normalized)
    return {"status": "queued", "call_id": call_id, "message_id": message_id}


@router.post("/call-complete")
async def call_complete(request: Request) -> dict:
    return await _handle_event(request)


@router.post("/transcript-ready")
async def transcript_ready(request: Request) -> dict:
    return await _handle_event(request)
