"""Health & readiness endpoints (docs/04 §8)."""

from __future__ import annotations

import time

from canonical_schema import HealthResponse, ReadyResponse
from fastapi import APIRouter, Request

from core_api._version import __version__

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health(request: Request) -> HealthResponse:
    """Liveness."""
    return HealthResponse(
        status="ok",
        service="core-api",
        version=__version__,
        uptime_s=round(time.monotonic() - request.app.state.started_at, 3),
    )


@router.get("/ready", response_model=ReadyResponse)
def ready(request: Request) -> ReadyResponse:
    """Readiness: dependency checks (store in dev; DB/Redis/MinIO in prod)."""
    store_ok = request.app.state.store is not None
    return ReadyResponse(ready=store_ok, dependencies={"case_store": store_ok})
