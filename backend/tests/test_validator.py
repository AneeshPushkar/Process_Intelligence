from app.validation.process_validator import ProcessValidator


def test_validator_detects_missing_start_and_end():
    validator = ProcessValidator()

    # Graph with no start event
    bad_model = {
        "nodes": [
            {"id": "act_1", "type": "task", "data": {"label": "Task 1", "actor": "HR"}},
            {"id": "end_1", "type": "event", "data": {"label": "End", "kind": "end"}}
        ],
        "edges": [{"id": "e1", "source": "act_1", "target": "end_1"}]
    }
    res = validator.validate(bad_model, {})
    assert any(i["id"] == "err_no_start" for i in res["issues"])
    assert res["validation_score"] < 100.0


def test_validator_detects_unreachable_and_dead_ends():
    validator = ProcessValidator()

    bad_model = {
        "nodes": [
            {"id": "start_1", "type": "event", "data": {"label": "Start", "kind": "start"}},
            {"id": "act_1", "type": "task", "data": {"label": "Connected Task", "actor": "HR"}},
            {"id": "act_orphan", "type": "task", "data": {"label": "Orphaned Task", "actor": "IT"}},  # Unreachable
            {"id": "act_dead_end", "type": "task", "data": {"label": "Dead End Task", "actor": "Mgr"}}, # No outgoing edge
            {"id": "end_1", "type": "event", "data": {"label": "End", "kind": "end"}}
        ],
        "edges": [
            {"id": "e1", "source": "start_1", "target": "act_1"},
            {"id": "e2", "source": "act_1", "target": "end_1"},
            {"id": "e3", "source": "start_1", "target": "act_dead_end"}
        ]
    }
    res = validator.validate(bad_model, {})
    assert any(i["id"] == "err_unreachable" for i in res["issues"])
    assert any(i["id"] == "err_dead_end" for i in res["issues"])
    assert res["status"] in ["NEEDS_REVIEW", "FAIL"]


def test_validator_detects_contradictions():
    validator = ProcessValidator()

    model = {
        "nodes": [
            {"id": "start", "type": "event", "data": {"label": "Start", "kind": "start"}},
            {"id": "act_1", "type": "task", "data": {"label": "Complete Onboarding", "actor": "HR"}},
            {"id": "end", "type": "event", "data": {"label": "End", "kind": "end"}}
        ],
        "edges": [
            {"id": "e1", "source": "start", "target": "act_1"},
            {"id": "e2", "source": "act_1", "target": "end"}
        ]
    }
    analyst_data = {
        "contradictions": ["Process attempts completion before intake of required information."]
    }

    res = validator.validate(model, analyst_data)
    assert any(i["id"] == "err_temporal_contradiction" for i in res["issues"])
    assert res["validation_score"] <= 75.0
