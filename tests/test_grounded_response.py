"""Unit and integration tests for Phase 6 Grounded LLM Response."""

import pytest
from unittest.mock import MagicMock, patch

from app.agent.config import LLMConfig
from app.agent.prompts import INSUFFICIENT_EVIDENCE_FALLBACK, INVESTIGATION_SYSTEM_PROMPT
from app.agent.llm_client import GeminiLLMClient, LLMMetrics, InvestigationResult


def test_llm_config_defaults():
    """Verify LLMConfig loads default limits and settings accurately."""
    config = LLMConfig(
        provider="gemini",
        api_key="test_key",
        model="gemini-3.8-flash",
        temperature=0.1,
        max_output_tokens=2048,
        max_input_tokens=8000,
        frequency_penalty=0.0,
    )
    assert config.temperature == 0.1
    assert config.max_output_tokens == 2048
    assert config.max_input_tokens == 8000
    assert config.frequency_penalty == 0.0


def test_empty_context_triggers_fallback():
    """Test that empty retrieved context immediately returns insufficient evidence fallback."""
    with patch("google.genai.Client"):
        client = GeminiLLMClient(LLMConfig(api_key="mock_key"))
        result = client.generate_investigation(
            query="Login fails after password reset",
            retrieved_chunks=[],
        )
        assert result.is_fallback is True
        assert "INSUFFICIENT EVIDENCE" in result.response_text
        assert result.sources == []
        assert result.chunks_used == 0


def test_empty_query_triggers_fallback():
    """Test that empty or whitespace query returns fallback response."""
    with patch("google.genai.Client"):
        client = GeminiLLMClient(LLMConfig(api_key="mock_key"))
        result = client.generate_investigation(
            query="   ",
            retrieved_chunks=[{"doc_id": "AUTH-01", "content": "Sample content"}],
        )
        assert result.is_fallback is True
        assert "INSUFFICIENT EVIDENCE" in result.response_text


def test_grounded_response_generation_and_metrics():
    """Test successful grounded response generation with token tracking and cost calculation."""
    mock_genai_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = (
        "BUG ANALYSIS\n\nLikely Module: Authentication\n\n"
        "Sources: AUTH-REQ-002, BUG-102"
    )
    mock_usage = MagicMock()
    mock_usage.prompt_token_count = 150
    mock_usage.candidates_token_count = 50
    mock_usage.total_token_count = 200
    mock_response.usage_metadata = mock_usage
    mock_genai_client.models.generate_content.return_value = mock_response

    mock_count_resp = MagicMock()
    mock_count_resp.total_tokens = 150
    mock_genai_client.models.count_tokens.return_value = mock_count_resp

    with patch("google.genai.Client", return_value=mock_genai_client):
        client = GeminiLLMClient(LLMConfig(api_key="mock_key", model="gemini-3.8-flash"))
        chunks = [
            {
                "doc_id": "AUTH-REQ-002",
                "title": "Password Reset Flow",
                "category": "Requirements",
                "content": "Users can reset passwords via email token.",
            },
            {
                "doc_id": "BUG-102",
                "title": "Session Invalidation Failure",
                "category": "Bug Reports",
                "content": "Sessions remain active after password change.",
            },
        ]
        result = client.generate_investigation("Password reset login failure", chunks)

        assert result.is_fallback is False
        assert "BUG ANALYSIS" in result.response_text
        assert "AUTH-REQ-002" in result.sources
        assert "BUG-102" in result.sources
        assert result.chunks_used == 2
        assert result.metrics.input_tokens == 150
        assert result.metrics.output_tokens == 50
        assert result.metrics.total_tokens == 200
        assert result.metrics.estimated_cost_usd > 0.0


def test_oversized_input_token_trimming():
    """Test that input exceeding max_input_tokens safely reduces context chunks."""
    mock_genai_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "BUG ANALYSIS\n\nLikely Module: Auth\n\nSources: DOC-1"
    mock_response.usage_metadata = None
    mock_genai_client.models.generate_content.return_value = mock_response

    # Simulate token count: first call exceeds 100 limit, second call fits under 100
    mock_genai_client.models.count_tokens.side_effect = [
        MagicMock(total_tokens=150),
        MagicMock(total_tokens=70),
    ]

    with patch("google.genai.Client", return_value=mock_genai_client):
        cfg = LLMConfig(api_key="mock_key", max_input_tokens=100)
        client = GeminiLLMClient(cfg)
        chunks = [
            {"doc_id": "DOC-1", "title": "First", "category": "Req", "content": "First doc"},
            {"doc_id": "DOC-2", "title": "Second", "category": "Req", "content": "Second doc"},
        ]
        result = client.generate_investigation("Test query", chunks)

        # One chunk should have been dropped to satisfy the limit
        assert result.chunks_used == 1
        assert result.sources == ["DOC-1"]

