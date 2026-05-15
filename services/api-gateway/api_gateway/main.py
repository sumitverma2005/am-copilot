"""AM Copilot API Gateway — FastAPI application entry point."""
from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api_gateway.auth import log_bypass_warning_on_startup
from api_gateway.routes.calls import router as calls_router
from api_gateway.routes.disagreements import router as disagreements_router
from api_gateway.routes.health import router as health_router
from api_gateway.routes.queues import router as queues_router

load_dotenv(Path(__file__).parents[3] / ".env")

logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO"))


@asynccontextmanager
async def _lifespan(app: FastAPI):
    log_bypass_warning_on_startup()
    yield


app = FastAPI(title="AM Copilot API", version="0.1.0", lifespan=_lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(calls_router)
app.include_router(queues_router)
app.include_router(disagreements_router)
