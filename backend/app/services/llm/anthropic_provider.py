from typing import Any, Dict, Optional
from app.services.llm.base import BaseLLMProvider
from app.services.llm.local_provider import LocalFallbackProvider


class AnthropicProvider(BaseLLMProvider):
    """Anthropic Claude API Provider with fallback."""

    def __init__(self, model_name: str = "claude-3-5-sonnet-20241022", temperature: float = 0.1, api_key: Optional[str] = None):
        super().__init__(model_name=model_name, temperature=temperature, api_key=api_key)
        self._fallback = LocalFallbackProvider()

    @property
    def provider_name(self) -> str:
        return "Anthropic"

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        if not self.api_key:
            return self._fallback.generate(prompt, system_prompt)
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=self.api_key)
            msg = client.messages.create(
                model=self.model_name,
                max_tokens=2048,
                system=system_prompt or "You are an enterprise process intelligence specialist.",
                messages=[{"role": "user", "content": prompt}]
            )
            return msg.content[0].text
        except Exception:
            return self._fallback.generate(prompt, system_prompt)

    def extract_process_data(self, process_name: str, process_description: str) -> Dict[str, Any]:
        if not self.api_key:
            return self._fallback.extract_process_data(process_name, process_description)
        try:
            import json
            import anthropic
            client = anthropic.Anthropic(api_key=self.api_key)
            prompt = (
                f"Extract structured process information from '{process_name}':\n\n{process_description}\n\n"
                "Return ONLY valid JSON matching: title, summary, domain, actors, activities, decisions, "
                "dependencies, start_event, end_event, assumptions, ambiguities, contradictions, analyst_confidence."
            )
            msg = client.messages.create(
                model=self.model_name,
                max_tokens=2048,
                messages=[{"role": "user", "content": prompt}]
            )
            text = msg.content[0].text
            # Extract JSON from potential code block
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()
            return json.loads(text)
        except Exception:
            return self._fallback.extract_process_data(process_name, process_description)
