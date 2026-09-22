import pytest
from app.workflow.graph import process_graph_workflow

PROCESS_A = (
    "HR receives the selected candidate's information. HR verifies the candidate's documents. "
    "If documents are incomplete, HR requests the missing documents. Once documents are complete, "
    "HR creates the employee record. IT creates the employee's email account and system access. "
    "The manager assigns the employee's initial responsibilities. HR schedules the orientation session. "
    "The employee completes onboarding orientation. The onboarding process is completed."
)

PROCESS_B = (
    "Hire a new employee. HR verifies documents, IT creates the account, and the manager assigns responsibilities. "
    "Then the employee completes onboarding."
)

PROCESS_C = (
    "Hire employee and give access. HR and IT do the necessary things and finish onboarding."
)

PROCESS_D = (
    "HR completes onboarding before receiving the candidate information. The employee account is created before documents are verified. "
    "If documents are incomplete, the process ends successfully without requesting the missing documents."
)


def _run_pipeline(name: str, desc: str):
    res = process_graph_workflow.invoke({
        "process_name": name,
        "user_input": desc,
        "analysis_attempt": 1
    })
    conf = res["confidence_result"]
    val = res["validation_result"]
    return {
        "analyst": conf["analyst_score"],
        "model": conf["model_completeness_score"],
        "validation": conf["validation_score"],
        "sequence": conf["sequence_consistency_score"],
        "gateway": conf["gateway_consistency_score"],
        "overall": conf["overall_score"],
        "decision": conf["decision"],
        "validation_status": val["status"],
        "explanation": conf["explanation"],
        "reasons": conf.get("reasons", []),
        "issues": val.get("issues", [])
    }


def test_confidence_matrix_case_a():
    """Detailed process: high detail, actors, decisions, clean outcomes."""
    res = _run_pipeline("Case A - Detailed Process", PROCESS_A)
    print("\n--- MATRIX CASE A ---", res)
    assert res["overall"] >= 80.0
    assert res["decision"] in ["HIGH", "REVIEW"]
    assert res["validation_status"] == "PASS"
    assert "authoritative confidence" in res["explanation"].lower()


def test_confidence_matrix_case_b():
    """Moderate process: fewer activities, linear."""
    res = _run_pipeline("Case B - Moderate Process", PROCESS_B)
    print("\n--- MATRIX CASE B ---", res)
    assert 60.0 <= res["overall"] <= 100.0
    assert res["decision"] in ["HIGH", "REVIEW"]
    assert "explanation" in res


def test_confidence_matrix_case_c():
    """Vague process: 'do the necessary things', ambiguous directives."""
    res = _run_pipeline("Case C - Vague Process", PROCESS_C)
    print("\n--- MATRIX CASE C ---", res)
    # Vague process has lower analyst confidence due to vague phrase detection
    assert res["analyst"] < 80.0
    assert "explanation" in res


def test_confidence_matrix_case_d():
    """Contradictory process: temporal inversions and contradictory endings."""
    res = _run_pipeline("Case D - Contradictory Process", PROCESS_D)
    print("\n--- MATRIX CASE D ---", res)
    # Contradictions are detected by the validator and analyst
    assert res["validation"] < 100.0
    assert res["validation_status"] in ["NEEDS_REVIEW", "FAIL"]
    has_contradiction = (
        any("contradiction" in r.lower() for r in res["reasons"]) or
        any("contradiction" in i.get("message", "").lower() for i in res["issues"])
    )
    assert has_contradiction
