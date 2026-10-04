"""Unit & Integration tests for Phase 2: Ingestion, Chunking & FAISS Vector DB."""

import shutil
from pathlib import Path
import pytest

from app.rag.ingestion import load_all_documents, load_document, chunk_document

# ---------------------------------------------------------------------------
# FAISS vector store is imported only if the index already exists.
# The index is built by running `python ingest.py` before the test suite.
# ---------------------------------------------------------------------------
FAISS_INDEX_DIR = "./faiss_index"


def test_load_all_31_documents():
    """Verify all 31 CallFlow CRM dataset documents load successfully with correct types."""
    docs = load_all_documents("data")
    assert len(docs) == 31, f"Expected 31 documents, got {len(docs)}"

    types_count: dict[str, int] = {}
    for d in docs:
        doc_type = d["document_type"]
        types_count[doc_type] = types_count.get(doc_type, 0) + 1

    assert types_count.get("Requirement") == 5, f"Expected 5 Requirements, got {types_count.get('Requirement')}"
    assert types_count.get("ApiDocumentation") == 5, f"Expected 5 API Docs, got {types_count.get('ApiDocumentation')}"
    assert types_count.get("TestCase") == 8, f"Expected 8 Test Cases, got {types_count.get('TestCase')}"
    assert types_count.get("BugReport") == 10, f"Expected 10 Bug Reports, got {types_count.get('BugReport')}"
    assert types_count.get("QaGuideline") == 3, f"Expected 3 QA Guidelines, got {types_count.get('QaGuideline')}"


def test_metadata_completeness():
    """Verify all documents contain non-empty required metadata fields."""
    docs = load_all_documents("data")
    required_keys = ["document_id", "title", "document_type", "module", "priority", "status", "tags", "content"]

    for d in docs:
        for k in required_keys:
            assert d.get(k) is not None, f"Document {d.get('file_path')} missing key {k}"
        assert len(d["content"].strip()) > 50, f"Document {d['document_id']} has empty or too short content"
        assert len(d["tags"]) > 0, f"Document {d['document_id']} has no tags"


def test_chunking_preserves_context():
    """Verify section-aware chunking preserves metadata and splits long documents cleanly."""
    doc = load_document("data/requirements/AUTH-REQ-002.md")
    chunks = chunk_document(doc, max_chunk_words=150)

    assert len(chunks) >= 1
    for chunk in chunks:
        assert chunk["document_id"] == "AUTH-REQ-002"
        assert chunk["module"] == "Authentication"
        assert chunk["document_type"] == "Requirement"
        assert len(chunk["text"].strip()) > 0
        assert chunk["chunk_id"].startswith("AUTH-REQ-002_c")


@pytest.mark.skipif(
    not (Path(FAISS_INDEX_DIR) / "index.faiss").exists(),
    reason="FAISS index not built — run `python ingest.py` first",
)
def test_faiss_vector_store_search():
    """Verify FAISS index returns relevant documents for the PRD sample query.

    Requires the index to be built first:
        python ingest.py
    """
    from app.rag.vector_store import FAISSVectorStore

    store = FAISSVectorStore(index_dir=FAISS_INDEX_DIR)

    assert store.count() > 0, "Index is empty"

    query = "Login fails after password reset for some users"
    results = store.similarity_search(query=query, top_k=5)

    assert len(results) > 0, "FAISS search returned no results"

    retrieved_doc_ids = [r["document_id"] for r in results]
    print(f"\nTop-5 retrieved for '{query}': {retrieved_doc_ids}")

    # At least one of the expected auth-related docs must appear in top-5
    expected = {"AUTH-REQ-002", "BUG-102", "BUG-147", "TC-AUTH-014"}
    overlap = expected.intersection(set(retrieved_doc_ids))
    assert len(overlap) >= 1, f"Expected one of {expected} in top-5, got {retrieved_doc_ids}"


@pytest.mark.skipif(
    not (Path(FAISS_INDEX_DIR) / "index.faiss").exists(),
    reason="FAISS index not built — run `python ingest.py` first",
)
def test_faiss_get_document_by_id():
    """Verify a full document can be reassembled from chunked FAISS metadata."""
    from app.rag.vector_store import FAISSVectorStore

    store = FAISSVectorStore(index_dir=FAISS_INDEX_DIR)
    doc = store.get_document_by_id("AUTH-REQ-002")

    assert doc is not None
    assert doc["document_id"] == "AUTH-REQ-002"
    assert "Password Reset" in doc["title"]
    assert "token_version" in doc["content"]
