from app.agents.analyst import AnalystAgent
from app.agents.modeler import ModelerAgent
from app.agents.validator import ValidatorAgent
from app.agents.intelligence import IntelligenceAgent


def test_analyst_agent_arbitrary_input():
    analyst = AnalystAgent()
    desc = "Doctor examines patient. Lab conducts blood test. If results are normal, Doctor discharges patient."
    res = analyst.analyze("Clinical Patient Care", desc)

    assert "Doctor" in res["actors"] or "Lab" in res["actors"]
    assert len(res["activities"]) >= 2
    assert len(res["decisions"]) >= 1
    assert "start_event" in res
    assert "end_event" in res
    assert 0 <= res["analyst_confidence"] <= 100


def test_modeler_agent_graph_generation():
    analyst = AnalystAgent()
    desc = "Customer places order. System verifies stock. If in stock, Warehouse packs goods. Courier delivers parcel."
    analyst_res = analyst.analyze("Fulfillment", desc)

    modeler = ModelerAgent()
    model = modeler.generate_model(analyst_res)

    nodes = model["nodes"]
    edges = model["edges"]

    assert len(nodes) >= 4
    assert len(edges) >= 3

    # Verify React Flow node properties
    for n in nodes:
        assert "id" in n
        assert "type" in n
        assert "position" in n
        assert "data" in n
        assert "label" in n["data"]

    # Verify edge connections
    node_ids = {n["id"] for n in nodes}
    for e in edges:
        assert e["source"] in node_ids
        assert e["target"] in node_ids


def test_intelligence_agent_generation():
    analyst = AnalystAgent()
    modeler = ModelerAgent()
    validator = ValidatorAgent()
    intel_agent = IntelligenceAgent()

    desc = "Clerk verifies invoice. Clerk reviews tax id. Manager approves payment. Bank transfers funds."
    a_out = analyst.analyze("Invoice Workflow", desc)
    m_out = modeler.generate_model(a_out)
    v_out = validator.validate(m_out, a_out)

    intel = intel_agent.generate_intelligence(a_out, m_out, v_out)

    assert "bottlenecks" in intel
    assert "risks" in intel
    assert "redundant_steps" in intel
    assert "automation_opportunities" in intel
    assert "recommendations" in intel

    all_insights = intel["bottlenecks"] + intel["risks"] + intel["automation_opportunities"] + intel["recommendations"]
    assert len(all_insights) >= 3

    for item in all_insights:
        assert "id" in item
        assert "title" in item
        assert "description" in item
        assert "severity" in item
        assert "priority" in item
        assert "recommendation" in item
