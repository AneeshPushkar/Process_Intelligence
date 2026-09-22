from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class BaseLLMProvider(ABC):
    """Abstract base class for all LLM providers (Cloud & Local Fallback)."""

    def __init__(self, model_name: str, temperature: float = 0.1, api_key: Optional[str] = None):
        self.model_name = model_name
        self.temperature = temperature
        self.api_key = api_key

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Name of the provider (e.g. 'Local Fallback', 'OpenAI', 'Gemini', 'Anthropic')."""
        pass

    @abstractmethod
    def generate(self, prompt: str, system_prompt: str = "") -> str:
        """Generate a text completion given prompt and system instructions."""
        pass

    @abstractmethod
    def extract_process_data(self, process_name: str, process_description: str) -> Dict[str, Any]:
        """Extract structured process analysis data."""
        pass
