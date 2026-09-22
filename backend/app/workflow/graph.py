from typing import Any, Dict, Literal
from langgraph.graph import StateGraph, START, END

from app.workflow.state import WorkflowState
from app.agents.analyst import AnalystAgent
from app.agents.modeler import ModelerAgent
from app.agents.validator import ValidatorAgent
from app.agents.confidence import ConfidenceAgent
from app.agents.intelligence import IntelligenceAgent


def analyst_step(state: WorkflowState) -> Dict[str, Any]:
    """Execute Analyst Agent."""
    process_name = state.get("process_name", "Untitled Process")
    user_input = state.get("user_input", "")
    analyst = AnalystAgent()
    result = analyst.analyze(process_name=process_name, process_description=user_input)
    attempt = state.get("analysis_attempt", 1)
    return {
        "analyst_result": result,
        "analysis_mode": result.get("provider_name", "Local Fallback"),
        "analysis_attempt": attempt
    }


def modeler_step(state: WorkflowState) -> Dict[str, Any]:
    """Execute Modeler Agent."""
    analyst_result = state.get("analyst_result", {})
    modeler = ModelerAgent()
    model = modeler.generate_model(analyst_data=analyst_result)
    return {"model_result": model}


def validator_step(state: WorkflowState) -> Dict[str, Any]:
    """Execute Validator Agent."""
    model_result = state.get("model_result", {})
    analyst_result = state.get("analyst_result", {})
    validator = ValidatorAgent()
    val_out = validator.validate(model_data=model_result, analyst_data=analyst_result)
    return {"validation_result": val_out}


def confidence_step(state: WorkflowState) -> Dict[str, Any]:
    """Execute Authoritative Confidence Calculation Agent."""
    analyst_result = state.get("analyst_result", {})
    model_result = state.get("model_result", {})
    validation_result = state.get("validation_result", {})
    user_input = state.get("user_input", "")

    conf_agent = ConfidenceAgent()
    conf_out = conf_agent.calculate(
        analyst_data=analyst_result,
        model_data=model_result,
        validation_data=validation_result,
        raw_description=user_input
    )
    return {
        "confidence_result": conf_out,
        "decision": conf_out["decision"]
    }


def decision_router(state: WorkflowState) -> Literal["analyst", "intelligence"]:
    """
    Decision Router:
    Re-analyzes if confidence is severely compromised (< 35%) due to initial parsing failure,
    subject to a strict limit of analysis_attempt < 2.
    Guarantees no infinite loop.
    """
    attempt = state.get("analysis_attempt", 1)
    conf_result = state.get("confidence_result", {})
    overall = conf_result.get("overall_score", 100.0)

    # If critical failure on attempt 1, try one controlled re-analysis pass
    if attempt < 2 and overall < 35.0:
        return "analyst"
    return "intelligence"


def intelligence_step(state: WorkflowState) -> Dict[str, Any]:
    """Execute Intelligence Agent."""
    analyst_result = state.get("analyst_result", {})
    model_result = state.get("model_result", {})
    validation_result = state.get("validation_result", {})

    intel_agent = IntelligenceAgent()
    intel_out = intel_agent.generate_intelligence(
        analyst_data=analyst_result,
        model_data=model_result,
        validation_data=validation_result
    )
    return {"intelligence_result": intel_out}


def create_process_workflow():
    """Build and compile the LangGraph StateGraph workflow matching architectural specification."""
    builder = StateGraph(WorkflowState)

    builder.add_node("analyst", analyst_step)
    builder.add_node("modeler", modeler_step)
    builder.add_node("validator", validator_step)
    builder.add_node("intelligence", intelligence_step)
    builder.add_node("confidence", confidence_step)

    # Pipeline: User -> Analyst -> Modeler -> Validator -> Intelligence -> Confidence -> Result
    builder.add_edge(START, "analyst")
    builder.add_edge("analyst", "modeler")
    builder.add_edge("modeler", "validator")
    builder.add_edge("validator", "intelligence")
    builder.add_edge("intelligence", "confidence")
    builder.add_edge("confidence", END)

    return builder.compile()


# Pre-compiled workflow graph instance
process_graph_workflow = create_process_workflow()
