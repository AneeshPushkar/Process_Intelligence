from typing import Any, Dict
from app.validation.process_validator import ProcessValidator


class ValidatorAgent:
    """
    Validator Agent: Executes structural, reachability, gateway branch completeness,
    dead-end, and logical contradiction verification on the modeled workflow.
    """

    def __init__(self):
        self.validator = ProcessValidator()

    def validate(self, model_data: Dict[str, Any], analyst_data: Dict[str, Any]) -> Dict[str, Any]:
        return self.validator.validate(model=model_data, analyst_data=analyst_data)
