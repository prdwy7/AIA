"""FastAPI application for retrieval-service (docs/04 §2)."""

from __future__ import annotations

import time
from contextlib import asynccontextmanager
from datetime import date

from canonical_schema import HealthResponse, ReadyResponse
from fastapi import FastAPI, Request
from pydantic import BaseModel, Field

from retrieval_service._version import __version__
from retrieval_service.embed import BgeM3Embedder, HashEmbedder
from retrieval_service.hybrid import Filters, HybridRetriever, PassageStore
from retrieval_service.rank import Passage


class RetrievalFilters(BaseModel):
    crop: str | None = None
    stage: str | None = None
    region: str | None = None
    only_valid: bool = True


class RetrievalRequest(BaseModel):
    query: str = Field(min_length=1)
    filters: RetrievalFilters = Field(default_factory=RetrievalFilters)
    top_k: int = Field(default=10, ge=1, le=50)


class EvidenceItem(BaseModel):
    passage_id: str
    entry_id: str
    text: str
    method: str  # sql | keyword | vector | hybrid
    score: float
    rank: int
    authority_level: int
    relevance: float
    freshness: float


class RetrievalResponse(BaseModel):
    query: str
    results: list[EvidenceItem] = Field(default_factory=list)


def _default_store() -> PassageStore:
    """Dev store: a few Kurnool-crop passages so the API is demonstrable."""
    embedder = HashEmbedder()
    sample = [
        Passage(
            passage_id="p1",
            entry_id="e1",
            text_te="పసపు పురుగులపై నియంత్రణ: నీరం కలిపి పండ్లపై పిచికారీ చేయాలి",
            text_en="Cotton bollworm control: spray the diluted solution on the leaves",
            crop="cotton",
            stage="flowering",
            region="kurnool",
            authority_level=6,
            effective_from=date(2025, 6, 1),
            embedding=embedder.embed("cotton bollworm control spray leaves")[0],
        ),
        Passage(
            passage_id="p2",
            entry_id="e2",
            text_te="వరిలో వానకాలంలో వేరుశనగ వ్యాధి నివారణ",
            text_en="Paddy season groundnut disease prevention in the rains",
            crop="groundnut",
            stage="vegetative",
            region="kurnool",
            authority_level=4,
            effective_from=date(2024, 1, 1),
            embedding=embedder.embed("groundnut disease prevention paddy rains")[0],
        ),
    ]
    return PassageStore(sample)


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.started_at = time.monotonic()
    embedder = BgeM3Embedder() if BgeM3Embedder().available() else HashEmbedder()
    app.state.retriever = HybridRetriever(store=_default_store(), embedder=embedder)
    yield


def create_app() -> FastAPI:
    app = FastAPI(title="AI Kiosk — retrieval-service", version=__version__, lifespan=lifespan)

    @app.get("/health", response_model=HealthResponse)
    def health(request: Request) -> HealthResponse:
        return HealthResponse(
            status="ok",
            service="retrieval-service",
            version=__version__,
            uptime_s=round(time.monotonic() - request.app.state.started_at, 3),
        )

    @app.get("/ready", response_model=ReadyResponse)
    def ready(request: Request) -> ReadyResponse:
        retriever: HybridRetriever = request.app.state.retriever
        embedder_ok = retriever.embedder.available()
        return ReadyResponse(ready=embedder_ok, dependencies={"embedder": embedder_ok})

    @app.post("/v1/retrieval/search", response_model=RetrievalResponse)
    def search(request: Request, body: RetrievalRequest) -> RetrievalResponse:
        """Hybrid evidence retrieval (docs/04 §2).

        Every result carries method + score + authority level.
        """
        retriever: HybridRetriever = request.app.state.retriever
        results = retriever.search(
            query=body.query,
            filters=Filters(
                crop=body.filters.crop,
                stage=body.filters.stage,
                region=body.filters.region,
                only_valid=body.filters.only_valid,
            ),
            top_k=body.top_k,
        )
        return RetrievalResponse(
            query=body.query,
            results=[
                EvidenceItem(
                    passage_id=r.passage.passage_id,
                    entry_id=r.passage.entry_id,
                    text=r.passage.text_te,
                    method=r.method,
                    score=round(r.score, 6),
                    rank=r.rank,
                    authority_level=r.passage.authority_level,
                    relevance=round(r.relevance, 6),
                    freshness=round(r.freshness, 6),
                )
                for r in results
            ],
        )

    return app


app = create_app()
