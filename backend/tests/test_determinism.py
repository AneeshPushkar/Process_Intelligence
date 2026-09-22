from app.workflow.graph import process_graph_workflow

PROCESS_SAMPLE = (
    "Warehouse receives shipments. System checks manifests. If discrepancies exist, Supervisor files report. "
    "Inventory records updated. Process finishes."
)


def test_confidence_determinism_identical_runs():
    """Verify running the pipeline multiple times on the same input yields identical numerical scores."""
    res1 = process_graph_workflow.invoke({
        "process_name": "Warehouse Intake",
        "user_input": PROCESS_SAMPLE,
        "analysis_attempt": 1
    })

    res2 = process_graph_workflow.invoke({
        "process_name": "Warehouse Intake",
        "user_input": PROCESS_SAMPLE,
        "analysis_attempt": 1
    })

    conf1 = res1["confidence_result"]
    conf2 = res2["confidence_result"]

    assert conf1["analyst_score"] == conf2["analyst_score"]
    assert conf1["model_completeness_score"] == conf2["model_completeness_score"]
    assert conf1["validation_score"] == conf2["validation_score"]
    assert conf1["sequence_consistency_score"] == conf2["sequence_consistency_score"]
    assert conf1["gateway_consistency_score"] == conf2["gateway_consistency_score"]
    assert conf1["overall_score"] == conf2["overall_score"]
    assert conf1["decision"] == conf2["decision"]
