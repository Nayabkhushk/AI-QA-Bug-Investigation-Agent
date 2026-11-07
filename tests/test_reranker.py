"""Unit and Integration tests for Phase 5: Cross-Encoder Reranking."""

import pytest
from app.rag.reranker import DocumentReranker


@pytest.fixture(scope="module")
def reranker():
    """Shared DocumentReranker instance for tests."""
    return DocumentReranker()


@pytest.fixture
def sample_candidates():
    """Representative candidate chunks from hybrid retrieval."""
    return [
        {
            "chunk_id": "BUG-102_c0",
            "document_id": "BUG-102",
            "title": "BUG-102: Users Unable to Login After Password Reset",
            "module": "Authentication",
            "document_type": "BugReport",
            "text": "Users receive invalid session credentials after resetting password due to stale cache.",
            "hybrid_score": 0.0163,
            "hybrid_rank": 1,
        },
        {
            "chunk_id": "BUG-102_c1",
            "document_id": "BUG-102",
            "title": "BUG-102: Root Cause Analysis",
            "module": "Authentication",
            "document_type": "BugReport",
            "text": "Redis session cache TTL was not expired immediately upon password change confirmation.",
            "hybrid_score": 0.0161,
            "hybrid_rank": 2,
        },
        {
            "chunk_id": "PAY-REQ-001_c0",
            "document_id": "PAY-REQ-001",
            "title": "Payment Gateway Requirements",
            "module": "Billing",
            "document_type": "Requirement",
            "text": "All credit card transactions must comply with PCI-DSS tokenization standards.",
            "hybrid_score": 0.0120,
            "hybrid_rank": 3,
        },
        {
            "chunk_id": "TC-AUTH-014_c0",
            "document_id": "TC-AUTH-014",
            "title": "TC-AUTH-014: Password Reset Session Invalidation",
            "module": "Authentication",
            "document_type": "TestCase",
            "text": "Verify active auth token is rejected after user completes password reset flow.",
            "hybrid_score": 0.0115,
            "hybrid_rank": 4,
        },
    ]


def test_reranker_reorders_by_relevance(reranker: DocumentReranker, sample_candidates):
    """Verify that reranker scores relevant auth documents higher than unrelated billing docs."""
    query = "Login fails after password reset for some users"
    results = reranker.rerank(query=query, documents=sample_candidates, top_k=4, max_chunks_per_doc=None)

    assert len(results) == 4
    # Highest scoring document should be the directly relevant bug report
    assert results[0]["document_id"] == "BUG-102"
    # Unrelated billing document must be ranked lowest
    assert results[-1]["document_id"] == "PAY-REQ-001"
    # Scores must be strictly descending
    scores = [r["rerank_score"] for r in results]
    assert scores == sorted(scores, reverse=True)


def test_reranker_preserves_metadata(reranker: DocumentReranker, sample_candidates):
    """Verify that reranking preserves all original chunk metadata and IDs."""
    query = "Password reset issue"
    results = reranker.rerank(query=query, documents=sample_candidates, top_k=2)

    for doc in results:
        assert "document_id" in doc
        assert "title" in doc
        assert "module" in doc
        assert "text" in doc
        assert "hybrid_score" in doc
        assert "rerank_score" in doc
        assert "rerank_rank" in doc


def test_reranker_diversity_filter(reranker: DocumentReranker, sample_candidates):
    """Verify max_chunks_per_doc limits multiple chunks from the same document."""
    query = "Password reset credentials rejected"
    # Limit to at most 1 chunk per document
    results = reranker.rerank(query=query, documents=sample_candidates, top_k=3, max_chunks_per_doc=1)

    doc_ids = [r["document_id"] for r in results]
    # BUG-102 should only appear once despite having 2 strong candidate chunks
    assert doc_ids.count("BUG-102") == 1
    # Another relevant document should be promoted into the results
    assert "TC-AUTH-014" in doc_ids


def test_reranker_latency_and_metrics(reranker: DocumentReranker, sample_candidates):
    """Verify latency and observability metrics are tracked."""
    query = "Authentication token expiration"
    reranker.rerank(query=query, documents=sample_candidates, top_k=3)
    metrics = reranker.last_rerank_metrics

    assert "rerank_latency_ms" in metrics
    assert "input_count" in metrics
    assert "output_count" in metrics
    assert "top_score" in metrics
    assert metrics["rerank_latency_ms"] > 0
    assert metrics["input_count"] == len(sample_candidates)
    assert metrics["output_count"] == 3


def test_reranker_min_score_cutoff(reranker: DocumentReranker, sample_candidates):
    """Verify min_score threshold drops irrelevant chunks."""
    query = "Login credentials rejected"
    # Set a high threshold that filters out low/negative scores
    results = reranker.rerank(query=query, documents=sample_candidates, top_k=4, min_score=0.0)

    for doc in results:
        assert doc["rerank_score"] >= 0.0


def test_reranker_empty_inputs(reranker: DocumentReranker):
    """Verify handling of empty queries or empty document lists."""
    assert reranker.rerank(query="", documents=[]) == []
    assert reranker.rerank(query="valid query", documents=[]) == []
    assert reranker.last_rerank_metrics["rerank_latency_ms"] == 0.0

