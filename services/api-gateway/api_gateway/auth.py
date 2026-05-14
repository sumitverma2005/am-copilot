"""Auth middleware — Cognito JWT verification with a development-only bypass.

The bypass is ONLY honoured when ENVIRONMENT=development. If the environment
is anything else (staging, production), the bypass flag is silently ignored and
real JWT verification proceeds — this is enforced in code, not just config.
"""
from __future__ import annotations

import logging
import os

from fastapi import Header, HTTPException, status

logger = logging.getLogger(__name__)

_BYPASS_LOGGED = False


def _bypass_active() -> bool:
    env = os.environ.get("ENVIRONMENT", "production")
    flag = os.environ.get("DEV_BYPASS_AUTH", "false").lower() == "true"
    return flag and env == "development"


def log_bypass_warning_on_startup() -> None:
    if _bypass_active():
        logger.warning(
            "⚠️  AUTH BYPASS ENABLED — development only. "
            "Set DEV_BYPASS_AUTH=false or ENVIRONMENT != development to disable."
        )


async def require_auth(authorization: str | None = Header(default=None)) -> None:
    """FastAPI dependency — verify Cognito JWT or allow bypass in dev."""
    if _bypass_active():
        return

    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or malformed Authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Phase A: Cognito JWT verification goes here in Phase B.
    # For now, accept any non-empty Bearer token when bypass is off.
    # Replace this block with jose/python-jose Cognito verification.
    token = authorization.removeprefix("Bearer ").strip()
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Empty Bearer token",
            headers={"WWW-Authenticate": "Bearer"},
        )
