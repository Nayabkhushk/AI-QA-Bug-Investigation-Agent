"""Unit and Integration tests for Phase 4: Hybrid Search & Retrieval (FAISS + BM25)."""

import os
import time
from pathlib import Path
import pytest

from app.rag.retrieval import HybridRetriever, BM25Index, RetrievalCache, tokenize_code_and_text
from app.rag.vector_store import FAISSVectorStore

FAISS_INDEX_DIR = "./faiss_index"


@pytest.fixture(scope="module")
def retriever():
    """Shared HybridRetriever instance loaded from the pre-built FAISS index."""
    if not (Path(FAISS_INDEX_DIR) / "index.faiss").exists():
        pytest.skip("FAISS index not built — run `python ingest.py` first")
    return HybridRetriever(index_dir=FAISS_INDEX_DIR)


def test_tokenizer_preserves_identifiers():
    """Verify tokenizer retains compound technical terms like bug and requirement IDs."""
    text = "Error in BUG-102: POST /api/v1/auth/reset failed with token_version mismatch."
    tokens = tokenize_code_and_text(text)

    assert "bug-102" in tokens
    assert "token_version" in tokens
    assert "auth" in tokens
    assert "reset" in tokens


def test_bm25_exact_bug_id_lookup(retriever: HybridRetriever):
    """Verify BM25 directly pinpoints exact bug IDs like BUG-102 with rank 1."""
    results = retriever.sparse_search("BUG-102", top_k=5)

    assert len(results) > 0
    top_doc_ids = [r["document_id"] for r in results[:3]]
    assert "BUG-102" in top_doc_ids
    assert results[0]["document_id"] == "BUG-102"
    assert results[0]["bm25_score"] > 0


def test_bm25_metadata_filter(retriever: HybridRetriever):
    """Verify BM25 respects module and document_type filters."""
    results = retriever.sparse_search(
        query="login session",
        top_k=10,
        module="Authentication",
        document_type="Requirement",
    )

    assert len(results) > 0
    for r in results:
        assert r["module"] == "Authentication"
        assert r["document_type"] == "Requirement"


def test_dense_semantic_search(retriever: HybridRetriever):
    """Verify FAISS semantic search finds conceptually relevant docs without exact keyword overlap."""
    query = "Customer credentials rejected immediately following password modification"
    results = retriever.dense_search(query=query, top_k=5)

    assert len(results) > 0
    top_ids = [r["document_id"] for r in results]
    # Should retrieve auth password reset requirements or bugs
    auth_matches = [doc_id for doc_id in top_ids if "AUTH" in doc_id or doc_id in {"BUG-102", "BUG-147"}]
    assert len(auth_matches) >= 1


def test_hybrid_retrieval_rrf_ranking(retriever: HybridRetriever):
    """Verify hybrid search fuses dense and sparse rankings with RRF scores."""
    query = "Login fails after password reset for some users BUG-102"
    results = retriever.retrieve(query=query, top_k=5)

    assert len(results) > 0
    for rank, r in enumerate(results, start=1):
        assert "hybrid_score" in r
        assert r["hybrid_rank"] == rank
        assert r["hybrid_score"] > 0

    top_ids = [r["document_id"] for r in results]
    assert "BUG-102" in top_ids or "AUTH-REQ-002" in top_ids


def test_hybrid_retrieval_empty_query(retriever: HybridRetriever):
    """Verify empty query returns empty results cleanly."""
    results = retriever.retrieve(query="", top_k=5)
    assert results == []


# ---------------------------------------------------------------------------
# Phase 4 Completion — Latency Tracking, Caching, and Cache Invalidation
# ---------------------------------------------------------------------------


def test_retrieval_metrics_populated(retriever: HybridRetriever):
    """Verify that last_retrieval_metrics contains expected keys after retrieve()."""
    retriever.retrieve(query="Login fails after password reset", top_k=5)
    m = retriever.last_retrieval_metrics

    assert "dense_latency_ms" in m
    assert "sparse_latency_ms" in m
    assert "total_latency_ms" in m
    assert "cache_hit" in m
    assert "result_count" in m
    assert m["dense_latency_ms"] >= 0
    assert m["sparse_latency_ms"] >= 0
    assert m["total_latency_ms"] >= 0
    assert m["cache_hit"] is False  # First call — not cached
    assert m["result_count"] > 0


