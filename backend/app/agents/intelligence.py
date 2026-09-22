import re
from typing import Any, Dict, List


class IntelligenceAgent:
    """
    Intelligence Agent: Generates structured process intelligence (Bottlenecks, Risks,
    Redundancies, Automation Opportunities, Recommendations) dynamically derived from
    the modeled process, extracted entities, and validation findings.
    """

    def generate_intelligence(
        self,
        analyst_data: Dict[str, Any],
        model_data: Dict[str, Any],
        validation_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        activities = analyst_data.get("activities", [])
        decisions = analyst_data.get("decisions", [])
        actors = analyst_data.get("actors", [])
        issues = validation_data.get("issues", [])
        ambiguities = analyst_data.get("ambiguities", [])
        contradictions = analyst_data.get("contradictions", [])

        bottlenecks: List[Dict[str, Any]] = []
        risks: List[Dict[str, Any]] = []
        redundant_steps: List[Dict[str, Any]] = []
        automation: List[Dict[str, Any]] = []
        recommendations: List[Dict[str, Any]] = []

        # 1. Bottlenecks Analysis
        # Single actor handling multiple consecutive activities
        consecutive_same_actor = []
        for i in range(len(activities) - 1):
            if activities[i].get("actor") and activities[i]["actor"] == activities[i + 1].get("actor"):
                consecutive_same_actor.append((activities[i], activities[i + 1]))

        if consecutive_same_actor:
            first_pair = consecutive_same_actor[0]
            actor_name = first_pair[0]["actor"]
            bottlenecks.append({
                "id": "btnk_1",
                "title": f"Single-role throughput bottleneck on '{actor_name}'",
                "description": (
                    f"{actor_name} is sequentially responsible for multiple successive tasks "
                    f"('{first_pair[0]['name']}' followed by '{first_pair[1]['name']}'). "
                    f"This creates operational queue delays when task volumes surge."
                ),
                "severity": "Medium",
                "priority": "P2",
                "impact": "Medium",
                "recommendation": f"Evaluate workload delegation or parallel sub-tasking for {actor_name}.",
                "related_node_ids": [first_pair[0]["id"], first_pair[1]["id"]]
            })

        # Verification / Approval bottleneck
        for act in activities:
            name_lower = act["name"].lower()
            if any(k in name_lower for k in ["verify", "check", "approve", "review", "inspect"]):
                bottlenecks.append({
                    "id": f"btnk_{act['id']}",
                    "title": f"Manual gatekeeper latency in '{act['name']}'",
                    "description": (
                        f"The activity '{act['name']}' requires manual inspection by {act.get('actor', 'the operator')}, "
                        f"which poses a cycle-time constraint on downstream execution."
                    ),
                    "severity": "High" if len(activities) > 4 else "Medium",
                    "priority": "P1",
                    "impact": "High",
                    "recommendation": "Implement automated pre-validation rules or straight-through processing thresholds.",
                    "related_node_ids": [act["id"]]
                })
                break

        if not bottlenecks and activities:
            bottlenecks.append({
                "id": "btnk_default",
                "title": "Linear execution serialization",
                "description": "All activities are structured strictly sequentially without concurrent work streams.",
                "severity": "Low",
                "priority": "P3",
                "impact": "Low",
                "recommendation": "Identify independent tasks that can be triggered asynchronously.",
                "related_node_ids": [activities[0]["id"]]
            })

        # 2. Risks Analysis
        # Validation issues as risks
        for idx, issue in enumerate(issues):
            risks.append({
                "id": f"risk_val_{idx+1}",
                "title": f"Structural risk: {issue.get('message', 'Validation concern')[:60]}",
                "description": issue.get("message", "Validation defect detected in workflow topology."),
                "severity": "High" if issue.get("severity") == "ERROR" else "Medium",
                "priority": "P1" if issue.get("severity") == "ERROR" else "P2",
                "impact": "High" if issue.get("severity") == "ERROR" else "Medium",
                "recommendation": "Correct the process definition to address this structural defect.",
                "related_node_ids": [issue.get("node_id")] if issue.get("node_id") else []
            })

        # Ambiguity / Contradiction risks
        for idx, amb in enumerate(ambiguities):
            risks.append({
                "id": f"risk_amb_{idx+1}",
                "title": f"Operational ambiguity: {amb[:50]}...",
                "description": amb,
                "severity": "High" if "contradiction" in amb.lower() else "Medium",
                "priority": "P1" if "contradiction" in amb.lower() else "P2",
                "impact": "High" if "contradiction" in amb.lower() else "Medium",
                "recommendation": "Clarify explicit business rules and prerequisite ordering in the process description.",
                "related_node_ids": []
            })

        # Unhandled decision branch risk
        if decisions and len(decisions) > 1:
            risks.append({
                "id": "risk_branching",
                "title": "Cascading conditional decision branching",
                "description": f"Workflow contains {len(decisions)} decision points. Edge failure cases risk unmonitored drop-off.",
                "severity": "Medium",
                "priority": "P2",
                "impact": "Medium",
                "recommendation": "Ensure dedicated escalation paths and SLA monitoring on all alternative branches.",
                "related_node_ids": [d["id"] for d in decisions]
            })

        if not risks and activities:
            risks.append({
                "id": "risk_nominal",
                "title": "Lack of automated exception fallback",
                "description": "The process lacks an explicit recovery mechanism if an intermediate activity fails.",
                "severity": "Low",
                "priority": "P3",
                "impact": "Low",
                "recommendation": "Define explicit timeout and exception recovery paths.",
                "related_node_ids": [activities[-1]["id"]]
            })

        # 3. Redundant Steps
        handoffs = []
        for i in range(len(activities) - 1):
            a1 = activities[i]
            a2 = activities[i + 1]
            if a1.get("actor") != a2.get("actor"):
                handoffs.append((a1, a2))

        if len(handoffs) >= 3:
            redundant_steps.append({
                "id": "red_handoffs",
                "title": "Excessive cross-role handoffs",
                "description": (
                    f"Detected {len(handoffs)} role-to-role transitions across {len(actors)} actors. "
                    f"Frequent context switching increases communication overhead and potential error rates."
                ),
                "severity": "Medium",
                "priority": "P2",
                "impact": "Medium",
                "recommendation": "Consolidate related verification and preparation tasks into unified actor swimlanes.",
                "related_node_ids": [h[0]["id"] for h in handoffs[:2]]
            })

        for act in activities:
            name_lower = act["name"].lower()
            if any(k in name_lower for k in ["notify", "email", "send message", "inform", "report"]):
                redundant_steps.append({
                    "id": f"red_{act['id']}",
                    "title": f"Manual communication step in '{act['name']}'",
                    "description": f"Manual dispatch of communications by {act.get('actor')} can be automated via webhooks or event triggers.",
                    "severity": "Low",
                    "priority": "P3",
                    "impact": "Low",
                    "recommendation": "Replace manual notification with event-driven system automated notifications.",
                    "related_node_ids": [act["id"]]
                })
                break

        # 4. Automation Opportunities
        for act in activities:
            name_lower = act["name"].lower()
            if any(k in name_lower for k in ["create", "setup", "generate", "record", "account", "check", "verify", "schedule"]):
                automation.append({
                    "id": f"auto_{act['id']}",
                    "title": f"Automate '{act['name']}' via API integration",
                    "description": (
                        f"The activity '{act['name']}' involves structured rule-based data operations "
                        f"well-suited for RPA or direct REST API automation."
                    ),
                    "severity": "High",
                    "priority": "P1",
                    "impact": "High",
                    "recommendation": f"Integrate an automated backend workflow service to execute '{act['name']}' instantaneously.",
                    "related_node_ids": [act["id"]]
                })
                if len(automation) >= 2:
                    break

        if not automation and activities:
            automation.append({
                "id": "auto_default",
                "title": f"Event-driven trigger for '{activities[0]['name']}'",
                "description": "Automate initiation of this process via webhook integration.",
                "severity": "Medium",
                "priority": "P2",
                "impact": "Medium",
                "recommendation": "Connect upstream data sources to automatically spawn process instances.",
                "related_node_ids": [activities[0]["id"]]
            })

        # 5. Recommendations
        recommendations.append({
            "id": "rec_1",
            "title": "Establish explicit Service Level Agreements (SLAs) per stage",
            "description": "Define maximum allowable dwell time for each actor before automatic notification/escalation triggers.",
            "severity": "Medium",
            "priority": "P2",
            "impact": "High",
            "recommendation": "Deploy real-time process monitoring with alert thresholds.",
            "related_node_ids": [a["id"] for a in activities[:3]]
        })

        if automation:
            recommendations.append({
                "id": "rec_2",
                "title": f"Prioritize automation of {automation[0]['title']}",
                "description": "Early automation of data verification or provisioning offers the highest ROI and cycle-time compression.",
                "severity": "High",
                "priority": "P1",
                "impact": "High",
                "recommendation": "Adopt API-first integration for high-frequency operational steps.",
                "related_node_ids": automation[0]["related_node_ids"]
            })

        # Calculate efficiency estimates (stage duration in hours)
        efficiency_metrics = []
        for i, act in enumerate(activities[:5]):
            # Deterministic duration heuristic based on verb type
            name_lower = act["name"].lower()
            if any(k in name_lower for k in ["ship", "orientation", "onboard", "conduct"]):
                hours = 12.0 + (i * 2.0)
            elif any(k in name_lower for k in ["verify", "review", "approve"]):
                hours = 4.0 + (i * 1.5)
            elif any(k in name_lower for k in ["create", "setup", "assign"]):
                hours = 2.0 + (i * 0.5)
            else:
                hours = 1.0 + (i * 0.4)
            efficiency_metrics.append({
                "stage": act["name"][:22].strip(),
                "hours": round(hours, 1)
            })

        # Issue distribution summary
        issue_distribution = [
            {"name": "Bottlenecks", "value": len(bottlenecks), "fill": "#fbbf24"},
            {"name": "Risks", "value": len(risks), "fill": "#f87171"},
            {"name": "Redundant", "value": len(redundant_steps), "fill": "#a1a1aa"},
            {"name": "Automation", "value": len(automation), "fill": "#14b8a6"},
        ]

        return {
            "bottlenecks": bottlenecks,
            "risks": risks,
            "redundant_steps": redundant_steps,
            "automation_opportunities": automation,
            "recommendations": recommendations,
            "efficiency_metrics": efficiency_metrics,
            "issue_distribution": issue_distribution
        }
