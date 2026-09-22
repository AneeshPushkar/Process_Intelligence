import re
from typing import Any, Dict, List


class ConfidenceAgent:
    """
    Authoritative Confidence Calculation Engine.
    Implements the exact project-defined formula:
    overall = (0.25 * analyst) + (0.20 * model_completeness) + (0.25 * validation) +
              (0.15 * sequence_consistency) + (0.15 * gateway_consistency)

    Fully deterministic with an explainable documented policy.
    """

    def calculate(
        self,
        analyst_data: Dict[str, Any],
        model_data: Dict[str, Any],
        validation_data: Dict[str, Any],
        raw_description: str = ""
    ) -> Dict[str, Any]:
        reasons: List[str] = []

        # 1. Analyst Score (0 - 100)
        analyst_score = self._compute_analyst_score(analyst_data, reasons)

        # 2. Model Completeness Score (0 - 100)
        model_score = self._compute_model_completeness(analyst_data, model_data, reasons)

        # 3. Validation Score (0 - 100)
        val_score = float(validation_data.get("validation_score", 100.0))
        if val_score < 80.0:
            reasons.append(f"Validation engine deducted score due to {len(validation_data.get('issues', []))} issue(s).")

        # 4. Sequence Consistency Score (0 - 100)
        seq_score = self._compute_sequence_consistency(model_data, validation_data, reasons)

        # 5. Gateway Consistency Score (0 - 100)
        gw_score = self._compute_gateway_consistency(analyst_data, model_data, raw_description, reasons)

        # Exact weighted formula
        overall = (
            0.25 * analyst_score
            + 0.20 * model_score
            + 0.25 * val_score
            + 0.15 * seq_score
            + 0.15 * gw_score
        )
        overall_score = round(overall, 1)

        # Threshold Decision
        if overall_score >= 85.0:
            decision = "HIGH"
        elif overall_score >= 60.0:
            decision = "REVIEW"
        else:
            decision = "LOW"

        explanation = self._build_explanation(
            overall_score, decision, analyst_score, model_score, val_score, seq_score, gw_score
        )

        return {
            "analyst_score": round(analyst_score, 1),
            "model_completeness_score": round(model_score, 1),
            "validation_score": round(val_score, 1),
            "sequence_consistency_score": round(seq_score, 1),
            "gateway_consistency_score": round(gw_score, 1),
            "overall_score": overall_score,
            "decision": decision,
            "explanation": explanation,
            "reasons": reasons
        }

    def _compute_analyst_score(self, analyst_data: Dict[str, Any], reasons: List[str]) -> float:
        """Evaluates clarity of extracted actors, activities, decisions, and ambiguities."""
        score = float(analyst_data.get("analyst_confidence", 80.0))
        ambiguities = analyst_data.get("ambiguities", [])
        contradictions = analyst_data.get("contradictions", [])

        if ambiguities:
            reasons.append(f"Analyst identified {len(ambiguities)} ambiguity/vagueness concern(s).")
        if contradictions:
            reasons.append(f"Analyst flagged {len(contradictions)} logical/temporal contradiction(s).")

        actors = analyst_data.get("actors", [])
        if len(actors) >= 3:
            reasons.append("Multi-stakeholder interaction well-defined across distinct actors.")
        elif len(actors) == 1 and actors[0] == "System":
            reasons.append("Single generic system actor inferred due to lack of role specification.")

        return max(0.0, min(100.0, score))

    def _compute_model_completeness(
        self, analyst_data: Dict[str, Any], model_data: Dict[str, Any], reasons: List[str]
    ) -> float:
        """Evaluates graph structure against extracted requirements."""
        score = 0.0
        nodes = model_data.get("nodes", [])
        edges = model_data.get("edges", [])

        has_start = any(n.get("type") in ["start", "event"] and n.get("data", {}).get("kind") == "start" for n in nodes)
        has_end = any(n.get("type") in ["end", "event"] and n.get("data", {}).get("kind") == "end" for n in nodes)

        if has_start:
            score += 15.0
        else:
            reasons.append("Model is missing an entry Start event.")

        if has_end:
            score += 15.0
        else:
            reasons.append("Model is missing a terminal End event.")

        # Activity coverage
        extracted_activities = analyst_data.get("activities", [])
        task_nodes = [n for n in nodes if n.get("type") in ["task", "activity"]]
        if extracted_activities:
            coverage = min(1.0, len(task_nodes) / len(extracted_activities))
            score += coverage * 30.0
        else:
            score += 15.0

        # Edge connectivity coverage
        if nodes and edges:
            node_ids = {n["id"] for n in nodes}
            connected_nodes = set()
            for e in edges:
                connected_nodes.add(e.get("source"))
                connected_nodes.add(e.get("target"))
            edge_coverage = min(1.0, len(connected_nodes.intersection(node_ids)) / len(node_ids))
            score += edge_coverage * 20.0
        else:
            reasons.append("Graph lacks adequate transitions connecting activities.")

        # Valid edge references
        valid_refs = True
        node_ids = {n["id"] for n in nodes}
        for e in edges:
            if e.get("source") not in node_ids or e.get("target") not in node_ids:
                valid_refs = False
                break
        if valid_refs and edges:
            score += 10.0

        # Actor assignments
        assigned_tasks = [t for t in task_nodes if t.get("data", {}).get("actor") and t.get("data", {}).get("actor") != "Unassigned"]
        if task_nodes:
            actor_ratio = len(assigned_tasks) / len(task_nodes)
            score += actor_ratio * 10.0
        else:
            score += 5.0

        return max(0.0, min(100.0, score))

    def _compute_sequence_consistency(
        self, model_data: Dict[str, Any], validation_data: Dict[str, Any], reasons: List[str]
    ) -> float:
        """Evaluates graph reachability, absence of deadlocks, and transition sanity."""
        score = 100.0
        issues = validation_data.get("issues", [])

        # Deductions based on structural graph flaws
        unreachable = [i for i in issues if i.get("id") == "err_unreachable"]
        if unreachable:
            score -= 30.0
            reasons.append("Sequence consistency reduced: nodes exist that cannot be reached from Start.")

        dead_ends = [i for i in issues if i.get("id") == "err_dead_end"]
        if dead_ends:
            score -= 25.0
            reasons.append("Sequence consistency reduced: dead-end paths found.")

        broken_edges = [i for i in issues if i.get("id") == "err_broken_edges"]
        if broken_edges:
            score -= 30.0

        stranded = [i for i in issues if i.get("id") == "err_stranded_nodes"]
        if stranded:
            score -= 25.0
            reasons.append("Sequence consistency reduced: pathways cannot terminate at End event.")

        # If contradictions were flagged in the process text
        contradictions = [i for i in issues if i.get("id") == "err_temporal_contradiction"]
        if contradictions:
            score -= 25.0
            reasons.append("Sequence consistency reduced: temporal prerequisites are inverted or contradictory.")

        return max(0.0, min(100.0, score))

    def _compute_gateway_consistency(
        self,
        analyst_data: Dict[str, Any],
        model_data: Dict[str, Any],
        raw_description: str,
        reasons: List[str]
    ) -> float:
        """
        Documented Non-Applicable Policy:
        - If the process is intrinsically linear (no conditional logic in text and no decisions extracted),
          there are zero branching defects. It receives a baseline score of 100.0 (Clean Linear Consistency).
        - If conditional keywords ('if', 'whether', 'in case') WERE present in text but no gateway was modeled,
          penalty is applied (score = 45.0).
        - If gateways exist: verified for >=2 outgoing branches and branch conditions.
        """
        nodes = model_data.get("nodes", [])
        edges = model_data.get("edges", [])
        gateways = [n for n in nodes if n.get("type") == "gateway"]
        text = raw_description.lower()
        has_conditional_words = bool(re.search(r"\b(if|whether|in case|otherwise|unless)\b", text))
        analyst_decisions = analyst_data.get("decisions", [])

        if not gateways:
            if not has_conditional_words and not analyst_decisions:
                # Documented Policy: Clean linear flow
                return 100.0
            else:
                reasons.append("Gateway consistency reduced: conditional branching logic mentioned in text but missing gateway nodes.")
                return 45.0

        # Gateways are present; inspect outgoing transitions
        score = 100.0
        for gw in gateways:
            gw_id = gw["id"]
            branches = [e for e in edges if e.get("source") == gw_id]
            if len(branches) < 2:
                score -= 35.0
                reasons.append(f"Gateway '{gw.get('data', {}).get('label', gw_id)}' lacks complete alternative paths (< 2 branches).")
            # Check edge labels/conditions
            unlabeled = [e for e in branches if not e.get("label")]
            if unlabeled:
                score -= 10.0

        return max(0.0, min(100.0, score))

    def _build_explanation(
        self, overall: float, decision: str, analyst: float, model: float, val: float, seq: float, gw: float
    ) -> str:
        return (
            f"Calculated authoritative confidence of {overall}% ({decision}) using the project standard formula "
            f"[0.25*Analyst({analyst}) + 0.20*Model({model}) + 0.25*Validation({val}) + "
            f"0.15*Sequence({seq}) + 0.15*Gateway({gw})]."
        )
