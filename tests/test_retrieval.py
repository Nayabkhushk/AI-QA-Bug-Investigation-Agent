"""Unit and Integration tests for Phase 4: Hybrid Search & Retrieval (FAISS + BM25)."""

from pathlib import Path
import pytest

from app.rag.retrieval import HybridRetriever, BM25Index, tokenize_code_and_text
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
