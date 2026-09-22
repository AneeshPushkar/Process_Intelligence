import os
from app.config import settings
from app.services.llm.base import BaseLLMProvider
from app.services.llm.local_provider import LocalFallbackProvider
from app.services.llm.openai_provider import OpenAIProvider
from app.services.llm.gemini_provider import GeminiProvider
from app.services.llm.anthropic_provider import AnthropicProvider


def get_llm_provider() -> BaseLLMProvider:
    """
    Factory to return the configured LLM provider.
    Defaults to LocalFallbackProvider if no external API key is provided.
    """
    provider_type = settings.LLM_PROVIDER.lower().strip()

    # Resolve API key from provider-specific settings, generic settings, or environment
    api_key = (
        (settings.OPENAI_API_KEY.strip() if provider_type == "openai" and settings.OPENAI_API_KEY else "")
        or (settings.GEMINI_API_KEY.strip() if provider_type == "gemini" and settings.GEMINI_API_KEY else "")
        or (settings.ANTHROPIC_API_KEY.strip() if provider_type == "anthropic" and settings.ANTHROPIC_API_KEY else "")
        or settings.LLM_API_KEY.strip()
        or (os.environ.get("OPENAI_API_KEY", "").strip() if provider_type == "openai" else "")
        or (os.environ.get("GEMINI_API_KEY", "").strip() if provider_type == "gemini" else "")
        or (os.environ.get("ANTHROPIC_API_KEY", "").strip() if provider_type == "anthropic" else "")
        or os.environ.get("LLM_API_KEY", "").strip()
        or None
    )

    # If no API key is configured for external providers, strictly fall back to Local Fallback
    if not api_key and provider_type in ["openai", "gemini", "anthropic"]:
        return LocalFallbackProvider(
            model_name="local-heuristic-v1",
            temperature=settings.LLM_TEMPERATURE
        )

    if provider_type == "openai" and api_key:
        return OpenAIProvider(
            model_name=settings.LLM_MODEL or "gpt-4o-mini",
            temperature=settings.LLM_TEMPERATURE,
            api_key=api_key
        )
    elif provider_type == "gemini" and api_key:
        return GeminiProvider(
            model_name=settings.LLM_MODEL or "gemini-1.5-flash",
            temperature=settings.LLM_TEMPERATURE,
            api_key=api_key
        )
    elif provider_type == "anthropic" and api_key:
        return AnthropicProvider(
            model_name=settings.LLM_MODEL or "claude-3-5-sonnet-20241022",
            temperature=settings.LLM_TEMPERATURE,
            api_key=api_key
        )
    else:
        return LocalFallbackProvider(
            model_name=settings.LLM_MODEL or "local-heuristic-v1",
            temperature=settings.LLM_TEMPERATURE
        )
