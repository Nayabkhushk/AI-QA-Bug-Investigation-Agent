"""Modular LLM provider interface and Google Gemini implementation using google-genai."""

import time
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, List, Dict, Any

from app.agent.config import LLMConfig
from app.agent.prompts import INVESTIGATION_SYSTEM_PROMPT, INSUFFICIENT_EVIDENCE_FALLBACK
from app.agent.prompt_builder import build_investigation_prompt
from app.agent.source_utils import extract_source_ids

logger = logging.getLogger(__name__)


@dataclass
class LLMMetrics:
    """Latency, token usage, and cost tracking metrics."""
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    latency_ms: float = 0.0
    estimated_cost_usd: float = 0.0


@dataclass
class InvestigationResult:
    """Complete result returned from a grounded LLM investigation."""
    response_text: str
    is_fallback: bool
    sources: List[str]
    metrics: LLMMetrics
    chunks_used: int


class BaseLLMClient(ABC):
    """Abstract interface to ensure modularity across LLM providers."""

    @abstractmethod
    def generate_investigation(self, query: str, retrieved_chunks: List[Dict[str, Any]]) -> InvestigationResult:
        """Generate a grounded bug investigation from query and retrieved context."""
        pass

    @abstractmethod
    def test_connection(self) -> bool:
        """Test the provider connection with a basic prompt."""
        pass


class GeminiLLMClient(BaseLLMClient):
    """Google Gemini LLM client implementing the official google-genai SDK."""

    def __init__(self, config: Optional[LLMConfig] = None):
        self.config = config or LLMConfig.from_env()
        if not self.config.api_key:
            raise ValueError(
                "GEMINI_API_KEY is not configured. Please set GEMINI_API_KEY in your .env file."
            )

        # Import here to keep dependencies isolated
        from google import genai
        from google.genai import types

        self.genai = genai
        self.types = types
        self.client = genai.Client(api_key=self.config.api_key)

    def _calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Calculate estimated cost using configured rates per million tokens."""
        input_cost = (input_tokens / 1_000_000.0) * self.config.cost_per_million_input
        output_cost = (output_tokens / 1_000_000.0) * self.config.cost_per_million_output
        return round(input_cost + output_cost, 6)

# Deprecated: formatting moved to prompt_builder

    def _build_prompt(self, query: str, context_str: str) -> str:
        return (
            f"REPORTED BUG QUERY:\n{query}\n\n"
            f"RETRIEVED AND VALIDATED KNOWLEDGE BASE CONTEXT:\n"
            f"{context_str}\n\n"
            f"Perform the QA bug investigation following the system instructions strictly."
        )

    def _count_tokens(self, contents: str) -> int:
        """Count tokens using Gemini's official count_tokens API."""
        try:
            resp = self.client.models.count_tokens(
                model=self.config.model,
                contents=contents,
            )
            return getattr(resp, "total_tokens", 0) or 0
        except Exception as e:
            logger.warning(f"Token counting call failed, falling back to approximation: {e}")
            # Fallback estimation: ~4 chars per token
            return len(contents) // 4

    def test_connection(self) -> bool:
        """Verify API key and Gemini connection with a minimal prompt."""
        try:
            response = self.client.models.generate_content(
                model=self.config.model,
                contents="Respond with 'OK' to verify connectivity.",
            )
            return bool(response and response.text)
        except Exception as e:
            logger.error(f"Gemini connection test failed: {e}")
            raise


    def generate_investigation(self, query: str, retrieved_chunks: List[Dict[str, Any]]) -> InvestigationResult:
        start_time = time.perf_counter()

        # Check for empty context or empty query
        if not query.strip() or not retrieved_chunks:
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            return InvestigationResult(
                response_text=INSUFFICIENT_EVIDENCE_FALLBACK,
                is_fallback=True,
                sources=[],
                metrics=LLMMetrics(latency_ms=round(elapsed_ms, 2)),
                chunks_used=0,
            )

        # Truncate chunks if exceeding application-level LLM_MAX_INPUT_TOKENS
        active_chunks = list(retrieved_chunks)
        full_user_prompt = build_investigation_prompt(query, active_chunks)

        # Check total input tokens (system instruction + contents)
        total_input_text = f"{INVESTIGATION_SYSTEM_PROMPT}\n{full_user_prompt}"
        estimated_input_tokens = self._count_tokens(total_input_text)

        # Safe input handling: drop lowest reranked chunks if exceeding max input tokens
        while estimated_input_tokens > self.config.max_input_tokens and len(active_chunks) > 1:
            logger.info(
                f"Input tokens ({estimated_input_tokens}) exceeded limit ({self.config.max_input_tokens}). "
                "Reducing context chunks..."
            )
            active_chunks.pop()  # Drop lowest reranked chunk
            full_user_prompt = build_investigation_prompt(query, active_chunks)
            total_input_text = f"{INVESTIGATION_SYSTEM_PROMPT}\n{full_user_prompt}"
            estimated_input_tokens = self._count_tokens(total_input_text)

        # Configure generation parameters safely
        # Note: Do NOT pass max_input_tokens to GenerateContentConfig
        config_kwargs = {
            "system_instruction": INVESTIGATION_SYSTEM_PROMPT,
            "temperature": self.config.temperature,
            "max_output_tokens": self.config.max_output_tokens,
        }

        # Apply frequency_penalty only if explicitly set and non-zero
        if self.config.frequency_penalty > 0.0:
            config_kwargs["frequency_penalty"] = self.config.frequency_penalty

        gen_config = self.types.GenerateContentConfig(**config_kwargs)

        try:
            llm_call_start = time.perf_counter()
            response = self.client.models.generate_content(
                model=self.config.model,
                contents=full_user_prompt,
                config=gen_config,
            )
            latency_ms = (time.perf_counter() - llm_call_start) * 1000.0

            response_text = response.text or ""

            # Extract token usage from response metadata if available
            usage = getattr(response, "usage_metadata", None)
            if usage:
                in_tokens = getattr(usage, "prompt_token_count", estimated_input_tokens) or estimated_input_tokens
                out_tokens = getattr(usage, "candidates_token_count", 0) or 0
                total_tokens = getattr(usage, "total_token_count", in_tokens + out_tokens) or (in_tokens + out_tokens)
            else:
                in_tokens = estimated_input_tokens
                out_tokens = len(response_text) // 4
                total_tokens = in_tokens + out_tokens

            cost = self._calculate_cost(in_tokens, out_tokens)

            # Check if LLM triggered fallback
            is_fallback = "INSUFFICIENT EVIDENCE" in response_text.upper()

            # Collect source IDs from context chunks actually used
            sources = extract_source_ids(active_chunks)

            return InvestigationResult(
                response_text=response_text,
                is_fallback=is_fallback,
                sources=sources if not is_fallback else [],
                metrics=LLMMetrics(
                    input_tokens=in_tokens,
                    output_tokens=out_tokens,
                    total_tokens=total_tokens,
                    latency_ms=round(latency_ms, 2),
                    estimated_cost_usd=cost,
                ),
                chunks_used=len(active_chunks),
            )

        except Exception as e:
            logger.error(f"Error during LLM investigation generation: {e}")
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            return InvestigationResult(
                response_text=f"INVESTIGATION ERROR: An error occurred while communicating with the LLM ({e}).",
                is_fallback=True,
                sources=[],
                metrics=LLMMetrics(latency_ms=round(elapsed_ms, 2)),
                chunks_used=len(active_chunks),
            )

