from typing import Any, Dict, List, Optional
from typing_extensions import TypedDict


class WorkflowState(TypedDict, total=False):
    user_input: str
    process_name: str
    analysis_attempt: int
    analysis_mode: str

    analyst_result: Dict[str, Any]
    model_result: Dict[str, Any]
    validation_result: Dict[str, Any]
    confidence_result: Dict[str, Any]
    decision: str
    intelligence_result: Dict[str, Any]

    errors: List[str]
