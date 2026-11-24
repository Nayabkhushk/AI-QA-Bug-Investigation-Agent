"""
Legacy Gemini connectivity script.
Skipped by pytest — this is a standalone script, not a test module.
Run manually with: python test_gemini.py
"""
import pytest

pytestmark = pytest.mark.skip(
    reason="Legacy connectivity script — uses outdated client.get_model() API; not a Phase 6 test."
)


if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    from google import genai

    # Load .env (contains GEMINI_API_KEY and LLM_MODEL)
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    model_id = os.getenv("LLM_MODEL", "gemini-2.0-flash")

    if not api_key:
        raise RuntimeError("GEMINI_API_KEY not found in .env")

    client = genai.Client(api_key=api_key)

    # Send the test prompt directly (get_model() is not part of the current SDK)
    prompt = "Reply with exactly: Gemini API connection successful."
    response = client.models.generate_content(model=model_id, contents=prompt)

    print(f"Using model: {model_id}")
    print(response.text.strip())
