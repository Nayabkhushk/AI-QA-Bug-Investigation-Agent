import pytest
from app.agent.source_utils import extract_source_ids


def test_extract_source_ids_basic():
    chunks = [
        {"metadata": {"doc_id": "REQ-001"}},
        {"metadata": {"doc_id": "API-042"}},
        {"metadata": {"doc_id": "REQ-001"}},  # duplicate should be ignored
    ]
    ids = extract_source_ids(chunks)
    assert ids == ["REQ-001", "API-042"]


def test_extract_source_ids_missing_or_malformed():
    chunks = [
        {"metadata": {}},
        {"metadata": {"doc_id": None}},
        {"metadata": {"doc_id": ""}},
        {"metadata": {"doc_id": "BUG-123"}},
    ]
    ids = extract_source_ids(chunks)
    assert ids == ["BUG-123"]

