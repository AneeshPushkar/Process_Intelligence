from app.agents.confidence import ConfidenceAgent


def test_confidence_formula_exact_computation():
    agent = ConfidenceAgent()

    analyst_data = {
        "analyst_confidence": 90.0,
        "actors": ["HR", "IT", "Manager"],
        "activities": [{"id": "a1", "name": "Task 1", "actor": "HR"}],
        "decisions": [],
        "ambiguities": [],
        "contradictions": []
    }
    model_data = {
        "nodes": [
            {"id": "node_start", "type": "event", "data": {"label": "Start", "kind": "start"}},
            {"id": "a1", "type": "task", "data": {"label": "Task 1", "actor": "HR"}},
            {"id": "node_end", "type": "event", "data": {"label": "End", "kind": "end"}}
        ],
        "edges": [
            {"id": "e1", "source": "node_start", "target": "a1"},
            {"id": "e2", "source": "a1", "target": "node_end"}
        ]
    }
    validation_data = {
        "status": "PASS",
        "validation_score": 100.0,
        "issues": []
    }

    res = agent.calculate(analyst_data, model_data, validation_data, raw_description="Sequential process.")

    # Check component scores range
    for key in [
        "analyst_score", "model_completeness_score", "validation_score",
        "sequence_consistency_score", "gateway_consistency_score"
    ]:
        assert 0.0 <= res[key] <= 100.0

    # Check mathematical formula
    expected_overall = round(
        0.25 * res["analyst_score"]
        + 0.20 * res["model_completeness_score"]
        + 0.25 * res["validation_score"]
        + 0.15 * res["sequence_consistency_score"]
        + 0.15 * res["gateway_consistency_score"],
        1
    )
    assert abs(res["overall_score"] - expected_overall) < 0.15

    # Check decision
    if res["overall_score"] >= 85.0:
        assert res["decision"] == "HIGH"
    elif res["overall_score"] >= 60.0:
        assert res["decision"] == "REVIEW"
    else:
        assert res["decision"] == "LOW"


def test_gateway_non_applicable_policy():
    agent = ConfidenceAgent()

    # Linear workflow with NO conditional keywords
    analyst_linear = {"decisions": [], "actors": ["User"], "activities": []}
    model_linear = {"nodes": [], "edges": []}
    res_linear = agent._compute_gateway_consistency(
        analyst_linear, model_linear, raw_description="User logs in. User views page.", reasons=[]
    )
    assert res_linear == 100.0  # Full consistency for clean linear flow

    # Linear workflow with conditional keywords in text but missing gateway nodes
    res_unmodeled = agent._compute_gateway_consistency(
        analyst_linear, model_linear, raw_description="If user logs in, system shows page.", reasons=[]
    )
    assert res_unmodeled == 45.0  # Penalized for omitting gateway
