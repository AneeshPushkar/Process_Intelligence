from typing import Any, Dict, List


class ModelerAgent:
    """
    Modeler Agent: Constructs a dynamic React Flow graph from Analyst output.
    Generates clean topological layout with start/end events, sequential activities,
    and branched decision gateways (YES/NO) without malformed nodes or duplicate gateways.
    """

    def generate_model(self, analyst_data: Dict[str, Any]) -> Dict[str, Any]:
        activities = analyst_data.get("activities", [])
        decisions = analyst_data.get("decisions", [])
        actors = analyst_data.get("actors", ["System"])

        nodes: List[Dict[str, Any]] = []
        edges: List[Dict[str, Any]] = []
        edge_idx = 1

        # 1. Start Node
        start_id = "node_start"
        start_label = analyst_data.get("start_event", {}).get("name", "Process Start")
        nodes.append({
            "id": start_id,
            "type": "event",
            "data": {
                "label": start_label,
                "kind": "start",
                "actor": actors[0] if actors else "System",
                "description": "Trigger initiating the business process"
            },
            "position": {"x": 300, "y": 30}
        })

        # Separate activities into pre-gateway sequential, branch 'yes', and branch 'no'
        pre_gateway_activities: List[Dict[str, Any]] = []
        yes_activities: List[Dict[str, Any]] = []
        no_activities: List[Dict[str, Any]] = []

        # Check if decisions define branch mapping
        branch_map: Dict[str, str] = {}
        for d in decisions:
            for b in d.get("branches", []):
                label_lower = b.get("label", "").lower()
                branch_type = "yes" if "yes" in label_lower or "true" in label_lower or "pos" in label_lower else "no"
                for aid in b.get("activity_ids", []):
                    branch_map[aid] = branch_type

        for act in activities:
            aid = act.get("id")
            branch = act.get("branch") or branch_map.get(aid)
            if branch == "yes":
                yes_activities.append(act)
            elif branch == "no":
                no_activities.append(act)
            elif act.get("is_conditional") and decisions:
                # If marked conditional but not explicitly tagged, place in YES or NO based on position
                if not yes_activities:
                    yes_activities.append(act)
                else:
                    no_activities.append(act)
            else:
                pre_gateway_activities.append(act)

        curr_y = 140
        prev_node_id = start_id

        # 2. Render Sequential Pre-Gateway Activities
        for act in pre_gateway_activities:
            act_id = act["id"]
            nodes.append({
                "id": act_id,
                "type": "task",
                "data": {
                    "label": act.get("name", "Activity"),
                    "actor": act.get("actor", "System"),
                    "description": act.get("description", "")
                },
                "position": {"x": 300, "y": curr_y}
            })
            edges.append({
                "id": f"e_{edge_idx}",
                "source": prev_node_id,
                "target": act_id
            })
            edge_idx += 1
            prev_node_id = act_id
            curr_y += 110

        # 3. If Decisions exist or branching activities exist, create Gateway and Branches
        if decisions or yes_activities or no_activities:
            gw_id = decisions[0]["id"] if decisions else "gw_1"
            gw_label = decisions[0].get("condition", "Approved?") if decisions else "Condition Met?"

            nodes.append({
                "id": gw_id,
                "type": "gateway",
                "data": {
                    "label": gw_label,
                    "actor": actors[0] if actors else "System",
                    "description": f"Decision gateway: {gw_label}"
                },
                "position": {"x": 300, "y": curr_y}
            })
            edges.append({
                "id": f"e_{edge_idx}",
                "source": prev_node_id,
                "target": gw_id
            })
            edge_idx += 1
            gw_y = curr_y

            # 4. YES / Positive Branch (Layout left at x: 160)
            yes_y = gw_y + 120
            yes_prev_id = gw_id
            if yes_activities:
                for i, act in enumerate(yes_activities):
                    act_id = act["id"]
                    nodes.append({
                        "id": act_id,
                        "type": "task",
                        "data": {
                            "label": act.get("name", "Activity"),
                            "actor": act.get("actor", "System"),
                            "description": act.get("description", "")
                        },
                        "position": {"x": 160, "y": yes_y}
                    })
                    edge_data = {
                        "id": f"e_{edge_idx}",
                        "source": yes_prev_id,
                        "target": act_id
                    }
                    if i == 0:
                        edge_data["label"] = "Yes"
                        edge_data["condition"] = "True"
                    edges.append(edge_data)
                    edge_idx += 1
                    yes_prev_id = act_id
                    yes_y += 110

                # Terminal End for YES Branch
                end_yes_id = "node_end_yes"
                end_yes_label = f"End: {yes_activities[-1]['name']}"
                nodes.append({
                    "id": end_yes_id,
                    "type": "event",
                    "data": {
                        "label": end_yes_label,
                        "kind": "end",
                        "actor": yes_activities[-1].get("actor", "System"),
                        "description": "Terminal completion outcome"
                    },
                    "position": {"x": 160, "y": yes_y}
                })
                edges.append({
                    "id": f"e_{edge_idx}",
                    "source": yes_prev_id,
                    "target": end_yes_id
                })
                edge_idx += 1
            else:
                # Direct end for YES branch
                end_yes_id = "node_end_yes"
                nodes.append({
                    "id": end_yes_id,
                    "type": "event",
                    "data": {
                        "label": "Process Completed (Yes)",
                        "kind": "end",
                        "actor": actors[0] if actors else "System",
                        "description": "Terminal outcome"
                    },
                    "position": {"x": 160, "y": yes_y}
                })
                edges.append({
                    "id": f"e_{edge_idx}",
                    "source": gw_id,
                    "target": end_yes_id,
                    "label": "Yes",
                    "condition": "True"
                })
                edge_idx += 1

            # 5. NO / Negative Branch (Layout right at x: 460)
            no_y = gw_y + 120
            no_prev_id = gw_id
            if no_activities:
                for i, act in enumerate(no_activities):
                    act_id = act["id"]
                    nodes.append({
                        "id": act_id,
                        "type": "task",
                        "data": {
                            "label": act.get("name", "Activity"),
                            "actor": act.get("actor", "System"),
                            "description": act.get("description", "")
                        },
                        "position": {"x": 460, "y": no_y}
                    })
                    edge_data = {
                        "id": f"e_{edge_idx}",
                        "source": no_prev_id,
                        "target": act_id
                    }
                    if i == 0:
                        edge_data["label"] = "No"
                        edge_data["condition"] = "False"
                    edges.append(edge_data)
                    edge_idx += 1
                    no_prev_id = act_id
                    no_y += 110

                # Terminal End for NO Branch
                end_no_id = "node_end_no"
                end_no_label = f"End: {no_activities[-1]['name']}"
                nodes.append({
                    "id": end_no_id,
                    "type": "event",
                    "data": {
                        "label": end_no_label,
                        "kind": "end",
                        "actor": no_activities[-1].get("actor", "System"),
                        "description": "Alternative terminal outcome"
                    },
                    "position": {"x": 460, "y": no_y}
                })
                edges.append({
                    "id": f"e_{edge_idx}",
                    "source": no_prev_id,
                    "target": end_no_id
                })
                edge_idx += 1
            else:
                # Direct end for NO branch
                end_no_id = "node_end_no"
                nodes.append({
                    "id": end_no_id,
                    "type": "event",
                    "data": {
                        "label": "Process Terminated (No)",
                        "kind": "end",
                        "actor": actors[-1] if actors else "System",
                        "description": "Alternative terminal outcome"
                    },
                    "position": {"x": 460, "y": no_y}
                })
                edges.append({
                    "id": f"e_{edge_idx}",
                    "source": gw_id,
                    "target": end_no_id,
                    "label": "No",
                    "condition": "False"
                })
                edge_idx += 1

        else:
            # Purely linear workflow: Single terminal End node
            end_id = "node_end"
            end_label = analyst_data.get("end_event", {}).get("name", "Process Completed")
            nodes.append({
                "id": end_id,
                "type": "event",
                "data": {
                    "label": end_label,
                    "kind": "end",
                    "actor": actors[-1] if actors else "System",
                    "description": "Normal terminal state for the business process"
                },
                "position": {"x": 300, "y": curr_y}
            })
            edges.append({
                "id": f"e_{edge_idx}",
                "source": prev_node_id,
                "target": end_id
            })

        statistics = {
            "total_nodes": len(nodes),
            "activities": len([n for n in nodes if n["type"] == "task"]),
            "gateways": len([n for n in nodes if n["type"] == "gateway"]),
            "events": len([n for n in nodes if n["type"] == "event"]),
            "edges": len(edges)
        }

        return {
            "nodes": nodes,
            "edges": edges,
            "statistics": statistics
        }

