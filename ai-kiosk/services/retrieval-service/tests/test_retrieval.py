"""retrieval-service tests: filters, keyword, vector, fusion, ranking."""

from __future__ import annotations

from datetime import date

import pytest
from fastapi.testclient import TestClient
from retrieval_service.app import create_app
from retrieval_service.embed import HashEmbedder
from retrieval_service.hybrid import Filters, HybridRetriever, PassageStore
from retrieval_service.rank import (
    Passage,
    authority_score,
    composite_score,
    freshness_score,
    rank_passages,
)

NOW = date(2026, 9, 1)
EMB = HashEmbedder()


def _passages() -> list[Passage]:
    return [
        Passage(
            passage_id="p1",
            entry_id="e1",
            text_te="పసపు పురుగు నియంత్రణ పిచికారీ",
            text_en="cotton bollworm control spray",
            crop="cotton",
            stage="flowering",
            region="kurnool",
            authority_level=6,
            effective_from=date(2025, 6, 1),
            embedding=EMB.embed("cotton bollworm control spray")[0],
        ),
        Passage(
            passage_id="p2",
            entry_id="e2",
            text_te="పసపు పురుగు నియంత్రణ పిచికారీ పాత పద్ధతి",
            text_en="cotton bollworm control spray old method",
            crop="cotton",
            stage="flowering",
            region="kurnool",
            authority_level=2,
            effective_from=date(2015, 1, 1),
            embedding=EMB.embed("cotton bollworm control spray old method")[0],
        ),
        Passage(
            passage_id="p3",
            entry_id="e3",
            text_te="వరి వ్యాధి నివారణ",
            text_en="paddy disease prevention",
            crop="paddy",
            stage="vegetative",
            region="kurnool",
            authority_level=5,
            effective_from=date(2025, 1, 1),
            embedding=EMB.embed("paddy disease prevention")[0],
        ),
        Passage(
            passage_id="p4",
            entry_id="e4",
            text_te="పసపు పురుగు నియంత్రణ రద్దయిన విధానం",
            text_en="cotton bollworm control retired method",
            crop="cotton",
            stage="flowering",
            region="kurnool",
            authority_level=6,
            effective_from=date(2020, 1, 1),
            effective_to=date(2024, 1, 1),  # retired
            embedding=EMB.embed("cotton bollworm control retired method")[0],
        ),
    ]


@pytest.fixture()
def retriever() -> HybridRetriever:
    return HybridRetriever(store=PassageStore(_passages()), embedder=EMB)


# ---------------------------------------------------------------------------
# Filters
# ---------------------------------------------------------------------------


def test_crop_filter_excludes_other_crops(retriever: HybridRetriever):
    results = retriever.search("cotton bollworm spray", Filters(crop="cotton"), now=NOW)
    assert results
    assert all(r.passage.crop == "cotton" for r in results)


def test_retired_passage_excluded_by_validity_filter(retriever: HybridRetriever):
    results = retriever.search("cotton bollworm spray", Filters(crop="cotton"), now=NOW)
    ids = {r.passage.passage_id for r in results}
    assert "p4" not in ids  # effective_to < now


def test_no_filter_includes_all_crops(retriever: HybridRetriever):
    results = retriever.search("cotton bollworm spray", Filters(only_valid=True), now=NOW)
    ids = {r.passage.passage_id for r in results}
    assert "p4" not in ids


# ---------------------------------------------------------------------------
# Keyword + vector + fusion
# ---------------------------------------------------------------------------


def test_keyword_match_found(retriever: HybridRetriever):
    results = retriever.search("cotton bollworm spray", Filters(crop="cotton"), now=NOW)
    assert results
    top = results[0]
    assert top.passage.passage_id in {"p1", "p2"}
    assert top.method in {"keyword", "vector", "hybrid"}


def test_every_result_carries_method_score_authority(retriever: HybridRetriever):
    results = retriever.search("cotton bollworm spray", Filters(crop="cotton"), now=NOW)
    for r in results:
        assert r.method in {"sql", "keyword", "vector", "hybrid"}
        assert 0.0 <= r.score <= 1.0
        assert 1 <= r.passage.authority_level <= 7
        assert r.rank >= 1


def test_ranks_are_sequential(retriever: HybridRetriever):
    results = retriever.search("cotton bollworm spray", Filters(crop="cotton"), now=NOW)
    assert [r.rank for r in results] == list(range(1, len(results) + 1))


def test_hybrid_method_when_both_signals_agree(retriever: HybridRetriever):
    # p1 matches on both keyword tokens and vector similarity.
    results = retriever.search("cotton bollworm control spray", Filters(crop="cotton"), now=NOW)
    methods = {r.passage.passage_id: r.method for r in results}
    assert methods.get("p1") == "hybrid"


# ---------------------------------------------------------------------------
# Composite ranking (authority + freshness + relevance)
# ---------------------------------------------------------------------------


def test_authority_breaks_relevance_ties():
    """Two passages with equal relevance: higher authority wins."""
    a = Passage(passage_id="a", entry_id="e", text_te="x", authority_level=7, effective_from=NOW)
    b = Passage(passage_id="b", entry_id="e", text_te="x", authority_level=1, effective_from=NOW)
    ranked = rank_passages([(a, "keyword", 0.8), (b, "keyword", 0.8)], NOW)
    assert ranked[0].passage.passage_id == "a"


def test_freshness_decays_with_age():
    assert freshness_score(date(2026, 8, 1), NOW) == 1.0
    assert freshness_score(date(2010, 1, 1), NOW) == 0.0
    mid = freshness_score(date(2015, 1, 1), NOW)
    assert 0.0 < mid < 1.0


def test_authority_score_bounds():
    assert authority_score(1) == 0.0
    assert authority_score(7) == 1.0
    assert 0.0 < authority_score(4) < 1.0


def test_composite_score_bounded():
    assert 0.0 <= composite_score(0.0, 0.0, 0.0) <= 1.0
    assert 0.0 <= composite_score(1.0, 1.0, 1.0) <= 1.0


def test_higher_authority_and_freshness_ranks_above_stale_low_authority(retriever: HybridRetriever):
    """p1 (authority 6, recent) should outrank p2 (authority 2, 2015) for the
    same query, all else equal."""
    results = retriever.search("cotton bollworm control spray", Filters(crop="cotton"), now=NOW)
    ids = [r.passage.passage_id for r in results]
    assert ids.index("p1") < ids.index("p2")


# ---------------------------------------------------------------------------
# API
# ---------------------------------------------------------------------------


@pytest.fixture()
def client():
    with TestClient(create_app()) as c:
        yield c


def test_health(client: TestClient):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["service"] == "retrieval-service"


def test_search_endpoint_returns_ranked_evidence(client: TestClient):
    r = client.post(
        "/v1/retrieval/search",
        json={"query": "cotton bollworm spray", "filters": {"crop": "cotton"}, "top_k": 5},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["query"] == "cotton bollworm spray"
    assert body["results"]
    for item in body["results"]:
        assert item["method"] in {"sql", "keyword", "vector", "hybrid"}
        assert item["authority_level"] >= 1
        assert item["rank"] >= 1
