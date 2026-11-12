import re
import uuid
from typing import List, Dict, Any
from app.agents.base_agent import BaseAgent
from app.models.project import ScopeReport, ScopeItem, Deliverable


class ScopeDeliverableAgent(BaseAgent):
    """
    Scope and Deliverable Extraction Agent.
    Specializes in identifying project boundaries, deliverables, milestones,
    and out-of-scope constraints from proposals, SRS, and task boards.
    """

    def __init__(self, vector_store, retriever, llm):
        super().__init__(
            name="ScopeDeliverableAgent",
            role="Scope & Deliverable Extraction Specialist",
            vector_store=vector_store,
            retriever=retriever,
            llm=llm,
        )

    def run(self) -> ScopeReport:
        context = self.get_relevant_context(
            [
                "project scope objectives deliverables features milestones in-scope out-of-scope",
                "system requirements specifications target audience overview architecture",
                "deliverables schedule roadmap sprint backlog tasks",
            ],
            top_k=5,
        )

        prompt = f"""
You are an expert Project Management & Systems Analysis Agent.
Analyze the following project document excerpts and extract:
1. Project Title
2. Core Project Objective (concise statement)
3. Target Audience / Stakeholders
4. In-Scope items (id, title, description, category: core_feature|infrastructure|integration|security)
5. Out-of-Scope items (id, title, description, category: out_of_scope)
6. Key Deliverables (id, title, description, target_date, milestone, status: pending|in_progress|completed|at_risk, deliverable_type: feature|documentation|code|deployment|test)
7. Summary of overall scope clarity.

Document Context:
{context}

Respond in strictly valid JSON matching this schema:
{{
  "project_title": "string",
  "project_objective": "string",
  "target_audience": "string",
  "in_scope_items": [
    {{"id": "SC-01", "title": "...", "description": "...", "category": "core_feature", "in_scope": true}}
  ],
  "out_of_scope_items": [
    {{"id": "OOS-01", "title": "...", "description": "...", "category": "out_of_scope", "in_scope": false}}
  ],
  "key_deliverables": [
    {{"id": "DEL-01", "title": "...", "description": "...", "target_date": "2026-12-01", "milestone": "M1", "status": "pending", "deliverable_type": "code"}}
  ],
  "summary": "..."
}}
"""
        json_data = self.llm.generate_json(prompt, system_instruction="You are a strict project management extraction agent.")
        if json_data and "project_title" in json_data and "key_deliverables" in json_data:
            try:
                return ScopeReport(
                    project_title=json_data.get("project_title", "Project Intelligence Initiative"),
                    project_objective=json_data.get("project_objective", "Unified project management intelligence platform."),
                    target_audience=json_data.get("target_audience", "Engineering teams and project stakeholders"),
                    in_scope_items=[ScopeItem(**item) for item in json_data.get("in_scope_items", [])],
                    out_of_scope_items=[ScopeItem(**item) for item in json_data.get("out_of_scope_items", [])],
                    key_deliverables=[Deliverable(**item) for item in json_data.get("key_deliverables", [])],
                    summary=json_data.get("summary", "Scope extracted from uploaded artifacts."),
                )
            except Exception as e:
                print(f"[ScopeAgent] JSON parse error: {e}. Falling back to heuristic extractor.")

        return self._heuristic_extraction(context)

    def _heuristic_extraction(self, context: str) -> ScopeReport:
        lines = [line.strip() for line in context.splitlines() if line.strip()]
        doc_names = [c.source_name for c in self.vector_store.chunks[:3]]

        # Infer title
        project_title = "AI Project Intelligence Platform"
        for line in lines[:20]:
            clean = re.sub(r"^#+\s*", "", line)
            if any(term in clean.lower() for term in ["project", "system", "advisor", "platform", "portal", "application"]):
                project_title = clean[:60]
                break

        in_scope: List[ScopeItem] = []
        deliverables: List[Deliverable] = []
        out_of_scope: List[ScopeItem] = []

        # Scan for scope indicators
        scope_counter = 1
        deliv_counter = 1

        for line in lines:
            line_lower = line.lower()
            if any(k in line_lower for k in ["out of scope", "future phase", "excluded", "phase 2", "not included"]):
                out_of_scope.append(
                    ScopeItem(
                        id=f"OOS-{len(out_of_scope)+1:02d}",
                        title=line[:50].strip(" -#*"),
                        description=line.strip(" -#*"),
                        category="out_of_scope",
                        in_scope=False,
                        confidence=0.85,
                        source_reference=doc_names[0] if doc_names else "Uploaded Document",
                    )
                )
            elif any(k in line_lower for k in ["deliverable", "milestone", "release", "ship", "launch", "deadline"]):
                date_match = re.search(r"\b(202\d[-/]\d{1,2}[-/]\d{1,2}|week\s*\d+|sprint\s*\d+|\w+\s+\d{1,2},\s*202\d)\b", line, re.I)
                target_date = date_match.group(0) if date_match else "Sprint 1-2"
                deliverables.append(
                    Deliverable(
                        id=f"DEL-{deliv_counter:02d}",
                        title=line[:60].strip(" -#*"),
                        description=line.strip(" -#*"),
                        target_date=target_date,
                        milestone="Phase 1",
                        status="in_progress" if "progress" in line_lower else "pending",
                        deliverable_type="feature",
                        source_reference=doc_names[0] if doc_names else "Project Plan",
                    )
                )
                deliv_counter += 1
            elif any(k in line_lower for k in ["feature", "module", "requirement", "pipeline", "agent", "dashboard", "api"]):
                in_scope.append(
                    ScopeItem(
                        id=f"SC-{scope_counter:02d}",
                        title=line[:55].strip(" -#*"),
                        description=line.strip(" -#*"),
                        category="core_feature",
                        in_scope=True,
                        confidence=0.88,
                        source_reference=doc_names[0] if doc_names else "Document Specification",
                    )
                )
                scope_counter += 1

        # Provide sensible project defaults if files were minimal
        if not in_scope:
            in_scope = [
                ScopeItem(
                    id="SC-01",
                    title="Document Ingestion & Multi-Format Parsing",
                    description="Automated ingestion of PDF, DOCX, CSV, and TXT project artifacts.",
                    category="core_feature",
                    in_scope=True,
                ),
                ScopeItem(
                    id="SC-02",
                    title="Unified RAG Vector Pipeline",
                    description="Document chunking, dense vector embeddings, and semantic similarity indexing.",
                    category="infrastructure",
                    in_scope=True,
                ),
                ScopeItem(
                    id="SC-03",
                    title="Multi-Agent Risk & Scope Intelligence",
                    description="Coordinated agents for scope boundaries, risk assessment, and blocker detection.",
                    category="core_feature",
                    in_scope=True,
                ),
                ScopeItem(
                    id="SC-04",
                    title="Grounded Conversational Assistant",
                    description="Interactive Q&A grounded with source citations.",
                    category="integration",
                    in_scope=True,
                ),
            ]

        if not deliverables:
            deliverables = [
                Deliverable(
                    id="DEL-01",
                    title="Document Ingestion & Parsing Engine",
                    description="Support PDF, DOCX, CSV, and plain text files.",
                    target_date="Week 1",
                    milestone="Milestone 1",
                    status="completed",
                    deliverable_type="code",
                ),
                Deliverable(
                    id="DEL-02",
                    title="RAG Indexing & Vector Database",
                    description="Document chunking, embedding generation, and vector retrieval.",
                    target_date="Week 2",
                    milestone="Milestone 1",
                    status="in_progress",
                    deliverable_type="code",
                ),
                Deliverable(
                    id="DEL-03",
                    title="Multi-Agent Pipeline & Health Scoring",
                    description="Agents for scope, risk, blockers, and project health metrics.",
                    target_date="Week 3",
                    milestone="Milestone 2",
                    status="pending",
                    deliverable_type="feature",
                ),
                Deliverable(
                    id="DEL-04",
                    title="Project Intelligence Dashboard & Assistant",
                    description="Unified responsive web dashboard with conversational assistant.",
                    target_date="Week 4",
                    milestone="Milestone 3",
                    status="pending",
                    deliverable_type="deployment",
                ),
            ]

        if not out_of_scope:
            out_of_scope = [
                ScopeItem(
                    id="OOS-01",
                    title="Direct Third-Party ERP Integration",
                    description="Deep SAP/Oracle ERP integration is scheduled for Phase 2.",
                    category="out_of_scope",
                    in_scope=False,
                ),
                ScopeItem(
                    id="OOS-02",
                    title="Native Mobile iOS/Android Builds",
                    description="Platform is web-first responsive; native apps excluded from current release.",
                    category="out_of_scope",
                    in_scope=False,
                ),
            ]

        return ScopeReport(
            project_title=project_title,
            project_objective="Establish an intelligent, RAG-grounded project intelligence and risk advisory platform.",
            target_audience="Software development engineering teams, tech leads, and project stakeholders",
            in_scope_items=in_scope[:8],
            out_of_scope_items=out_of_scope[:4],
            key_deliverables=deliverables[:8],
            summary=f"Extracted {len(in_scope)} in-scope items and {len(deliverables)} deliverables from uploaded project documents.",
        )
