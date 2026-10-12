"""FastAPI application for image-service (docs/04 §1).

Endpoints:
- GET  /health, GET /ready
- POST /v1/media/analyze — image evidence extraction:
  deterministic quality checks → (if usable) Gemma 3 vision observations +
  ViT classification with the diagnosis guard → media-set bookkeeping
  (missing views, never re-requested).

Degradation: the quality pipeline is local and always available. Vision
(Gemma 3 via Ollama) and the ViT classifier are probed once at startup;
when unavailable the response degrades (empty observations / null
classification) instead of failing — a photo never dead-ends the case.
"""

from __future__ import annotations

import base64
import binascii
import time
from contextlib import asynccontextmanager
from typing import Protocol, runtime_checkable

from canonical_schema import HealthResponse, ProblemDetail, ReadyResponse, new_ulid
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from image_service._version import __version__
from image_service.classifier import (
    DiseaseClassifier,
    GuardedClassification,
    VitClassifier,
    classify_with_guard,
)
from image_service.media_set import ALL_VIEWS, DEFAULT_REQUESTED_VIEWS, MediaSetManager
from image_service.observations import (
    VLM_CONFIDENCE_CAP,
    GemmaVisionExtractor,
    ImageContext,
    Observation,
    ObservationExtractor,
    candidate_hypotheses,
)
from image_service.quality import check_image_quality

SERVICE_NAME = "image-service"


class MediaSourceUnavailable(Exception):
    """A media_ref was given but no media source (MinIO) is configured."""


@runtime_checkable
class MediaSource(Protocol):
    """Fetches media bytes from a reference (MinIO in production)."""

    def fetch(self, media_ref: str) -> bytes: ...


class MinIOMediaSource:
    """Production media source (MinIO). Lazy import of the minio client."""

    def __init__(self, endpoint: str, access_key: str, secret_key: str, bucket: str) -> None:
        self._endpoint = endpoint
        self._access_key = access_key
        self._secret_key = secret_key
        self._bucket = bucket
        self._client = None  # lazy

    def _ensure(self):
        if self._client is None:
            from minio import Minio  # lazy — optional runtime

            self._client = Minio(
                self._endpoint,
                access_key=self._access_key,
                secret_key=self._secret_key,
                secure=False,
            )
        return self._client

    def fetch(self, media_ref: str) -> bytes:
        # media_ref format: "<object_key>" inside the configured bucket.
        data = self._ensure().get_object(self._bucket, media_ref)
        return b"".join(data.data)


# ---------------------------------------------------------------------------
# Request / response (docs/04 §1: POST /v1/media/analyze)
# ---------------------------------------------------------------------------


class MediaAnalyzeRequest(BaseModel):
    case_id: str
    media_ref: str | None = Field(default=None, description="MinIO object key (central path)")
    image_b64: str | None = Field(default=None, description="base64 image (edge/offline path)")
    view: str | None = Field(default=None, description="which view this photo is (ALL_VIEWS)")
    requested_views: list[str] = Field(
        default_factory=list, description="default: whole_plant, leaf, pest_closeup"
    )
    crop: str | None = None
    stage: str | None = None
    region: str | None = None


class MediaAnalyzeResponse(BaseModel):
    media_id: str
    quality: dict
    observations: list[dict] = Field(default_factory=list)
    candidate_hypotheses: list[dict] = Field(default_factory=list)
    classification: dict | None = None
    missing_views: list[str] = Field(default_factory=list)
    missing_view_instructions: list[str] = Field(default_factory=list)


def _obs_to_dict(o: Observation) -> dict:
    # Enforce the VLM confidence cap at the API boundary — a weak visual
    # signal never becomes a high-confidence diagnosis (docs/05 §3).
    conf = o.confidence
    if conf is not None:
        conf = min(conf, VLM_CONFIDENCE_CAP)
    return {
        "observation_type": o.observation_type,
        "state": o.state,
        "notes": o.notes,
        "confidence": conf,
    }


def _guard_to_dict(g: GuardedClassification) -> dict:
    return {
        "state": g.state,
        "top": (
            {"class_name": g.top.class_name, "probability": g.top.probability} if g.top else None
        ),
        "runner_up": (
            {"class_name": g.runner_up.class_name, "probability": g.runner_up.probability}
            if g.runner_up
            else None
        ),
        "margin": g.margin,
        "reason": g.reason,
    }


# ---------------------------------------------------------------------------
# App factory
# ---------------------------------------------------------------------------


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.started_at = time.monotonic()
    app.state.media_sets = MediaSetManager()
    # Probe engines once at startup — the kiosk device-agent starts Ollama
    # before the services, so a startup probe is cheap and avoids a network
    # timeout on every request when an engine is down.
    app.state.vision_available = app.state.extractor.available()
    app.state.classifier_available = app.state.classifier.available()
    yield


