import pytest
from app.agent.prompt_builder import build_investigation_prompt, _format_chunks


def test_build_prompt_with_chunks():
    query = "Login fails after password reset"
    chunks = [
        {
            "content": "The authentication token must be invalidated after password reset.",
            "metadata": {"doc_id": "REQ-001", "source": "Requirements"},
        },
        {
            "content": "API endpoint /login returns 401 when token is expired.",
            "metadata": {"doc_id": "API-042", "source": "API Docs"},
        },
    ]
    prompt = build_investigation_prompt(query, chunks)
    # Query part must be present
    assert "REPORTED BUG QUERY" in prompt
    assert query in prompt
    # Both chunks should be formatted with labels
    assert "Chunk 1 [REQ-001 (Requirements)]" in prompt
    assert "Chunk 2 [API-042 (API Docs)]" in prompt
    # Context separator should be present
    assert "RETRIEVED AND VALIDATED KNOWLEDGE‑BASE CONTEXT" in prompt


def test_build_prompt_no_chunks():
    query = "App crashes on startup"
    prompt = build_investigation_prompt(query, [])
    # Should contain only the query part and a trailing newline
    assert prompt.strip().endswith(query)
    assert "RETRIEVED" not in prompt


def test_format_chunks_skips_empty():
    chunks = [
        {"content": "   ", "metadata": {"doc_id": "DOC-1"}},
        {"content": "Valid content", "metadata": {"doc_id": "DOC-2"}},
    ]
    formatted = _format_chunks(chunks)
    # The empty content chunk should be omitted
    assert "DOC-1" not in formatted
    assert "DOC-2" in formatted
    assert "Valid content" in formatted

