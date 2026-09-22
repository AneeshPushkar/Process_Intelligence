import re
from typing import Any, Dict, List, Optional
from app.services.llm.base import BaseLLMProvider


class LocalFallbackProvider(BaseLLMProvider):
    """
    Deterministic rule-based NLP local fallback provider.
    Works for arbitrary business processes without any external API dependencies.
    Accurately extracts actors, activities, decision gateways, branches, and dependencies.
    """

    ROLES = [
        "HR", "IT", "Manager", "Employee", "Customer", "Client", "User", "Operator",
        "System", "Warehouse", "Finance", "Auditor", "Vendor", "Supervisor", "Admin",
        "Developer", "Specialist", "Bank", "Support Team", "Support", "Doctor", "Lab",
        "Nurse", "Patient", "Clerk", "Courier", "Billing", "Sales", "Reviewer"
    ]

    def __init__(self, model_name: str = "local-heuristic-v1", temperature: float = 0.0, api_key: Optional[str] = None):
        super().__init__(model_name=model_name, temperature=temperature, api_key=api_key)

    @property
    def provider_name(self) -> str:
        return "Local Fallback"

    def generate(self, prompt: str, system_prompt: str = "") -> str:
        """Deterministic completion for generic prompts."""
        return "Deterministic local response generated."

    def extract_process_data(self, process_name: str, process_description: str) -> Dict[str, Any]:
        """
        Dynamically extracts structured entities from arbitrary process text.
        Handles sequential steps and conditional branches without creating malformed fragments.
        """
        text = process_description.strip()
        raw_sentences = self._split_sentences(text)

        actors: List[str] = []
        activities: List[Dict[str, Any]] = []
        decisions: List[Dict[str, Any]] = []
        dependencies: List[Dict[str, Any]] = []
        assumptions: List[str] = []
        ambiguities: List[str] = []
        contradictions: List[str] = []

        vague_phrases = [
    "do the necessary things",
    "necessary things",
    "appropriate actions",
    "stuff",
    "etc",
    "and so on",
    "as needed",
    "whatever is required",
    "may",
    "might",
    "sometimes",
    "possibly",
    "could",
    "if necessary",
    "at any time",
    "or continue",
    "or it may",
]
        for vp in vague_phrases:
            if vp in text.lower():
                ambiguities.append(f"Vague directive detected: '{vp}'. Specific activities and responsibilities are not defined.")

        contradiction_patterns = [
            (r"completes?\s+(?:.*)\s+before\s+receiving", "Process attempts completion before intake of required information."),
            (r"is\s+created\s+before\s+(?:.*)\s+is\s+verified", "Asset/Record created before mandatory verification step is performed."),
            (r"created\s+before\s+documents\s+are\s+verified", "Record created prior to document verification."),
            (r"ends?\s+successfully\s+without", "Process claims successful termination despite incomplete or missing prerequisites.")
        ]
        for pattern, msg in contradiction_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                contradictions.append(msg)
                ambiguities.append(f"Contradiction: {msg}")

        # Separate terminal statements, conditional sentences, and sequential sentences
        sequential_clauses: List[str] = []
        conditional_clauses: List[Dict[str, str]] = []

        for s in raw_sentences:
            s_clean = s.strip()
            if not s_clean:
                continue

            # Check if sentence is an explicit terminal statement
            if re.search(r"\b(process\s+(?:is\s+)?completed|workflow\s+(?:is\s+)?completed|process\s+ends|workflow\s+ends)\b", s_clean, re.IGNORECASE):
                continue

            # Check if sentence starts with conditional keywords
            m_cond = re.match(r"^\s*(?:if|in case|whether)\s+([^,]+),\s*(.+)$", s_clean, re.IGNORECASE)
            if m_cond:
                conditional_clauses.append({
                    "raw": s_clean,
                    "condition": m_cond.group(1).strip(),
                    "consequence": m_cond.group(2).strip()
                })
            else:
                # Check for inline conditional: "...; otherwise, ..."
                if re.search(r"\botherwise\b", s_clean, re.IGNORECASE):
                    parts = re.split(r"\botherwise,?\s*", s_clean, flags=re.IGNORECASE)
                    if len(parts) == 2:
                        conditional_clauses.append({
                            "raw": s_clean,
                            "condition": "Default condition met",
                            "consequence": parts[0].strip()
                        })
                        conditional_clauses.append({
                            "raw": s_clean,
                            "condition": "Otherwise",
                            "consequence": parts[1].strip()
                        })
                        continue
                sequential_clauses.append(s_clean)

        act_counter = 1
        prev_act_id = None

        # 1. Parse Sequential Sentences (Pre-Gateway)
        for s in sequential_clauses:
            actor = self._detect_actor(s)
            if actor and actor not in actors:
                actors.append(actor)

            # Check if sentence has multiple actions joined by 'and' or 'then'
            sub_actions = self._split_compound_actions(s)
            for sub_act in sub_actions:
                sub_actor = self._detect_actor(sub_act) or actor or "System"
                if sub_actor not in actors:
                    actors.append(sub_actor)

                act_id = f"act_{act_counter}"
                act_counter += 1
                name = self._clean_verb_name(sub_act, sub_actor)

                activities.append({
                    "id": act_id,
                    "name": name,
                    "actor": sub_actor,
                    "description": sub_act,
                    "is_conditional": False,
                    "branch": None
                })

                if prev_act_id:
                    dependencies.append({
                        "from": prev_act_id,
                        "to": act_id,
                        "type": "sequential"
                    })
                prev_act_id = act_id

        # 2. Parse Conditional Sentences (Gateways and Branches)
        if conditional_clauses:
            gw_id = "gw_1"
            source_act_id = activities[-1]["id"] if activities else "node_start"

            pos_clause = conditional_clauses[0]
            cond_label = self._format_condition_label(pos_clause["condition"])

            # Extract actions for YES/Positive branch
            pos_actions = self._split_compound_actions(pos_clause["consequence"])
            pos_act_ids: List[str] = []
            for pa in pos_actions:
                pa_actor = self._detect_actor(pa) or self._detect_actor(pos_clause["consequence"]) or (actors[0] if actors else "System")
                if pa_actor not in actors:
                    actors.append(pa_actor)

                pa_id = f"act_{act_counter}"
                act_counter += 1
                pa_name = self._clean_verb_name(pa, pa_actor)

                activities.append({
                    "id": pa_id,
                    "name": pa_name,
                    "actor": pa_actor,
                    "description": pa,
                    "is_conditional": True,
                    "branch": "yes",
                    "gateway_id": gw_id
                })
                pos_act_ids.append(pa_id)

            # Connect sequence inside YES branch
            for i in range(len(pos_act_ids) - 1):
                dependencies.append({
                    "from": pos_act_ids[i],
                    "to": pos_act_ids[i + 1],
                    "type": "sequential"
                })

            # Extract actions for NO/Negative branch
            neg_act_ids: List[str] = []
            if len(conditional_clauses) > 1:
                neg_clause = conditional_clauses[1]
                neg_actions = self._split_compound_actions(neg_clause["consequence"])
                for na in neg_actions:
                    na_actor = self._detect_actor(na) or self._detect_actor(neg_clause["consequence"]) or (actors[0] if actors else "System")
                    if na_actor not in actors:
                        actors.append(na_actor)

                    na_id = f"act_{act_counter}"
                    act_counter += 1
                    na_name = self._clean_verb_name(na, na_actor)

                    activities.append({
                        "id": na_id,
                        "name": na_name,
                        "actor": na_actor,
                        "description": na,
                        "is_conditional": True,
                        "branch": "no",
                        "gateway_id": gw_id
                    })
                    neg_act_ids.append(na_id)

                for i in range(len(neg_act_ids) - 1):
                    dependencies.append({
                        "from": neg_act_ids[i],
                        "to": neg_act_ids[i + 1],
                        "type": "sequential"
                    })
            else:
                # Synthesize clean alternative outcome branch to guarantee gateway branch completeness
                neg_id = f"act_{act_counter}"
                act_counter += 1
                fallback_actor = actors[-1] if actors else "System"
                activities.append({
                    "id": neg_id,
                    "name": "Process exception / Rejection",
                    "actor": fallback_actor,
                    "description": "Handle alternative exception pathway",
                    "is_conditional": True,
                    "branch": "no",
                    "gateway_id": gw_id
                })
                neg_act_ids.append(neg_id)

            decisions.append({
                "id": gw_id,
                "condition": cond_label,
                "source_activity": source_act_id,
                "sentence": f"{pos_clause['raw']} {conditional_clauses[1]['raw'] if len(conditional_clauses) > 1 else ''}".strip(),
                "branches": [
                    {"label": "Yes", "condition": "Positive", "activity_ids": pos_act_ids},
                    {"label": "No", "condition": "Negative", "activity_ids": neg_act_ids}
                ]
            })

            # Add gateway dependencies
            if pos_act_ids:
                dependencies.append({
                    "from": source_act_id,
                    "to": pos_act_ids[0],
                    "type": "conditional",
                    "condition": "Yes"
                })
            if neg_act_ids:
                dependencies.append({
                    "from": source_act_id,
                    "to": neg_act_ids[0],
                    "type": "conditional",
                    "condition": "No"
                })

        if not actors:
            actors = ["System"]
            assumptions.append("No explicit actors detected; default system actor assigned.")

        # Start and End events
        start_label = f"Start: {activities[0]['name']}" if activities else "Process Started"
        if decisions and len(decisions[0].get("branches", [])) >= 2:
            end_label = "Process Completed"
        elif activities:
            end_label = f"End: {activities[-1]['name']}"
        else:
            end_label = "Process Completed"

        start_event = {
            "id": "node_start",
            "name": start_label,
            "trigger": "Initial workflow trigger"
        }
        end_event = {
            "id": "node_end",
            "name": end_label,
            "outcome": "Completed"
        }

        domain = self._infer_domain(text)
        title = process_name.strip() if process_name.strip() else (activities[0]["name"] if activities else "Business Process Workflow")

        summary = (
            f"The workflow '{title}' encompasses {len(activities)} main activities executed across "
            f"{len(actors)} identified actor(s) ({', '.join(actors)}). "
            f"It features {len(decisions)} decision gateway(s) and terminates with '{end_label}'."
        )

        # Analyst confidence calculation
        score = 85.0
        if len(actors) >= 2:
            score += 5.0
        elif len(actors) == 1 and actors[0] != "System":
            score += 2.0
        else:
            score -= 5.0

        if len(activities) >= 4:
            score += 5.0
        elif len(activities) < 3:
            score -= 10.0

        if decisions:
            score += 5.0

        score -= len(ambiguities) * 10.0
        if contradictions:
            score -= len(contradictions) * 15.0

        analyst_confidence = max(20.0, min(98.0, round(score, 1)))

        return {
            "title": title,
            "summary": summary,
            "domain": domain,
            "actors": actors,
            "activities": activities,
            "decisions": decisions,
            "dependencies": dependencies,
            "start_event": start_event,
            "end_event": end_event,
            "assumptions": assumptions,
            "ambiguities": ambiguities,
            "contradictions": contradictions,
            "analyst_confidence": analyst_confidence,
            "provider_name": self.provider_name
        }

    def _split_sentences(self, text: str) -> List[str]:
        """Split text into distinct sentences while preserving conditional clauses."""
        raw = re.split(r"[\.\n;]+", text)
        result: List[str] = []
        for r in raw:
            r = r.strip()
            if not r:
                continue
            # Do NOT sub-split if sentence starts with conditional 'If'
            if re.match(r"^\s*(?:if|in case|whether)\b", r, re.IGNORECASE):
                result.append(r)
                continue
            # Sub-split on strong sequence conjunctions like 'Then' or 'Subsequently'
            sub = re.split(r"\b(?:then|subsequently|after that|afterward)\b", r, flags=re.IGNORECASE)
            for s in sub:
                s = s.strip()
                if len(s) > 3:
                    result.append(s)
        return result

    def _split_compound_actions(self, clause: str) -> List[str]:
        """Split compound actions joined by 'and' or 'then' when appropriate."""
        # e.g., "payment is processed and the order is shipped" -> ["payment is processed", "the order is shipped"]
        parts = re.split(r"\s+(?:and\s+then|and|then)\s+", clause, flags=re.IGNORECASE)
        clean_parts = [p.strip() for p in parts if len(p.strip()) > 3]
        return clean_parts if clean_parts else [clause.strip()]

    def _detect_actor(self, text: str) -> Optional[str]:
        """Detect responsible actor or subject role for the action."""
        # 1. Exact match on known roles
        for role in self.ROLES:
            pattern = rf"\b{re.escape(role)}\b"
            if re.search(pattern, text, re.IGNORECASE):
                return "Support Team" if role.lower() == "support team" else role

        # 2. Contextual passive hints
        t = text.lower()
        if any(k in t for k in ["payment", "invoice", "reimburse"]):
            return "Finance"
        if any(k in t for k in ["ship", "warehouse", "stock", "pack", "inventory"]):
            return "Warehouse"
        if any(k in t for k in ["email account", "system access", "software", "code", "deploy"]):
            return "IT"
        if any(k in t for k in ["loan", "credit score", "bank"]):
            return "Bank"
        if any(k in t for k in ["specialist", "escalated"]):
            return "Specialist"
        if any(k in t for k in ["customer is notified", "notify customer"]):
            return "System"
        if any(k in t for k in ["candidate", "applicant", "application", "employee record", "onboarding"]):
            return "HR"

        # 3. Syntactic subject match: first non-stopword capitalized word
        words = text.split()
        for w in words[:3]:
            clean_w = re.sub(r"[^\w]", "", w)
            if clean_w.istitle() and clean_w.lower() not in [
                "if", "then", "once", "after", "when", "the", "a", "an", "in", "case", "process", "workflow", "it"
            ]:
                return clean_w

        return None

    def _clean_verb_name(self, phrase: str, actor: Optional[str] = None) -> str:
        """Extract clean, descriptive verb phrase for task label."""
        s = phrase.strip().rstrip(".,;").strip()
        s = re.sub(r"^(if|then|once|after|when|the|a|an)\s+", "", s, flags=re.IGNORECASE).strip()

        # Passive patterns: 'X is <verb>ed [to/by Y]'
        m_passive = re.match(
            r"^(?:the\s+)?(payment|order|account|loan|customer|documents?|application|issue|results?|employee\s+account|records?)\s+(?:is|are|was|were)\s+(\w+ed|\w+en|\w+t)(?:\s+(?:to|by|for)\s+([^,]+))?",
            s,
            re.IGNORECASE
        )
        if m_passive:
            noun = m_passive.group(1)
            verb = m_passive.group(2)
            rest = m_passive.group(3) or ""
            verb_map = {
                "processed": "Process", "shipped": "Ship", "notified": "Notify",
                "created": "Create", "verified": "Verify", "approved": "Approve",
                "rejected": "Reject", "resolved": "Resolve", "escalated": "Escalate",
                "discharged": "Discharge", "issued": "Issue", "checked": "Check",
                "completed": "Complete", "reviewed": "Review", "sent": "Send",
                "updated": "Update", "requested": "Request"
            }
            v = verb_map.get(verb.lower(), verb.capitalize())
            if rest:
                return f"{v} {noun} to {rest.strip()}"
            return f"{v} {noun}"

        # Escalated pattern
        if re.search(r"\bescalated\s+to\s+(?:a\s+)?(\w+)", s, re.IGNORECASE):
            m = re.search(r"\bescalated\s+to\s+(?:a\s+)?(\w+)", s, re.IGNORECASE)
            target = m.group(1).capitalize()
            return f"Escalate to {target}"

        # Resolves it pattern
        if re.search(r"\bresolves?\s+it\b", s, re.IGNORECASE):
            return "Resolve issue"

        # Onboarding begins pattern
        if re.search(r"\bonboarding\s+begins?\b", s, re.IGNORECASE):
            return "Begin onboarding"

        # Strip actor prefix if repeated in phrase: "HR requests the missing documents" -> "Request missing documents"
        if actor:
            s = re.sub(rf"^(?:the\s+)?{re.escape(actor)}\s+", "", s, flags=re.IGNORECASE).strip()

        # Convert 3rd person singular verb to imperative/base form
        words = s.split()
        if words:
            first = words[0].lower()
            third_person_map = {
                "requests": "Request", "verifies": "Verify", "checks": "Check",
                "reviews": "Review", "receives": "Receive", "places": "Place",
                "submits": "Submit", "creates": "Create", "sends": "Send",
                "approves": "Approve", "rejects": "Reject", "discharges": "Discharge",
                "delivers": "Deliver", "packs": "Pack", "examines": "Examine",
                "conducts": "Conduct", "files": "File", "resolves": "Resolve",
                "assigns": "Assign", "schedules": "Schedule", "completes": "Complete"
            }
            v = third_person_map.get(first, words[0].capitalize())
            rest = " ".join(words[1:5])
            action_phrase = f"{v} {rest}".strip()

            # Include subject actor prefix if it adds natural enterprise clarity
            if actor and actor != "System" and not action_phrase.lower().startswith(actor.lower()):
                # e.g., "HR receives new employee application", "Customer places an order"
                return f"{actor} {action_phrase[0].lower() + action_phrase[1:]}"
            return action_phrase

        return s.capitalize()

    def _format_condition_label(self, cond_str: str) -> str:
        """Format clean decision condition label, e.g. 'Product available?'."""
        s = cond_str.strip().rstrip(".,;?")
        s = re.sub(r"^(if|in case|whether|that|it is|it)\s+", "", s, flags=re.IGNORECASE).strip()
        s = re.sub(r"^(the|a|an)\s+", "", s, flags=re.IGNORECASE).strip()

        # Standardize common condition phrases
        norm_map = {
            "product is available": "Product available?",
            "product available": "Product available?",
            "documents are valid": "Documents valid?",
            "documents valid": "Documents valid?",
            "application is approved": "Application approved?",
            "application approved": "Application approved?",
            "issue is simple": "Issue simple?",
            "issue simple": "Issue simple?",
            "in stock": "In stock?",
            "results are normal": "Results normal?",
            "results normal": "Results normal?"
        }
        low = s.lower()
        if low in norm_map:
            return norm_map[low]

        label = s.capitalize()
        if not label.endswith("?"):
            label += "?"
        return label

    def _infer_domain(self, text: str) -> str:
        """Infer business domain from semantic keywords."""
        t = text.lower()
        if any(k in t for k in ["employee", "hire", "candidate", "onboard", "orientation", "resume", "hr"]):
            return "Human Resources"
        if any(k in t for k in ["order", "product", "ship", "warehouse", "inventory", "stock", "cart"]):
            return "Commerce & Logistics"
        if any(k in t for k in ["payment", "invoice", "credit", "loan", "bank", "financial", "audit"]):
            return "Finance & Banking"
        if any(k in t for k in ["ticket", "support", "customer service", "complaint", "incident"]):
            return "Customer Support"
        if any(k in t for k in ["code", "deploy", "server", "software", "api", "database", "it"]):
            return "Information Technology"
        return "Operations"