def create_app(
    extractor: ObservationExtractor | None = None,
    classifier: DiseaseClassifier | None = None,
    media_source: MediaSource | None = None,
) -> FastAPI:
    app = FastAPI(title="AI Kiosk — image-service", version=__version__, lifespan=lifespan)
    app.state.extractor = extractor or GemmaVisionExtractor()
    app.state.classifier = classifier or VitClassifier()
    app.state.media_source = media_source

    @app.exception_handler(MediaSourceUnavailable)
    async def _media_source_unavailable(
        request: Request, exc: MediaSourceUnavailable
    ) -> JSONResponse:
        return JSONResponse(
            status_code=503,
            media_type="application/problem+json",
            content=ProblemDetail(
                title="Media source unavailable",
                status=503,
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

    @app.get("/health", response_model=HealthResponse)
    def health(request: Request) -> HealthResponse:
        return HealthResponse(
            status="ok",
            service=SERVICE_NAME,
            version=__version__,
            uptime_s=round(time.monotonic() - request.app.state.started_at, 3),
        )

    @app.get("/ready", response_model=ReadyResponse)
    def ready(request: Request) -> ReadyResponse:
        """Ready when the local quality pipeline is up (always) — vision and
        the classifier are optional enhancements reported in dependencies."""
        return ReadyResponse(
            ready=True,
            dependencies={
                "quality_pipeline": True,
                "vision": bool(request.app.state.vision_available),
                "classifier": bool(request.app.state.classifier_available),
                "media_source": request.app.state.media_source is not None,
            },
        )

    @app.post("/v1/media/analyze", response_model=MediaAnalyzeResponse)
    def analyze(request: Request, body: MediaAnalyzeRequest) -> MediaAnalyzeResponse:
        """Image evidence extraction (docs/04 §1, roadmap §9.4.4).

        Quality first (deterministic); vision + classifier only on usable
        images; media-set bookkeeping so received views are never
        re-requested.
        """
        state = request.app.state

        # 1. Resolve image bytes (base64 direct, or media source).
        if body.image_b64:
            try:
                image_bytes = base64.b64decode(body.image_b64, validate=True)
            except (binascii.Error, ValueError):
                raise ValueError("image_b64 is not valid base64") from None
        elif body.media_ref:
            if state.media_source is None:
                raise MediaSourceUnavailable("media_ref given but no media source configured")
            image_bytes = state.media_source.fetch(body.media_ref)
        else:
            raise ValueError("provide image_b64 or media_ref")

        # 2. Deterministic quality checks (always run).
        quality = check_image_quality(image_bytes)

        # 3. Media-set bookkeeping.
        manager: MediaSetManager = state.media_sets
        media_id = new_ulid()
        if body.view is not None:
            if body.view not in ALL_VIEWS:
                raise ValueError(f"unknown view: {body.view} (allowed: {', '.join(ALL_VIEWS)})")
            if quality.usable:
                manager.record(body.case_id, body.view, media_id)
        requested = tuple(body.requested_views) if body.requested_views else DEFAULT_REQUESTED_VIEWS
        for v in requested:
            if v not in ALL_VIEWS:
                raise ValueError(f"unknown requested view: {v} (allowed: {', '.join(ALL_VIEWS)})")
        media_set = manager.get(body.case_id)
        missing = media_set.missing(requested)
        instructions = media_set.instructions(requested)

        # 4. Vision + classifier (only on usable images; degrade if down).
        observations: list[Observation] = []
        classification: GuardedClassification | None = None
        if quality.usable:
            if state.vision_available:
                context = ImageContext(crop=body.crop, stage=body.stage, region=body.region)
                observations = state.extractor.extract(image_bytes, context)
            if state.classifier_available:
                classification = classify_with_guard(image_bytes, state.classifier)

        return MediaAnalyzeResponse(
            media_id=media_id,
            quality={
                "usable": quality.usable,
                "reasons": quality.reasons,
                "retry_instruction": quality.retry_instruction,
                "metrics": {k: round(v, 3) for k, v in quality.metrics.items()},
            },
            observations=[_obs_to_dict(o) for o in observations],
            candidate_hypotheses=[
                {"hypothesis": h, "source": "vision", "strength": "weak"}
                for h in candidate_hypotheses(observations)
            ],
            classification=_guard_to_dict(classification) if classification else None,
            missing_views=missing,
            missing_view_instructions=instructions,
        )

    return app


app = create_app()
