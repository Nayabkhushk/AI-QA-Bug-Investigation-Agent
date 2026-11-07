import pytest
from app.rag.retrieval import BM25Index

# Sample corpus for testing BM25 and metadata filtering
SAMPLE_CORPUS = [
    {
        "chunk_id": "c1",
        "document_id": "REQ-1",
        "title": "Login requirement",
        "tags_str": "login",
        "text": "User can login using email and password.",
        "module": "Authentication",
        "document_type": "Requirement",
    },
    {
        "chunk_id": "c2",
        "document_id": "BUG-102",
        "title": "Login bug",
        "tags_str": "login bug",
        "text": "Login fails after password reset.",
        "module": "Authentication",
        "document_type": "BugReport",
    },
    {
        "chunk_id": "c3",
        "document_id": "REQ-2",
        "title": "Billing requirement",
        "tags_str": "billing",
        "text": "User can add credit card.",
        "module": "Billing",
        "document_type": "Requirement",
    },
]

@pytest.fixture(scope="module")
def bm25_index() -> BM25Index:
    """Create a BM25Index instance based on the sample corpus."""
    return BM25Index(corpus=SAMPLE_CORPUS)


def test_bm25_basic_search(bm25_index: BM25Index):
    """Basic keyword search should return relevant chunks in descending score order."""
    results = bm25_index.search(query="login", top_k=10)
    # Both authentication chunks contain the term "login"
    assert len(results) == 2
    # The highest‑scoring chunk should be the one with the exact term in the title/text
    assert results[0]["document_id"] in {"REQ-1", "BUG-102"}
    assert results[0]["bm25_score"] > 0


def test_bm25_metadata_filter_module(bm25_index: BM25Index):
    """Filtering by module should keep only matching chunks."""
    results = bm25_index.search(query="login", top_k=10, module="Authentication")
    assert len(results) == 2
    for r in results:
        assert r["module"] == "Authentication"


def test_bm25_metadata_filter_type(bm25_index: BM25Index):
    """Filtering by document_type should keep only matching chunks."""
    results = bm25_index.search(query="login", top_k=10, document_type="Requirement")
    # Only the requirement document matches the filter
    assert len(results) == 1
    assert results[0]["document_id"] == "REQ-1"
    assert results[0]["document_type"] == "Requirement"


def test_bm25_combined_filters(bm25_index: BM25Index):
    """Both module and document_type filters together should narrow results correctly."""
    results = bm25_index.search(query="login", top_k=10, module="Authentication", document_type="BugReport")
    assert len(results) == 1
    assert results[0]["document_id"] == "BUG-102"
    assert results[0]["module"] == "Authentication"
    assert results[0]["document_type"] == "BugReport"
