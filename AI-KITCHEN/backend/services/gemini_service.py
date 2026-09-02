from backend.utils.config import Config

# Lightweight wrapper around an external LLM (Gemini).
# This file intentionally provides a safe fallback when no API key is configured,
# so the app continues to work in offline or demo environments.

def generate_text(prompt: str, max_tokens: int = 256) -> str:
    """Generate text using Gemini if configured, otherwise return a mock response.

    Returns:
        str: Generated text or fallback string.
    """
    api_key = getattr(Config, 'GEMINI_API_KEY', '')

    if not api_key:
        # Demo fallback
        return f"[GEMINI MOCK] {prompt}"

    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        response = genai.generate_text(model="models/text-bison-001", input=prompt)
        return getattr(response, 'text', str(response))
    except Exception as e:
        # Fail gracefully in production -- return short error string
        return f"[GEMINI ERROR] {e}"
