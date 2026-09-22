from typing import Any, Dict, List, Set
from collections import deque


class ProcessValidator:
    """
    Deterministic validation engine for business process graphs and models.
    Operates on the actual generated process model and analyst data.
    """

    def validate(self, model: Dict[str, Any], analyst_data: Dict[str, Any]) -> Dict[str, Any]:
        nodes = model.get("nodes", [])
        edges = model.get("edges", [])

        node_map = {n["id"]: n for n in nodes}
        node_ids = set(node_map.keys())

        issues: List[Dict[str, Any]] = []
        warnings: List[str] = []
        checks: List[Dict[str, Any]] = []

        # 1. Start and End node checks
        start_nodes = [
            n for n in nodes
            if n.get("type") in ["start", "event"] and (n.get("data", {}).get("kind") == "start" or n.get("type") == "start")
        ]
        end_nodes = [
            n for n in nodes
            if n.get("type") in ["end", "event"] and (n.get("data", {}).get("kind") == "end" or n.get("type") == "end")
        ]

        if not start_nodes:
            issues.append({
                "id": "err_no_start",
                "severity": "ERROR",
                "message": "Process model is missing an explicit Start event.",
                "node_id": None
            })
            start_check = {"id": "start_end", "label": "Start & End Events", "result": "Fail", "detail": "Missing Start event."}
        elif not end_nodes:
            issues.append({
                "id": "err_no_end",
                "severity": "ERROR",
                "message": "Process model is missing an explicit End event.",
                "node_id": None
            })
            start_check = {"id": "start_end", "label": "Start & End Events", "result": "Fail", "detail": "Missing End event."}
        else:
            start_check = {
                "id": "start_end",
                "label": "Start & End Events",
                "result": "Pass",
                "detail": f"Verified {len(start_nodes)} start event and {len(end_nodes)} end event(s)."
            }
        checks.append(start_check)

        # 2. Graph Connectivity & Edge Validation
        outgoing: Dict[str, List[Dict[str, Any]]] = {nid: [] for nid in node_ids}
        incoming: Dict[str, List[Dict[str, Any]]] = {nid: [] for nid in node_ids}

        broken_edges = []
        for e in edges:
            src = e.get("source")
            tgt = e.get("target")
            if src not in node_ids or tgt not in node_ids:
                broken_edges.append(e)
            else:
                outgoing[src].append(e)
                incoming[tgt].append(e)

        if broken_edges:
            issues.append({
                "id": "err_broken_edges",
                "severity": "ERROR",
                "message": f"Detected {len(broken_edges)} broken edge reference(s) targeting non-existent nodes.",
                "node_id": None
            })

        # Forward reachability from Start
        reachable_from_start: Set[str] = set()
        if start_nodes:
            queue = deque([sn["id"] for sn in start_nodes])
            reachable_from_start.update(queue)
            while queue:
                curr = queue.popleft()
                for edge in outgoing.get(curr, []):
                    nxt = edge["target"]
                    if nxt not in reachable_from_start:
                        reachable_from_start.add(nxt)
                        queue.append(nxt)

        unreachable_nodes = [nid for nid in node_ids if nid not in reachable_from_start]
        if unreachable_nodes:
            issues.append({
                "id": "err_unreachable",
                "severity": "ERROR",
                "message": f"{len(unreachable_nodes)} node(s) are unreachable from the Start event: {', '.join(unreachable_nodes[:3])}.",
                "node_id": unreachable_nodes[0]
            })

        # Dead ends: non-end nodes with 0 outgoing edges
        dead_ends = []
        for n in nodes:
            nid = n["id"]
            is_end = n.get("type") in ["end", "event"] and n.get("data", {}).get("kind") == "end"
            if not is_end and len(outgoing.get(nid, [])) == 0:
                dead_ends.append(nid)

        if dead_ends:
            issues.append({
                "id": "err_dead_end",
                "severity": "ERROR",
                "message": f"Detected {len(dead_ends)} dead-end node(s) with no outbound transition: {', '.join(dead_ends[:3])}.",
                "node_id": dead_ends[0]
            })

        if unreachable_nodes or dead_ends:
            reach_check = {
                "id": "reachability",
                "label": "Reachability & Dead Ends",
                "result": "Fail",
                "detail": f"{len(unreachable_nodes)} unreachable node(s), {len(dead_ends)} dead-end node(s)."
            }
        else:
            reach_check = {
                "id": "reachability",
                "label": "Reachability & Dead Ends",
                "result": "Pass",
                "detail": "All nodes reachable from Start and smoothly progress forward."
            }
        checks.append(reach_check)

        # 3. Gateway Branch Completeness
        gateways = [n for n in nodes if n.get("type") == "gateway"]
        gateway_issues = []
        for gw in gateways:
            gw_id = gw["id"]
            branches = outgoing.get(gw_id, [])
            if len(branches) < 2:
                gateway_issues.append(gw_id)
                issues.append({
                    "id": f"err_gateway_branches_{gw_id}",
                    "severity": "ERROR",
                    "message": f"Gateway '{gw.get('data', {}).get('label', gw_id)}' has fewer than 2 outgoing branch conditions.",
                    "node_id": gw_id
                })

        if gateway_issues:
            gw_check = {
                "id": "gateway_branches",
                "label": "Gateway Completeness",
                "result": "Fail",
                "detail": f"{len(gateway_issues)} gateway(s) lack complete outgoing alternative paths."
            }
        elif gateways:
            gw_check = {
                "id": "gateway_branches",
                "label": "Gateway Completeness",
                "result": "Pass",
                "detail": f"All {len(gateways)} gateway(s) have distinct alternative branches."
            }
        else:
            gw_check = {
                "id": "gateway_branches",
                "label": "Gateway Completeness",
                "result": "Pass",
                "detail": "Purely sequential process; no decision branch defects."
            }
        checks.append(gw_check)

        # 4. Actor Assignment Completeness
        task_nodes = [n for n in nodes if n.get("type") in ["task", "activity"]]
        missing_actors = []
        for t in task_nodes:
            actor = t.get("data", {}).get("actor", "").strip()
            if not actor or actor.lower() in ["unassigned", "none", "null"]:
                missing_actors.append(t["id"])

        if missing_actors:
            warnings.append(f"{len(missing_actors)} activity node(s) have unassigned or default actors.")
            issues.append({
                "id": "warn_unassigned_actors",
                "severity": "WARNING",
                "message": f"{len(missing_actors)} activity node(s) lack a clear responsible actor.",
                "node_id": missing_actors[0]
            })
            actor_check = {
                "id": "actors",
                "label": "Actor Assignment",
                "result": "Review",
                "detail": f"{len(missing_actors)} activities lack an explicit human or system role."
            }
        else:
            actor_check = {
                "id": "actors",
                "label": "Actor Assignment",
                "result": "Pass",
                "detail": "Every activity has an identified actor assignment."
            }
        checks.append(actor_check)

        # 5. Path Coverage (backward reachability to End events)
        can_reach_end: Set[str] = set()
        if end_nodes:
            rev_queue = deque([en["id"] for en in end_nodes])
            can_reach_end.update(rev_queue)
            while rev_queue:
                curr = rev_queue.popleft()
                for edge in incoming.get(curr, []):
                    src = edge["source"]
                    if src not in can_reach_end:
                        can_reach_end.add(src)
                        rev_queue.append(src)

        stranded_from_end = [nid for nid in node_ids if nid not in can_reach_end]
        if stranded_from_end:
            issues.append({
                "id": "err_stranded_nodes",
                "severity": "ERROR",
                "message": f"{len(stranded_from_end)} node(s) cannot reach any terminal End event.",
                "node_id": stranded_from_end[0]
            })
            cov_check = {
                "id": "coverage",
                "label": "Path Coverage",
                "result": "Fail",
                "detail": f"{len(stranded_from_end)} node(s) cannot terminate at an End event."
            }
        else:
            cov_check = {
                "id": "coverage",
                "label": "Path Coverage",
                "result": "Pass",
                "detail": "All execution paths lead to a valid terminating event."
            }
        checks.append(cov_check)

        # 6. Contradictions & Temporal Paradoxes
        analyst_contradictions = analyst_data.get("contradictions", [])
        if analyst_contradictions:
            for ac in analyst_contradictions:
                issues.append({
                    "id": "err_temporal_contradiction",
                    "severity": "ERROR",
                    "message": f"Contradiction detected in process logic: {ac}",
                    "node_id": None
                })
            contra_check = {
                "id": "contradictions",
                "label": "Logical & Temporal Consistency",
                "result": "Fail",
                "detail": f"Identified {len(analyst_contradictions)} logical contradiction(s) in sequence prerequisites."
            }
        else:
            contra_check = {
                "id": "contradictions",
                "label": "Logical & Temporal Consistency",
                "result": "Pass",
                "detail": "No causal or temporal paradoxes found in process dependencies."
            }
        checks.append(contra_check)

        # 7. Overall Soundness check
        error_count = sum(1 for i in issues if i["severity"] == "ERROR")
        warning_count = sum(1 for i in issues if i["severity"] == "WARNING")

        soundness_detail = (
            f"Soundness verified with 0 errors and {warning_count} warning(s)."
            if error_count == 0
            else f"Validation failed with {error_count} critical structural defect(s) and {warning_count} warning(s)."
        )
        checks.insert(0, {
            "id": "soundness",
            "label": "Workflow Soundness",
            "result": "Pass" if error_count == 0 else "Fail",
            "detail": soundness_detail
        })

        # Calculate Validation Score (0 - 100)
        # Base is 100. Each critical error deducts 25. Each warning deducts 8.
        raw_val_score = 100.0 - (error_count * 25.0) - (warning_count * 8.0)
        validation_score = max(0.0, min(100.0, round(raw_val_score, 1)))

        if validation_score >= 80.0 and error_count == 0:
            status = "PASS"
            display_status = "Validated"
        elif validation_score >= 60.0:
            status = "NEEDS_REVIEW"
            display_status = "Needs review"
        else:
            status = "FAIL"
            display_status = "Failed"

        return {
            "status": status,
            "display_status": display_status,
            "validation_score": validation_score,
            "issues": issues,
            "warnings": warnings,
            "checks": checks
        }
