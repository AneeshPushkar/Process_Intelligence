import json
import logging
from typing import Any, Dict, Optional
import httpx

from app.services.llm.base import BaseLLMProvider
from app.services.llm.local_provider import LocalFallbackProvider

logger = logging.getLogger(__name__)


class OpenAIProvider(BaseLLMProvider):
    """OpenAI API Provider supporting direct REST via httpx with graceful fallback."""

    def __init__(self, model_name: str = "gpt-4o-mini", temperature: float = 0.1, api_key: Optional[str] = None):
        super().__init__(model_name=model_name, temperature=temperature, api_key=api_key)
        self._fallback = LocalFallbackProvider()

    @property
    def provider_name(self) -> str:
        return f"OpenAI ({self.model_name})"

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        if not self.api_key:
            return self._fallback.generate(prompt, system_prompt)
        try:
            url = "https://api.openai.com/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            payload = {
                "model": self.model_name,
                "temperature": self.temperature,
                "messages": messages
            }
            with httpx.Client(timeout=20.0) as client:
                res = client.post(url, headers=headers, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    return data["choices"][0]["message"]["content"] or ""
            return self._fallback.generate(prompt, system_prompt)
        except Exception as e:
            logger.warning(f"OpenAI generate failed: {e}. Using local fallback.")
            return self._fallback.generate(prompt, system_prompt)

    def extract_process_data(self, process_name: str, process_description: str) -> Dict[str, Any]:
        if not self.api_key:
            return self._fallback.extract_process_data(process_name, process_description)
        try:
            url = "https://api.openai.com/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            system_prompt = (
                "You are an enterprise Business Process Analyst. Extract structured workflow models from process text. "
                "Output STRICT valid JSON without markdown wrapping."
            )
            user_prompt = (
                f"Extract structured process information from '{process_name}':\n\n"
                f"{process_description}\n\n"
                "Return a JSON object with keys:\n"
                "- title: string\n"
                "- summary: string\n"
                "- domain: string (e.g. Finance & Banking, Human Resources, Commerce & Logistics, Customer Support)\n"
                "- actors: array of string roles (e.g. Customer, System, HR, IT, Bank)\n"
                "- activities: array of objects {id, name, actor, description, is_conditional: bool, branch: 'yes'|'no'|null}\n"
                "- decisions: array of objects {id, condition, source_activity, branches: [{label: 'Yes', activity_ids: []}, {label: 'No', activity_ids: []}]}\n"
                "- dependencies: array of objects {from, to, type}\n"
                "- start_event: {id: 'node_start', name: string}\n"
                "- end_event: {id: 'node_end', name: string}\n"
                "- assumptions: array of strings\n"
                "- ambiguities: array of strings\n"
                "- contradictions: array of strings\n"
                "- analyst_confidence: float between 0 and 100\n"
                "Ensure decisions have clear condition labels (e.g. 'Product available?') and distinct Yes/No branches."
            )
            payload = {
                "model": self.model_name,
                "temperature": self.temperature,
                "response_format": {"type": "json_object"},
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            }
            with httpx.Client(timeout=25.0) as client:
                res = client.post(url, headers=headers, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    content = data["choices"][0]["message"]["content"]
                    parsed = json.loads(content)
                    parsed["provider_name"] = self.provider_name
                    return parsed
            return self._fallback.extract_process_data(process_name, process_description)
        except Exception as e:
            logger.warning(f"OpenAI extraction failed: {e}. Using local fallback.")
            return self._fallback.extract_process_data(process_name, process_description)

