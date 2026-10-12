"""FastAPI application factory (docs/04-api-contracts.md).

Conventions:
- Errors: RFC 7807 `problem+json` with domain error codes.
- Versioning: URL prefix `/v1`.
- Health: `/health` (liveness), `/ready` (readiness) on every service.
"""

from __future__ import annotations

import time
from contextlib import asynccontextmanager

from canonical_schema import ProblemDetail, VersionTuple
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from core_api._version import __version__
from core_api.routers import cases, health, inputs, sessions
from core_api.store import ConsentRequired, InMemoryCaseStore

SERVICE_NAME = "core-api"


def _default_version_tuple() -> VersionTuple:
    """Development version tuple; production reads from version_registry."""
    return VersionTuple(
        model="gemma-3-12b:0.34.4",
        knowledge="1.0.0",
        rules="1.0.0",
        prompt_policy="1.0.0",
        speech="1.0.0",
        schema="1.0.0",
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.started_at = time.monotonic()
    app.state.store = InMemoryCaseStore(_default_version_tuple())
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="AI Kiosk — core-api",
        version=__version__,
        lifespan=lifespan,
    )

    @app.exception_handler(ConsentRequired)
    async def _consent_handler(request: Request, exc: ConsentRequired) -> JSONResponse:
        return JSONResponse(
            status_code=403,
            media_type="application/problem+json",
            content=ProblemDetail(
                title="Consent required",
                status=403,
                detail=str(exc),
                instance=str(request.url.path),
                error_code="CONSENT_REQUIRED",
            ).model_dump(exclude_none=True),
        )

    @app.exception_handler(KeyError)
    async def _not_found_handler(request: Request, exc: KeyError) -> JSONResponse:
        return JSONResponse(
            status_code=404,
            media_type="application/problem+json",
            content=ProblemDetail(
                title="Not found",
                status=404,
                detail=str(exc),
                instance=str(request.url.path),
            ).model_dump(exclude_none=True),
        )

    @app.exception_handler(ValueError)
    async def _validation_handler(request: Request, exc: ValueError) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            media_type="application/problem+json",
            content=ProblemDetail(
                title="Invalid input",
                status=422,
                detail=str(exc),
                instance=str(request.url.path),
            ).model_dump(exclude_none=True),
        )

    app.include_router(health.router)
    app.include_router(sessions.router)
    app.include_router(cases.router)
    app.include_router(inputs.router)
    return app


app = create_app()
