import re
import uuid
from typing import List, Dict, Any
from app.agents.base_agent import BaseAgent
from app.models.project import ScopeReport, ScopeItem, Deliverable


class ScopeDeliverableAgent(BaseAgent):
    """
    Scope and Deliverable Extraction Agent.
    Identifies project goals, milestones, timelines, and responsibilities
    strictly from uploaded project documents.
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
                "deliverables schedule roadmap sprint backlog tasks goals timeline",
            ],
            top_k=6,
        )

        prompt = f"""
You are an expert Project Management & Systems Analysis Agent.
Analyze the following project document excerpts and extract:
1. Project Title
2. Primary Project Goals & Core Objective (concise statement grounded strictly in the provided text)
3. Target Audience, Stakeholders & Key Responsibilities
4. In-Scope items: id, title, description, category (core_feature|infrastructure|integration|security), source_reference (name of file from '--- Source: <filename> ---')
5. Out-of-Scope boundaries: id, title, description, category (out_of_scope), source_reference
6. Key Deliverables, Milestones & Timelines: id, title, description, target_date, milestone, status (pending|in_progress|completed|at_risk), deliverable_type (feature|documentation|code|deployment|test), source_reference
7. Summary of overall scope clarity.

Document Context:
{context}

Respond in strictly valid JSON matching this schema:
{{
  "project_title": "string",
  "project_objective": "string",
  "target_audience": "string",
  "in_scope_items": [
    {{"id": "SC-01", "title": "...", "description": "...", "category": "core_feature", "in_scope": true, "source_reference": "..."}}
  ],
  "out_of_scope_items": [
    {{"id": "OOS-01", "title": "...", "description": "...", "category": "out_of_scope", "in_scope": false, "source_reference": "..."}}
  ],
  "key_deliverables": [
    {{"id": "DEL-01", "title": "...", "description": "...", "target_date": "...", "milestone": "...", "status": "pending", "deliverable_type": "feature", "source_reference": "..."}}
  ],
  "summary": "..."
}}
"""
        json_data = self.llm.generate_json(prompt, system_instruction="You are a strict project management extraction agent. Extract facts strictly from the provided text.")
        if json_data and "project_title" in json_data and "key_deliverables" in json_data:
            try:
                default_doc = self.vector_store.chunks[0].source_name if self.vector_store.chunks else "Uploaded Document"
                in_scope = []
                for item in json_data.get("in_scope_items", []):
                    if not item.get("source_reference"): item["source_reference"] = default_doc
                    in_scope.append(ScopeItem(**item))

                out_scope = []
                for item in json_data.get("out_of_scope_items", []):
                    if not item.get("source_reference"): item["source_reference"] = default_doc
                    out_scope.append(ScopeItem(**item))

                deliverables = []
                for item in json_data.get("key_deliverables", []):
                    if not item.get("source_reference"): item["source_reference"] = default_doc
                    deliverables.append(Deliverable(**item))

                return ScopeReport(
                    project_title=json_data.get("project_title", "Project Intelligence Initiative"),
                    project_objective=json_data.get("project_objective", "Core project initiative based on uploaded documents."),
                    target_audience=json_data.get("target_audience", "Engineering teams and project stakeholders"),
                    in_scope_items=in_scope,
                    out_of_scope_items=out_scope,
                    key_deliverables=deliverables,
                    summary=json_data.get("summary", "Scope extracted from uploaded artifacts."),
                )
            except Exception as e:
                print(f"[ScopeAgent] JSON parse error: {e}. Falling back to dynamic heuristic extractor.")

        return self._heuristic_extraction(context)

    def _heuristic_extraction(self, context: str) -> ScopeReport:
        lines = [line.strip() for line in context.splitlines() if line.strip()]
        doc_names = list(dict.fromkeys(c.source_name for c in self.vector_store.chunks))
        primary_doc = doc_names[0] if doc_names else "Uploaded Document"

        # 1. Dynamically Infer Project Title from context
        project_title = ""
        for line in lines[:30]:
            clean = re.sub(r"^#+\s*", "", line).strip()
            if clean.startswith("--- Source:"):
                continue
            if any(term in clean.lower() for term in ["project", "system", "platform", "portal", "application", "initiative", "specification", "overview"]):
                project_title = clean[:70]
                break
        if not project_title:
            project_title = primary_doc.rsplit(".", 1)[0].replace("_", " ").title()

        # 2. Dynamically Infer Core Objective & Goals
        project_objective = ""
        for line in lines:
            line_l = line.lower()
            if any(k in line_l for k in ["objective", "goal", "aim", "purpose", "mission", "vision"]):
                obj_cand = re.sub(r"^[-*#\s]*\w+[:=-]?\s*", "", line).strip()
                if len(obj_cand) > 15:
                    project_objective = obj_cand
                    break
        if not project_objective:
            for line in lines:
                if len(line) > 35 and not line.startswith("--- Source:"):
                    project_objective = line
                    break
        if not project_objective:
            project_objective = f"Project goals and execution deliverables derived directly from {', '.join(doc_names)}."

        # 3. Target Audience / Responsibilities
        target_audience = "Cross-functional engineering team, project managers, and key stakeholders"
        for line in lines:
            if any(k in line.lower() for k in ["target audience", "stakeholder", "roles and responsibilities", "intended for"]):
                target_audience = re.sub(r"^[-*#\s]*\w+[:=-]?\s*", "", line).strip()[:80]
                break

        in_scope: List[ScopeItem] = []
        deliverables: List[Deliverable] = []
        out_of_scope: List[ScopeItem] = []

        current_source = primary_doc

        for line in lines:
            src_match = re.search(r"--- Source:\s*([^\s(]+)", line)
            if src_match:
                current_source = src_match.group(1)
                continue

            line_lower = line.lower()
            clean_line = re.sub(r"^[-*#\d\.\s]+", "", line).strip()
            if len(clean_line) < 8:
                continue

            # Out of scope boundaries
            if any(k in line_lower for k in ["out of scope", "future phase", "excluded", "phase 2", "not included", "non-goal", "out-of-scope"]):
                out_of_scope.append(
                    ScopeItem(
                        id=f"OOS-{len(out_of_scope)+1:02d}",
                        title=clean_line[:60],
                        description=clean_line,
                        category="out_of_scope",
                        in_scope=False,
                        confidence=0.9,
                        source_reference=current_source,
                    )
                )
            # Milestones and Deliverables
            elif any(k in line_lower for k in ["deliverable", "milestone", "release", "ship", "launch", "deadline", "target date"]):
                date_match = re.search(r"\b(202\d[-/]\d{1,2}[-/]\d{1,2}|week\s*\d+|sprint\s*\d+|phase\s*\d+|\w+\s+\d{1,2},\s*202\d)\b", line, re.I)
                target_date = date_match.group(0) if date_match else "Sprint Schedule"
                deliverables.append(
                    Deliverable(
                        id=f"DEL-{len(deliverables)+1:02d}",
                        title=clean_line[:65],
                        description=clean_line,
                        target_date=target_date,
                        milestone="Milestone 1",
                        status="in_progress" if "progress" in line_lower else "pending",
                        deliverable_type="feature" if "feature" in line_lower else "code",
                        source_reference=current_source,
                    )
                )
            # In-Scope Requirements
            elif any(k in line_lower for k in ["feature", "requirement", "module", "system", "pipeline", "service", "capability", "component", "functionality"]):
                in_scope.append(
                    ScopeItem(
                        id=f"SC-{len(in_scope)+1:02d}",
                        title=clean_line[:60],
                        description=clean_line,
                        category="core_feature",
                        in_scope=True,
                        confidence=0.88,
                        source_reference=current_source,
                    )
                )

        # If sparse lines, extract substantive requirements dynamically from lines
        if not in_scope and lines:
            for line in lines:
                clean = re.sub(r"^[-*#\d\.\s]+", "", line).strip()
                if len(clean) > 25 and not clean.startswith("--- Source:"):
                    in_scope.append(
                        ScopeItem(
                            id=f"SC-{len(in_scope)+1:02d}",
                            title=clean[:60],
                            description=clean,
                            category="core_feature",
                            in_scope=True,
                            confidence=0.85,
                            source_reference=primary_doc,
                        )
                    )
                    if len(in_scope) >= 6:
                        break

        if not deliverables and in_scope:
            for idx, item in enumerate(in_scope[:4]):
                deliverables.append(
                    Deliverable(
                        id=f"DEL-{idx+1:02d}",
                        title=f"Delivery of {item.title}",
                        description=item.description,
                        target_date=f"Phase {idx+1}",
                        milestone=f"Milestone {idx+1}",
                        status="in_progress" if idx == 0 else "pending",
                        deliverable_type="feature",
                        source_reference=item.source_reference or primary_doc,
                    )
                )

        if not out_of_scope:
            out_of_scope.append(
                ScopeItem(
                    id="OOS-01",
                    title="Unspecified External System Integrations",
                    description="Any third-party integration not explicitly detailed in the uploaded project documents is deferred to post-release.",
                    category="out_of_scope",
                    in_scope=False,
                    source_reference=primary_doc,
                )
            )

        return ScopeReport(
            project_title=project_title,
            project_objective=project_objective,
            target_audience=target_audience,
            in_scope_items=in_scope[:8],
            out_of_scope_items=out_of_scope[:4],
            key_deliverables=deliverables[:8],
            summary=f"Extracted {len(in_scope)} in-scope items and {len(deliverables)} deliverables dynamically from {', '.join(doc_names)}.",
        )
