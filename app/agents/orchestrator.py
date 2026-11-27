from datetime import datetime
from typing import Dict, Any, Optional, List
from app.rag.vector_store import VectorStore
from app.rag.retriever import HybridRetriever
from app.agents.llm_provider import LLMProvider
from app.agents.scope_agent import ScopeDeliverableAgent
from app.agents.risk_agent import RiskForecastAgent
from app.agents.blocker_agent import BlockerActionAgent
from app.agents.doc_generator_agent import DocumentationGeneratorAgent
from app.analytics.health_scorer import HealthScorer
from app.models.project import ScopeReport, DeliveryForecast, DocumentationBundle
from app.models.health import ProjectHealthReport


class ProjectIntelligenceOrchestrator:
    """
    Multi-Agent Orchestrator.
    Coordinates sequential execution of the 4 specialized agents,
    manages inter-agent data passing, invokes the Health Scorer,
    maintains persistent analysis history, and caches the latest state.
    """

    def __init__(self, vector_store: VectorStore, retriever: HybridRetriever, llm: LLMProvider):
        self.vector_store = vector_store
        self.retriever = retriever
        self.llm = llm

        # Initialize subagents
        self.scope_agent = ScopeDeliverableAgent(vector_store, retriever, llm)
        self.risk_agent = RiskForecastAgent(vector_store, retriever, llm)
        self.blocker_agent = BlockerActionAgent(vector_store, retriever, llm)
        self.doc_agent = DocumentationGeneratorAgent(vector_store, retriever, llm)
        self.health_scorer = HealthScorer()

        # Cached state & History
        self.last_analysis: Optional[Dict[str, Any]] = None
        self.analysis_history: List[Dict[str, Any]] = []

    def run_full_pipeline(self) -> Dict[str, Any]:
        """
        Executes the complete multi-agent workflow:
        1. Scope & Deliverable extraction
        2. Risk detection & Delivery forecasting
        3. Blocker & Action item identification
        4. Documentation generation (User Stories, Risk Register)
        5. Holistic Project Health Scoring
        """
        print("[Orchestrator] Step 1/5: Running Scope & Deliverables Extraction Agent...")
        scope_report: ScopeReport = self.scope_agent.run()

        print("[Orchestrator] Step 2/5: Running Risk Detection & Delivery Forecasting Agent...")
        risks, delivery_forecast = self.risk_agent.run()

        print("[Orchestrator] Step 3/5: Running Blocker & Action Item Identification Agent...")
        blockers, action_items = self.blocker_agent.run()

        print("[Orchestrator] Step 4/5: Running Documentation Generation Agent...")
        doc_bundle: DocumentationBundle = self.doc_agent.run(risks=risks, action_items=action_items)

        print("[Orchestrator] Step 5/5: Computing Holistic Project Health Score...")
        health_report: ProjectHealthReport = self.health_scorer.compute_health(
            scope_report=scope_report,
            risks=risks,
            forecast=delivery_forecast,
            blockers=blockers,
            action_items=action_items,
            doc_bundle=doc_bundle,
            total_documents=len(self.vector_store.chunks),
        )

        analysis_result = {
            "scope_report": scope_report.model_dump(),
            "risks": [r.model_dump() for r in risks],
            "delivery_forecast": delivery_forecast.model_dump(),
            "blockers": [b.model_dump() for b in blockers],
            "action_items": [a.model_dump() for a in action_items],
            "documentation": doc_bundle.model_dump(),
            "health_report": health_report.model_dump(),
            "agent_summary": {
                "active_llm": self.llm.get_active_provider_name(),
                "total_risks_identified": len(risks),
                "total_blockers_open": len(blockers),
                "total_action_items": len(action_items),
                "total_user_stories_generated": len(doc_bundle.user_stories),
                "overall_health_score": health_report.overall_score,
                "health_grade": health_report.health_grade,
            },
        }

        self.last_analysis = analysis_result

        # Preserve execution history
        history_entry = {
            "id": f"run_{len(self.analysis_history) + 1}",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "project_title": scope_report.project_title,
            "overall_score": health_report.overall_score,
            "health_grade": health_report.health_grade,
            "total_risks": len(risks),
            "total_blockers": len(blockers),
            "data": analysis_result,
        }
        self.analysis_history.append(history_entry)

        return analysis_result

    def get_latest_analysis(self) -> Optional[Dict[str, Any]]:
        return self.last_analysis

    def get_analysis_history(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": h["id"],
                "timestamp": h["timestamp"],
                "project_title": h["project_title"],
                "overall_score": h["overall_score"],
                "health_grade": h["health_grade"],
                "total_risks": h["total_risks"],
                "total_blockers": h["total_blockers"],
            }
            for h in self.analysis_history
        ]

    def get_history_item(self, run_id: str) -> Optional[Dict[str, Any]]:
        for h in self.analysis_history:
            if h["id"] == run_id:
                return h["data"]
        return None
