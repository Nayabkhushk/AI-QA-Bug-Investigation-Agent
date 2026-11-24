"""LLM factory and agent module exports."""

from app.agent.config import LLMConfig
from app.agent.llm_client import (
    BaseLLMClient,
    GeminiLLMClient,
    LLMMetrics,
    InvestigationResult,
)
from app.agent.prompts import (
    INVESTIGATION_SYSTEM_PROMPT,
    INSUFFICIENT_EVIDENCE_FALLBACK,
)


def get_llm_client(config: LLMConfig = None) -> BaseLLMClient:
    """Factory to retrieve configured LLM client instance."""
    cfg = config or LLMConfig.from_env()
    provider = cfg.provider.lower()

    if provider == "gemini":
        return GeminiLLMClient(cfg)
    else:
        raise ValueError(
            f"Unsupported LLM provider: '{provider}'. Supported providers: 'gemini'."
        )


__all__ = [
    "LLMConfig",
    "BaseLLMClient",
    "GeminiLLMClient",
    "LLMMetrics",
    "InvestigationResult",
    "INVESTIGATION_SYSTEM_PROMPT",
    "INSUFFICIENT_EVIDENCE_FALLBACK",
    "get_llm_client",
]

