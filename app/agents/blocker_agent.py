import re
from typing import List, Tuple
from app.agents.base_agent import BaseAgent
from app.models.project import BlockerItem, ActionItem


class BlockerActionAgent(BaseAgent):
    """
    Blocker and Action Item Identification Agent.
    Specializes in extracting active impediments, stuck tasks, open blockers,
    pending decisions, and deriving clear, assigned, actionable follow-up items
    strictly grounded in uploaded meeting notes and progress reports.
    """

    def __init__(self, vector_store, retriever, llm):
        super().__init__(
            name="BlockerActionAgent",
            role="Blocker & Action Item Identification Specialist",
            vector_store=vector_store,
            retriever=retriever,
            llm=llm,
        )

    def run(self) -> Tuple[List[BlockerItem], List[ActionItem]]:
        context = self.get_relevant_context(
            [
                "blocker blocked impediment stuck issue error failure dependency wait delay",
                "action item to-do todo next steps assigned owner due date follow-up decision",
                "sprint meeting notes retrospective status updates task obstacles pending",
            ],
            top_k=6,
        )

        prompt = f"""
You are an expert Project Scrum Master & Blocker Resolution Agent.
Analyze the following project document excerpts and extract:
1. Blockers: id, title, description, severity (critical|high|medium|low), assigned_owner, impacted_deliverable, suggested_resolution, status (open|investigating|resolved), source_reference (name of file from '--- Source: <filename> ---')
2. Action Items: id, task_description, assignee, priority (Urgent|High|Medium|Low), due_date, related_risk_or_blocker, status (todo|in_progress|done), source_reference

Document Context:
{context}

Respond in strictly valid JSON:
{{
  "blockers": [
    {{
      "id": "BLK-01",
      "title": "...",
      "description": "...",
      "severity": "critical",
      "assigned_owner": "...",
      "impacted_deliverable": "...",
      "suggested_resolution": "...",
      "status": "open",
      "source_reference": "..."
    }}
  ],
  "action_items": [
    {{
      "id": "ACT-01",
      "task_description": "...",
      "assignee": "...",
      "priority": "High",
      "due_date": "...",
      "related_risk_or_blocker": "BLK-01",
      "status": "todo",
      "source_reference": "..."
    }}
  ]
}}
"""
        json_data = self.llm.generate_json(prompt, system_instruction="You are a strict blocker and action item identification agent. Only extract items present in the document text.")
        if json_data and "blockers" in json_data and "action_items" in json_data:
            try:
                default_doc = self.vector_store.chunks[0].source_name if self.vector_store.chunks else "Uploaded Document"
                blockers = []
                for b in json_data["blockers"]:
                    if not b.get("source_reference"): b["source_reference"] = default_doc
                    blockers.append(BlockerItem(**b))

                actions = []
                for a in json_data["action_items"]:
                    if not a.get("source_reference"): a["source_reference"] = default_doc
                    actions.append(ActionItem(**a))

                return blockers, actions
            except Exception as e:
                print(f"[BlockerAgent] JSON parse error: {e}. Falling back to dynamic heuristic extractor.")

        return self._heuristic_extraction(context)

    def _heuristic_extraction(self, context: str) -> Tuple[List[BlockerItem], List[ActionItem]]:
        lines = [line.strip() for line in context.splitlines() if line.strip()]
        doc_names = list(dict.fromkeys(c.source_name for c in self.vector_store.chunks))
        primary_doc = doc_names[0] if doc_names else "Uploaded Document"

        blockers: List[BlockerItem] = []
        action_items: List[ActionItem] = []

        current_source = primary_doc
        blk_count = 1
        act_count = 1

        for line in lines:
            # Track current source document if header line
            src_match = re.search(r"--- Source:\s*([^\s(]+)", line)
            if src_match:
                current_source = src_match.group(1)
                continue

            line_lower = line.lower()
            clean_line = re.sub(r"^[-*#\d\.\s]+", "", line).strip()
            if len(clean_line) < 8:
                continue

            # 1. Blocker / Impediment keywords
            if any(k in line_lower for k in ["blocker", "blocked", "impediment", "stuck on", "waiting on", "failing", "pending decision", "unresolved"]):
                severity = "critical" if any(w in line_lower for w in ["critical", "showstopper", "urgent", "cannot proceed", "major"]) else "high"
                owner_match = re.search(r"\b(assigned to|owner|by|assignee)\s*[:=]?\s*([A-Za-z]+)", line, re.I)
                owner = owner_match.group(2) if owner_match else "Team Lead"

                blockers.append(
                    BlockerItem(
                        id=f"BLK-{blk_count:02d}",
                        title=clean_line[:65],
                        description=clean_line,
                        severity=severity,
                        assigned_owner=owner,
                        impacted_deliverable="Current Sprint Milestone",
                        suggested_resolution="Schedule immediate alignment sync with dependency stakeholders.",
                        status="open",
                        source_reference=current_source,
                    )
                )
                blk_count += 1

            # 2. Action Item keywords
            elif any(k in line_lower for k in ["action item", "todo", "to-do", "next step", "must complete", "assigned:", "responsible:"]):
                priority = "Urgent" if "urgent" in line_lower else ("High" if "high" in line_lower else "Medium")
                assignee_match = re.search(r"\b([A-Za-z]+)\s*(?:will|to|should|assignee)\b", line, re.I)
                assignee = assignee_match.group(1) if assignee_match else "Assigned Engineer"

                action_items.append(
                    ActionItem(
                        id=f"ACT-{act_count:02d}",
                        task_description=clean_line,
                        assignee=assignee,
                        priority=priority,
                        due_date="Next Standup / Sprint Review",
                        related_risk_or_blocker=f"BLK-{max(1, blk_count-1):02d}" if blockers else None,
                        status="todo",
                        source_reference=current_source,
                    )
                )
                act_count += 1

        # Fallback: scan for any unresolved issues in the text
        if not blockers and lines:
            for line in lines:
                line_l = line.lower()
                clean = re.sub(r"^[-*#\d\.\s]+", "", line).strip()
                if any(w in line_l for w in ["delay", "pending", "concern", "problem", "gap", "issue", "obstacle"]):
                    if len(clean) > 20 and not clean.startswith("--- Source:"):
                        blockers.append(
                            BlockerItem(
                                id=f"BLK-{len(blockers)+1:02d}",
                                title=clean[:65],
                                description=clean,
                                severity="medium",
                                assigned_owner="Project Team",
                                impacted_deliverable="Deliverable Milestones",
                                suggested_resolution="Assess impact in standup and assign remediation owner.",
                                status="open",
                                source_reference=primary_doc,
                            )
                        )
                        if len(blockers) >= 3:
                            break

        # Fallback: scan for follow-up actions in the text
        if not action_items and lines:
            for line in lines:
                clean = re.sub(r"^[-*#\d\.\s]+", "", line).strip()
                if any(w in line.lower() for w in ["ensure", "complete", "implement", "verify", "review", "test", "deliver"]):
                    if len(clean) > 20 and not clean.startswith("--- Source:"):
                        action_items.append(
                            ActionItem(
                                id=f"ACT-{len(action_items)+1:02d}",
                                task_description=clean,
                                assignee="Team Member",
                                priority="High" if len(action_items) == 0 else "Medium",
                                due_date="Sprint Milestone",
                                status="todo",
                                source_reference=primary_doc,
                            )
                        )
                        if len(action_items) >= 4:
                            break

        return blockers[:6], action_items[:8]
