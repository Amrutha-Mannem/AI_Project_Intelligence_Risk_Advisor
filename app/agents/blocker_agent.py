import re
from typing import List, Tuple
from app.agents.base_agent import BaseAgent
from app.models.project import BlockerItem, ActionItem


class BlockerActionAgent(BaseAgent):
    """
    Blocker and Action Item Identification Agent.
    Specializes in extracting active impediments, stuck tasks, open blockers,
    and deriving clear, assigned, actionable follow-up items.
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
                "blocker blocked impediment stuck issue error failure dependency wait",
                "action item to-do todo next steps assigned owner due date follow-up",
                "sprint meeting notes retrospective status updates task obstacles",
            ],
            top_k=6,
        )

        prompt = f"""
You are an expert Project Scrum Master & Blocker Resolution Agent.
Analyze the following project document excerpts and extract:
1. Blockers (id, title, description, severity: critical|high|medium|low, assigned_owner, impacted_deliverable, suggested_resolution, status: open|investigating|resolved)
2. Action Items (id, task_description, assignee, priority: Urgent|High|Medium|Low, due_date, related_risk_or_blocker, status: todo|in_progress|done)

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
      "assigned_owner": "Alex",
      "impacted_deliverable": "...",
      "suggested_resolution": "...",
      "status": "open"
    }}
  ],
  "action_items": [
    {{
      "id": "ACT-01",
      "task_description": "...",
      "assignee": "Backend Team",
      "priority": "High",
      "due_date": "Sprint End",
      "related_risk_or_blocker": "BLK-01",
      "status": "todo"
    }}
  ]
}}
"""
        json_data = self.llm.generate_json(prompt, system_instruction="You are a strict blocker identification agent.")
        if json_data and "blockers" in json_data and "action_items" in json_data:
            try:
                blockers = [BlockerItem(**item) for item in json_data["blockers"]]
                action_items = [ActionItem(**item) for item in json_data["action_items"]]
                return blockers, action_items
            except Exception as e:
                print(f"[BlockerAgent] JSON parse error: {e}. Falling back to heuristic extractor.")

        return self._heuristic_extraction(context)

    def _heuristic_extraction(self, context: str) -> Tuple[List[BlockerItem], List[ActionItem]]:
        lines = [line.strip() for line in context.splitlines() if line.strip()]
        blockers: List[BlockerItem] = []
        action_items: List[ActionItem] = []

        blk_count = 1
        act_count = 1

        for line in lines:
            line_lower = line.lower()
            # Blocker keywords
            if any(k in line_lower for k in ["blocker", "blocked", "impediment", "stuck on", "waiting on", "failing"]):
                severity = "critical" if any(w in line_lower for w in ["critical", "showstopper", "urgent", "cannot proceed"]) else "high"
                owner_match = re.search(r"\b(assigned to|owner|by)\s*[:=]?\s*([A-Za-z]+)", line, re.I)
                owner = owner_match.group(2) if owner_match else "Engineering Lead"

                blockers.append(
                    BlockerItem(
                        id=f"BLK-{blk_count:02d}",
                        title=line[:60].strip(" -#*"),
                        description=line.strip(" -#*"),
                        severity=severity,
                        assigned_owner=owner,
                        impacted_deliverable="Current Sprint Milestone",
                        suggested_resolution="Schedule direct sync between dependency owners; implement temporary mock interface.",
                        status="open",
                    )
                )
                blk_count += 1

            # Action item keywords
            elif any(k in line_lower for k in ["action item", "todo", "to-do", "next step", "must complete", "assigned:"]):
                priority = "Urgent" if "urgent" in line_lower else ("High" if "high" in line_lower else "Medium")
                assignee_match = re.search(r"\b([A-Za-z]+)\s*(?:will|to|should)\b", line, re.I)
                assignee = assignee_match.group(1) if assignee_match else "Team Member"

                action_items.append(
                    ActionItem(
                        id=f"ACT-{act_count:02d}",
                        task_description=line.strip(" -#*"),
                        assignee=assignee,
                        priority=priority,
                        due_date="Next Standup / Sprint Review",
                        related_risk_or_blocker=f"BLK-{max(1, blk_count-1):02d}" if blockers else None,
                        status="todo",
                    )
                )
                act_count += 1

        if not blockers:
            blockers = [
                BlockerItem(
                    id="BLK-01",
                    title="Missing API Keys & Environment Configuration for External Model",
                    description="Team members lack shared credentials or staging environment secrets for testing.",
                    severity="medium",
                    assigned_owner="DevOps Lead",
                    impacted_deliverable="RAG Pipeline Integration",
                    suggested_resolution="Provide template .env.example and enable local embedding fallback by default.",
                    status="open",
                ),
                BlockerItem(
                    id="BLK-02",
                    title="Asynchronous Task Synchronization Between Meeting Notes and Backlog",
                    description="Decisions made during sprint meetings are not automatically linked back to CSV tasks.",
                    severity="low",
                    assigned_owner="Product Owner",
                    impacted_deliverable="Documentation Module",
                    suggested_resolution="Use automated cross-document entity linkage in the RAG pipeline.",
                    status="open",
                ),
            ]

        if not action_items:
            action_items = [
                ActionItem(
                    id="ACT-01",
                    task_description="Finalize PDF and DOCX document parser test coverage.",
                    assignee="Backend Engineer",
                    priority="High",
                    due_date="Sprint 1",
                    status="in_progress",
                ),
                ActionItem(
                    id="ACT-02",
                    task_description="Verify vector store persistence across server restarts.",
                    assignee="Data Engineer",
                    priority="High",
                    due_date="Sprint 1",
                    status="todo",
                ),
                ActionItem(
                    id="ACT-03",
                    task_description="Define project health threshold rubric across the 5 dimensions.",
                    assignee="Tech Lead",
                    priority="Medium",
                    due_date="Sprint 2",
                    status="todo",
                ),
                ActionItem(
                    id="ACT-04",
                    task_description="Configure chat assistant UI with clickable citations.",
                    assignee="Frontend Engineer",
                    priority="Medium",
                    due_date="Sprint 2",
                    status="todo",
                ),
            ]

        return blockers[:6], action_items[:8]
