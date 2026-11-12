from typing import List, Dict, Any
from app.agents.base_agent import BaseAgent
from app.models.project import UserStory, RiskItem, ActionItem, DocumentationBundle


class DocumentationGeneratorAgent(BaseAgent):
    """
    Documentation Generation Agent.
    Synthesizes missing project documentation including Agile User Stories,
    formal Risk Registers, actionable to-do matrices, and detects critical documentation gaps.
    """

    def __init__(self, vector_store, retriever, llm):
        super().__init__(
            name="DocumentationGeneratorAgent",
            role="Technical Documentation & Agile Artifact Specialist",
            vector_store=vector_store,
            retriever=retriever,
            llm=llm,
        )

    def run(self, risks: List[RiskItem] = None, action_items: List[ActionItem] = None) -> DocumentationBundle:
        context = self.get_relevant_context(
            [
                "user requirements user stories persona as a i want so that acceptance criteria",
                "functional specification use cases system features user interaction",
                "non-functional requirements testing documentation gaps architecture",
            ],
            top_k=6,
        )

        prompt = f"""
You are an expert Agile Product Owner & Technical Documentation Specialist.
Generate structured missing documentation for the project based on the context below:
1. 4-6 high quality Agile User Stories following the format:
   - id (e.g. US-01)
   - title
   - as_a (user persona)
   - i_want_to (action or capability)
   - so_that (business value or benefit)
   - acceptance_criteria (list of 3-4 specific verifiable conditions)
   - priority (Must Have | Should Have | Could Have)
   - estimated_story_points (1, 2, 3, 5, 8)
   - epic_tag (e.g. Core Ingestion, RAG Pipeline, Analytics, Assistant)

2. Critical Documentation Gaps (list of 3-5 strings describing what documents are missing, e.g. "Test Plan", "API Spec", "Rollback Strategy")

Document Context:
{context}

Respond in strictly valid JSON:
{{
  "user_stories": [
    {{
      "id": "US-01",
      "title": "...",
      "as_a": "Project Lead",
      "i_want_to": "...",
      "so_that": "...",
      "acceptance_criteria": ["Given...", "When...", "Then..."],
      "priority": "Must Have",
      "estimated_story_points": 5,
      "epic_tag": "RAG Knowledge Base"
    }}
  ],
  "missing_documentation_gaps": [
    "Comprehensive Test Plan covering edge cases in PDF table extraction",
    "Deployment Runbook and Production Scaling Strategy"
  ]
}}
"""
        json_data = self.llm.generate_json(prompt, system_instruction="You are a strict agile documentation generator.")
        if json_data and "user_stories" in json_data:
            try:
                user_stories = [UserStory(**item) for item in json_data["user_stories"]]
                gaps = json_data.get("missing_documentation_gaps", [])
                return DocumentationBundle(
                    user_stories=user_stories,
                    risk_register=risks or [],
                    action_items=action_items or [],
                    missing_documentation_gaps=gaps,
                )
            except Exception as e:
                print(f"[DocGenAgent] JSON parse error: {e}. Falling back to heuristic generator.")

        return self._heuristic_generation(context, risks, action_items)

    def _heuristic_generation(
        self, context: str, risks: List[RiskItem] = None, action_items: List[ActionItem] = None
    ) -> DocumentationBundle:
        user_stories = [
            UserStory(
                id="US-01",
                title="Multi-Format Project Artifact Ingestion",
                as_a="Project Manager or Student Lead",
                i_want_to="upload proposal PDFs, SRS DOCX files, meeting notes, and task CSVs",
                so_that="I have a centralized, unified knowledge base without manually consolidating notes",
                acceptance_criteria=[
                    "System successfully accepts and extracts text from .pdf, .docx, .csv, .txt, and .md files",
                    "Uploaded artifacts are partitioned into chunks with source metadata attached",
                    "System provides immediate ingestion status feedback and character/word statistics",
                ],
                priority="Must Have",
                estimated_story_points=5,
                epic_tag="Knowledge Base Construction",
            ),
            UserStory(
                id="US-02",
                title="Automated Risk Detection and Scoring",
                as_a="Scrum Master or Tech Lead",
                i_want_to="run automated risk analysis over uploaded sprint and requirement artifacts",
                so_that="I can identify schedule slippage and technical bottlenecks before they cause missed deadlines",
                acceptance_criteria=[
                    "System detects technical, schedule, dependency, and resource risks",
                    "Each risk receives a calculated severity score (1-25) based on probability and impact",
                    "Actionable mitigation strategies and contingency plans are generated for high-severity items",
                ],
                priority="Must Have",
                estimated_story_points=5,
                epic_tag="Risk Advisor Pipeline",
            ),
            UserStory(
                id="US-03",
                title="Grounded Conversational Project Assistant",
                as_a="Developer or Team Member",
                i_want_to="ask natural language questions about project status, deadlines, and blockers",
                so_that="I can get fast, accurate answers directly cited from official team documentation",
                acceptance_criteria=[
                    "Assistant answers queries using hybrid semantic + keyword RAG retrieval",
                    "Every answer includes clickable citation references with file name and excerpt",
                    "Assistant clarifies when answers cannot be found in the uploaded documents",
                ],
                priority="Must Have",
                estimated_story_points=8,
                epic_tag="Conversational Assistant",
            ),
            UserStory(
                id="US-04",
                title="Holistic Project Health Scoring Dashboard",
                as_a="Stakeholder or Course Instructor",
                i_want_to="view an objective 100-point project health score across multiple dimensions",
                so_that="I can quickly evaluate project viability and identify areas requiring immediate intervention",
                acceptance_criteria=[
                    "Overall health score computed from Planning, Timeline, Risk, Docs, and Blockers",
                    "Interactive radar chart and category progress bars displayed in the UI",
                    "Top positive factors and top vulnerabilities highlighted with remediation steps",
                ],
                priority="Should Have",
                estimated_story_points=3,
                epic_tag="Project Health Analytics",
            ),
            UserStory(
                id="US-05",
                title="Automated Agile Artifact & Risk Register Export",
                as_a="Technical Writer or Agile Coach",
                i_want_to="export generated user stories, risk registers, and action items as Markdown or JSON",
                so_that="I can instantly import them into Jira, GitHub Issues, or project wiki repositories",
                acceptance_criteria=[
                    "One-click export available in Markdown and JSON formats",
                    "Export bundle includes User Stories with Gherkin acceptance criteria and full Risk Register",
                ],
                priority="Should Have",
                estimated_story_points=3,
                epic_tag="Documentation Generation",
            ),
        ]

        missing_gaps = [
            "Formal QA / Test Automation Plan covering end-to-end integration test suites.",
            "Non-Functional Requirements (NFR) benchmark specifying target response latencies and concurrency limits.",
            "Production Deployment & Disaster Recovery Runbook for vector index backups.",
            "Security & Compliance Checklist for handling proprietary or sensitive corporate project documents.",
        ]

        return DocumentationBundle(
            user_stories=user_stories,
            risk_register=risks or [],
            action_items=action_items or [],
            missing_documentation_gaps=missing_gaps,
        )
