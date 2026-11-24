"""Configuration settings for LLM and investigation pipeline."""

import os
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


@dataclass
class LLMConfig:
    """Configuration parameters for LLM interactions."""
    provider: str = os.getenv("LLM_PROVIDER", "gemini").lower()
    api_key: str = os.getenv("GEMINI_API_KEY", "")
    model: str = os.getenv("LLM_MODEL", "gemini-3.8-flash")
    temperature: float = float(os.getenv("LLM_TEMPERATURE", "0.1"))
    max_output_tokens: int = int(os.getenv("LLM_MAX_OUTPUT_TOKENS", "2048"))
    max_input_tokens: int = int(os.getenv("LLM_MAX_INPUT_TOKENS", "8000"))
    frequency_penalty: float = float(os.getenv("LLM_FREQUENCY_PENALTY", "0.0"))

    # Approximate Gemini Flash pricing per million tokens (USD)
    # Gemini 2.5 Flash / 1.5 Flash reference rate
    cost_per_million_input: float = 0.075
    cost_per_million_output: float = 0.30

    @classmethod
    def from_env(cls) -> "LLMConfig":
        return cls()

