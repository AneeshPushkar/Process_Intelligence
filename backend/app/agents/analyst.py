from typing import Any, Dict
from app.services.llm.factory import get_llm_provider


class AnalystAgent:
    """
    Analyst Agent: Interprets natural language process descriptions into
    structured entities: actors, activities, decisions, dependencies,
    start/end events, assumptions, ambiguities, and contradictions.
    """

    def __init__(self):
        self.provider = get_llm_provider()

    def analyze(self, process_name: str, process_description: str) -> Dict[str, Any]:
        result = self.provider.extract_process_data(process_name, process_description)
        result["provider_name"] = self.provider.provider_name
        return result
