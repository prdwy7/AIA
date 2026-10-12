"""FastAPI application for mlops-service (S26).

Skeleton service.
Built in: Phase 14 (foundation W3, hardening W5).
Full module context: README.md (from docs/02-modules.md §S26).
Conventions: RFC 7807 problem+json errors, `/v1` URL prefix, `/health` +
`/ready` on every service.
"""

from __future__ import annotations

import time
from contextlib import asynccontextmanager

from canonical_schema import HealthResponse, ReadyResponse
from fastapi import FastAPI, Request

from mlops_service._version import __version__

SERVICE_NAME = "mlops-service"


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.started_at = time.monotonic()
    # TODO: wire real dependencies (DB, Redis, MinIO, ...) as the service is built out.
    yield


def create_app() -> FastAPI:
    app = FastAPI(title=f"AI Kiosk — {SERVICE_NAME}", version=__version__, lifespan=lifespan)

    @app.get("/health", response_model=HealthResponse)
    def health(request: Request) -> HealthResponse:
        """Liveness."""
        return HealthResponse(
            status="ok",
            service=SERVICE_NAME,
            version=__version__,
            uptime_s=round(time.monotonic() - request.app.state.started_at, 3),
        )

    @app.get("/ready", response_model=ReadyResponse)
    def ready(request: Request) -> ReadyResponse:
        """Readiness — TODO: add real dependency checks as the service is built out."""
        return ReadyResponse(ready=True, dependencies={})

    return app


app = create_app()
