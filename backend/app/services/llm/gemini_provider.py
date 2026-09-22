import json
import logging
import re
from typing import Any, Dict, Optional
import httpx

from app.services.llm.base import BaseLLMProvider
from app.services.llm.local_provider import LocalFallbackProvider

logger = logging.getLogger(__name__)


class GeminiProvider(BaseLLMProvider):
    """Google Gemini API Provider supporting direct REST via httpx with graceful fallback."""

    def __init__(self, model_name: str = "gemini-1.5-flash", temperature: float = 0.1, api_key: Optional[str] = None):
        super().__init__(model_name=model_name, temperature=temperature, api_key=api_key)
        self._fallback = LocalFallbackProvider()

    @property
    def provider_name(self) -> str:
        return f"Google Gemini ({self.model_name})"

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        if not self.api_key:
            return self._fallback.generate(prompt, system_prompt)
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent?key={self.api_key}"
            contents = []
            if system_prompt:
                contents.append({"role": "user", "parts": [{"text": f"System Instructions: {system_prompt}"}]})
            contents.append({"role": "user", "parts": [{"text": prompt}]})

            payload = {
                "contents": contents,
                "generationConfig": {"temperature": self.temperature}
            }
            with httpx.Client(timeout=20.0) as client:
                res = client.post(url, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    candidates = data.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        if parts:
                            return parts[0].get("text", "")
            return self._fallback.generate(prompt, system_prompt)
        except Exception as e:
            logger.warning(f"Gemini generate failed: {e}. Using local fallback.")
            return self._fallback.generate(prompt, system_prompt)

    def extract_process_data(self, process_name: str, process_description: str) -> Dict[str, Any]:
        if not self.api_key:
            return self._fallback.extract_process_data(process_name, process_description)
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent?key={self.api_key}"
            prompt = (
                f"You are an enterprise Business Process Analyst. Extract structured workflow models from the process titled '{process_name}':\n\n"
                f"{process_description}\n\n"
                "Return STRICT valid JSON matching this schema:\n"
                "{\n"
                '  "title": string,\n'
                '  "summary": string,\n'
                '  "domain": string,\n'
                '  "actors": ["Actor1", "Actor2"],\n'
                '  "activities": [{"id": "act_1", "name": "...", "actor": "...", "description": "...", "is_conditional": false, "branch": null}],\n'
                '  "decisions": [{"id": "gw_1", "condition": "Condition?", "source_activity": "act_1", "branches": [{"label": "Yes", "activity_ids": []}, {"label": "No", "activity_ids": []}]}],\n'
                '  "dependencies": [{"from": "node_start", "to": "act_1", "type": "sequential"}],\n'
                '  "start_event": {"id": "node_start", "name": "Start: ..."},\n'
                '  "end_event": {"id": "node_end", "name": "Process Completed"},\n'
                '  "assumptions": [],\n'
                '  "ambiguities": [],\n'
                '  "contradictions": [],\n'
                '  "analyst_confidence": 90.0\n'
                "}\n"
                "Only return JSON without markdown code blocks."
            )
            payload = {
                "contents": [{"role": "user", "parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": self.temperature,
                    "responseMimeType": "application/json"
                }
            }
            with httpx.Client(timeout=25.0) as client:
                res = client.post(url, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    candidates = data.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        if parts:
                            raw_json = parts[0].get("text", "").strip()
                            # Clean potential markdown wrapping if returned
                            clean_json = re.sub(r"^```json\s*", "", raw_json)
                            clean_json = re.sub(r"\s*```$", "", clean_json)
                            parsed = json.loads(clean_json)
                            parsed["provider_name"] = self.provider_name
                            return parsed
            return self._fallback.extract_process_data(process_name, process_description)
        except Exception as e:
            logger.warning(f"Gemini extraction failed: {e}. Using local fallback.")
            return self._fallback.extract_process_data(process_name, process_description)

