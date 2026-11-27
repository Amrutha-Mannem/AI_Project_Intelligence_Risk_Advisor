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
        context_lower = context.lower()

        # FinRelief AI project grounded user stories
        if "finrelief" in context_lower:
            user_stories = [
                UserStory(
                    id="US-01",
                    title="Guided Loan Portfolio Registration & Aggregation",
                    as_a="Distressed Borrower",
                    i_want_to="input my loan balances, interest rates, monthly EMIs, and creditor names into a secure dashboard",
                    so_that="I have a consolidated overview of my aggregate debt liabilities without sharing raw bank passwords",
                    acceptance_criteria=[
                        "Given an authenticated borrower, When they enter principal balance, interest rate, and monthly EMI, Then the debt portfolio computes total monthly commitment and overall debt load.",
                        "Given invalid or negative loan values, When the form is submitted, Then client-side validation displays explanatory error prompts and blocks submission.",
                        "Given multiple loans across lenders, When saved, Then the system organizes creditors by urgency and interest rate hierarchy."
                    ],
                    priority="Must Have",
                    estimated_story_points=5,
                    epic_tag="Core Debt Engine",
                ),
                UserStory(
                    id="US-02",
                    title="Affordability Assessment & Settlement Feasibility Prediction",
                    as_a="Borrower seeking settlement",
                    i_want_to="calculate my realistic lump-sum settlement targets based on disposable surplus income",
                    so_that="I can propose debt settlements that creditors will realistically accept without bankrupting myself",
                    acceptance_criteria=[
                        "Given monthly income and essential expenses, When the assessment runs, Then the engine computes Debt-to-Income (DTI) and net disposable surplus.",
                        "Given a high DTI ratio (>50%), When evaluated, Then the platform flags the borrower for proactive hardship negotiation rather than aggressive consolidation.",
                        "Given historical lender settlement benchmarks, When settlement is estimated, Then realistic lump-sum targets (e.g. 40-60% of principal) are generated with confidence scores."
                    ],
                    priority="Must Have",
                    estimated_story_points=5,
                    epic_tag="Settlement Analytics",
                ),
                UserStory(
                    id="US-03",
                    title="AI-Assisted Formal Hardship Letter Generator",
                    as_a="Borrower facing aggressive collections",
                    i_want_to="generate a formal, customized hardship negotiation letter citing my specific financial circumstances",
                    so_that="I can formally request interest moratoriums, EMI reductions, or one-time settlements from collection agencies",
                    acceptance_criteria=[
                        "Given registered creditor details and debt balances, When 'Generate Letter' is clicked, Then Gemini AI synthesizes a professional hardship letter referencing legal norms.",
                        "Given Gemini API rate limits or network outage, When letter generation is requested, Then deterministic local template fallback activates within 500ms without error.",
                        "Given generated letter output, When reviewed by the borrower, Then an edit mode and one-click PDF/TXT export options are provided."
                    ],
                    priority="Must Have",
                    estimated_story_points=8,
                    epic_tag="AI Negotiation",
                ),
                UserStory(
                    id="US-04",
                    title="Multi-Currency & Regional Language Advisory Support",
                    as_a="Regional Borrower (Telugu / Hindi speaker)",
                    i_want_to="view financial advice and letter drafts translated into my preferred regional language",
                    so_that="I can comprehend negotiation options without language barriers impeding debt relief",
                    acceptance_criteria=[
                        "Given selected language preference (English, Telugu, Hindi), When navigation renders, Then financial health metrics and advice are displayed in that language.",
                        "Given currency input, When selecting INR or USD, Then settlement target estimations format correctly with local thousand-separators and symbols.",
                    ],
                    priority="Should Have",
                    estimated_story_points=5,
                    epic_tag="Accessibility & Localization",
                ),
                UserStory(
                    id="US-05",
                    title="Automated Bank Statement OCR Ingestion",
                    as_a="Time-Constrained Borrower",
                    i_want_to="upload PDF bank statements to automatically extract loan EMIs, income streams, and transaction history",
                    so_that="I avoid tedious manual data entry and prevent transcription inaccuracies",
                    acceptance_criteria=[
                        "Given a standard PDF bank e-statement, When uploaded, Then OCR parser extracts monthly recurring salary and loan debits.",
                        "Given extracted figures, When presented to user, Then borrower can verify and approve before portfolio consolidation.",
                        "Given sensitive bank statements, When processed, Then document chunks are encrypted in transit and at rest."
                    ],
                    priority="Could Have",
                    estimated_story_points=8,
                    epic_tag="Smart Ingestion",
                ),
            ]
            missing_gaps = [
                "Automated Bank Statement OCR Integration Specification (replaces manual data entry)",
                "Offline Rule-Based Hardship Letter Fallback Test Suite & Performance Benchmarks",
                "Regional Banking Ombudsman Settlement Compliance Guidelines (RBI / Consumer Bureau)",
                "End-to-End PII Encryption & Security Runbook for Stored Financial Records",
            ]
            return DocumentationBundle(
                user_stories=user_stories,
                risk_register=risks or [],
                action_items=action_items or [],
                missing_documentation_gaps=missing_gaps,
            )

        # APSRTC Smart Yatra grounded user stories
        if "apsrtc" in context_lower or "yatra" in context_lower:
            user_stories = [
                UserStory(
                    id="US-01",
                    title="Real-Time Bus Tracking & Route Navigation",
                    as_a="AP Commuter",
                    i_want_to="track live GPS locations and expected arrival times (ETA) for APSRTC buses",
                    so_that="I can minimize waiting time at bus shelters and plan connections reliably",
                    acceptance_criteria=[
                        "Given a route number or station, When searched, Then live map displays bus marker with updated ETA within 5 seconds.",
                        "Given network degradation, When GPS drops, Then estimated schedule timestamps are clearly distinguished from live tracking.",
                    ],
                    priority="Must Have",
                    estimated_story_points=5,
                    epic_tag="Fleet Tracking",
                ),
                UserStory(
                    id="US-02",
                    title="Voice-Activated Commuter Assistance in Telugu & English",
                    as_a="Commuter on the move or with visual impairment",
                    i_want_to="speak voice queries regarding bus timings, platform numbers, and fares in Telugu",
                    so_that="I can navigate APSRTC services hands-free without typing on a mobile screen",
                    acceptance_criteria=[
                        "Given spoken voice input via Web Speech API, When query completes, Then assistant responds with audio speech synthesis and text transcript.",
                        "Given ambiguous stops, When multiple destinations match, Then assistant prompts commuter to clarify before confirming bus number.",
                    ],
                    priority="Must Have",
                    estimated_story_points=8,
                    epic_tag="Voice AI",
                ),
                UserStory(
                    id="US-03",
                    title="Automated Passenger Grievance Redressal Generator",
                    as_a="Aggrieved Passenger",
                    i_want_to="generate a formal complaint letter with depot code, ticket number, and driver details",
                    so_that="I can escalate service deficiencies to depot managers with verifiable evidence",
                    acceptance_criteria=[
                        "Given complaint category (overcrowding, delay, staff conduct), When submitted, Then formal letter is generated with unique reference ID.",
                        "Given generated grievance, When reviewed, Then user can download PDF and dispatch to APSRTC grievance cell.",
                    ],
                    priority="Should Have",
                    estimated_story_points=5,
                    epic_tag="Grievance Portal",
                ),
            ]
            missing_gaps = [
                "Live Vehicle GPS Telemetry Webhook Protocol & API Latency Contract",
                "Telugu Speech-to-Text Acoustic Model Accuracy Benchmark Specification",
                "Depot Dispatcher Failover Operations Runbook for Bus Breakdown Rescheduling",
            ]
            return DocumentationBundle(
                user_stories=user_stories,
                risk_register=risks or [],
                action_items=action_items or [],
                missing_documentation_gaps=missing_gaps,
            )

        # Generic enterprise fallback
        user_stories = [
            UserStory(
                id="US-01",
                title="Multi-Format Project Artifact Ingestion",
                as_a="Project Manager or Student Lead",
                i_want_to="upload proposal PDFs, SRS DOCX files, meeting notes, and task CSVs",
                so_that="I have a centralized, unified knowledge base without manually consolidating notes",
                acceptance_criteria=[
                    "Given a valid project artifact (.pdf, .docx, .csv, .txt, .md), When uploaded, Then system extracts text and generates chunks.",
                    "Given unsupported file formats, When uploaded, Then system returns helpful validation messages without crashing.",
                    "Given partitioned chunks, When indexed, Then document metadata and source attribution are linked to every chunk."
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
                    "Given ingested project documents, When Risk Agent executes, Then risks are mapped across 5x5 severity matrix.",
                    "Given severity score calculation, When P and I are scored 1-5, Then severity equals Probability x Impact.",
                    "Given high severity risks (>=15), When detected, Then actionable mitigations and contingency plans are generated."
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
                    "Given a user query, When assistant searches, Then hybrid semantic + keyword RAG retrieval retrieves grounded excerpts.",
                    "Given generated answer, When displayed, Then clickable source document citations and chunk IDs are included.",
                    "Given ungrounded queries, When information is absent from documents, Then assistant explicitly states document limitations."
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
                    "Given analysis completion, When health is computed, Then score is weighted across Planning, Timeline, Risk, Docs, and Blockers.",
                    "Given health category breakdown, When inspected, Then dimension scores and status badges are rendered.",
                    "Given project vulnerabilities, When identified, Then clear improvement recommendations are listed."
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
                    "Given analyzed project artifacts, When export is clicked, Then Markdown and JSON bundles are generated.",
                    "Given export payload, When validated, Then stories with Gherkin criteria and 5x5 risk registers are formatted."
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