def test_retrieval_metrics_empty_query(retriever: HybridRetriever):
    """Verify metrics are set correctly for an empty query."""
    retriever.retrieve(query="", top_k=5)
    m = retriever.last_retrieval_metrics

    assert m["total_latency_ms"] == 0.0
    assert m["cache_hit"] is False
    assert m["result_count"] == 0


def test_cache_hit_on_repeated_query(retriever: HybridRetriever):
    """Verify that a repeated identical query returns a cache hit."""
    query = "session token invalidation after logout"
    retriever._cache.clear()

    # First call — cache miss
    results_1 = retriever.retrieve(query=query, top_k=5)
    assert retriever.last_retrieval_metrics["cache_hit"] is False

    # Second call — cache hit
    results_2 = retriever.retrieve(query=query, top_k=5)
    assert retriever.last_retrieval_metrics["cache_hit"] is True
    assert retriever.last_retrieval_metrics["result_count"] == len(results_1)

    # Results should be equivalent
    ids_1 = [r["chunk_id"] for r in results_1]
    ids_2 = [r["chunk_id"] for r in results_2]
    assert ids_1 == ids_2


def test_cache_miss_on_different_params(retriever: HybridRetriever):
    """Verify different query parameters produce cache misses."""
    retriever._cache.clear()

    retriever.retrieve(query="password reset", top_k=5)
    assert retriever.last_retrieval_metrics["cache_hit"] is False

    # Same query, different top_k — must be a miss
    retriever.retrieve(query="password reset", top_k=3)
    assert retriever.last_retrieval_metrics["cache_hit"] is False


def test_cache_invalidation_on_index_change(retriever: HybridRetriever):
    """Verify cache is invalidated when the FAISS index file is modified."""
    retriever._cache.clear()
    query = "MFA verification timeout"

    # Populate cache
    retriever.retrieve(query=query, top_k=5)
    assert retriever._cache.size() > 0

    # Simulate an index rebuild by touching the FAISS index file
    index_path = Path(FAISS_INDEX_DIR) / "index.faiss"
    original_mtime = index_path.stat().st_mtime

    # Touch the file to update its modification time
    os.utime(index_path, None)

    # Next cache lookup should detect the change and invalidate
    result = retriever._cache.get(query, 5, None, None, 0.5)
    assert result is None
    assert retriever._cache.size() == 0

    # Restore original mtime to avoid side effects on other tests
    os.utime(index_path, (original_mtime, original_mtime))


def test_cache_ttl_expiry():
    """Verify that cache entries expire after their TTL."""
    cache = RetrievalCache(max_size=10, ttl_seconds=0.1, index_dir="./faiss_index")

    cache.put("test query", 5, None, None, 0.5, [{"chunk_id": "c1", "text": "test"}])
    assert cache.size() == 1

    # Entry should be available immediately
    result = cache.get("test query", 5, None, None, 0.5)
    assert result is not None

    # Wait for TTL to expire
    time.sleep(0.15)

    # Entry should now be expired
    result = cache.get("test query", 5, None, None, 0.5)
    assert result is None


def test_cache_max_size_eviction():
    """Verify that cache evicts the oldest entry when max_size is reached."""
    cache = RetrievalCache(max_size=2, ttl_seconds=300.0, index_dir="./faiss_index")

    cache.put("query1", 5, None, None, 0.5, [{"chunk_id": "c1"}])
    time.sleep(0.01)  # Ensure distinct timestamps
    cache.put("query2", 5, None, None, 0.5, [{"chunk_id": "c2"}])
    assert cache.size() == 2

    # Adding a third entry should evict the oldest (query1)
    time.sleep(0.01)
    cache.put("query3", 5, None, None, 0.5, [{"chunk_id": "c3"}])
    assert cache.size() == 2

    assert cache.get("query1", 5, None, None, 0.5) is None  # Evicted
    assert cache.get("query2", 5, None, None, 0.5) is not None  # Still there
    assert cache.get("query3", 5, None, None, 0.5) is not None  # Still there
