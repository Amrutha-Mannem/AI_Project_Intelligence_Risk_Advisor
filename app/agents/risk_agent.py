import re
from typing import List, Dict, Any, Tuple
from app.agents.base_agent import BaseAgent
from app.models.project import RiskItem, DeliveryForecast


class RiskForecastAgent(BaseAgent):
    """
    Risk Detection and Delivery Forecasting Agent.
    Specializes in identifying technical, schedule, dependency, and resource vulnerabilities,
    computing quantitative risk severity matrix scores, and forecasting delivery challenges.
    """

    def __init__(self, vector_store, retriever, llm):
        super().__init__(
            name="RiskForecastAgent",
            role="Risk Assessment & Schedule Forecasting Specialist",
            vector_store=vector_store,
            retriever=retriever,
            llm=llm,
        )

    def run(self) -> Tuple[List[RiskItem], DeliveryForecast]:
        context = self.get_relevant_context(
            [
                "risks technical challenges schedule delay bottlenecks blockers critical path",
                "dependencies third-party api external vendor resource constraints turnover",
                "scope creep incomplete requirements missed deadlines bug backlog testing delays",
            ],
            top_k=6,
        )

        prompt = f"""
You are an expert Project Risk Manager and Delivery Forecasting Agent.
Analyze the following project document excerpts and:
1. Identify all project risks across Technical, Schedule, Resource, Scope Creep, Dependency, and External categories.
   For each risk provide:
   - id (e.g. RSK-01)
   - risk_title
   - description
   - category (technical | schedule | resource | scope_creep | dependency | external)
   - probability (High | Medium | Low)
   - impact (High | Medium | Low)
   - severity_score (integer from 1 to 25)
   - early_warning_signs (list of strings)
   - mitigation_strategy
   - contingency_plan
   - status (identified | mitigating | resolved)

2. Provide a Delivery Forecast:
   - forecast_status (On Track | At Risk | Critical Delay)
   - predicted_delay_days (integer estimate, 0 if on track)
   - confidence_level (float between 0.1 and 1.0)
   - critical_path_factors (list of strings)
   - forecast_narrative (concise paragraph)
   - recommendations (list of actionable steps)

Document Context:
{context}

Respond in strictly valid JSON:
{{
  "risks": [
    {{
      "id": "RSK-01",
      "risk_title": "...",
      "description": "...",
      "category": "technical",
      "probability": "High",
      "impact": "High",
      "severity_score": 20,
      "early_warning_signs": ["..."],
      "mitigation_strategy": "...",
      "contingency_plan": "...",
      "status": "identified"
    }}
  ],
  "delivery_forecast": {{
    "forecast_status": "At Risk",
    "predicted_delay_days": 10,
    "confidence_level": 0.85,
    "critical_path_factors": ["..."],
    "forecast_narrative": "...",
    "recommendations": ["..."]
  }}
}}
"""
        json_data = self.llm.generate_json(prompt, system_instruction="You are a strict risk assessment agent.")
        if json_data and "risks" in json_data and "delivery_forecast" in json_data:
            try:
                risks = [RiskItem(**item) for item in json_data["risks"]]
                forecast = DeliveryForecast(**json_data["delivery_forecast"])
                return risks, forecast
            except Exception as e:
                print(f"[RiskAgent] JSON parse error: {e}. Falling back to heuristic engine.")

        return self._heuristic_analysis(context)

    def _heuristic_analysis(self, context: str) -> Tuple[List[RiskItem], DeliveryForecast]:
        context_lower = context.lower()
        risks: List[RiskItem] = []
        critical_factors: List[str] = []
        delay_days = 0

        # Heuristic Pattern 1: API / Third Party Integration
        if any(w in context_lower for w in ["api rate limit", "third-party", "vendor", "external api", "integration failure"]):
            risks.append(
                RiskItem(
                    id="RSK-01",
                    risk_title="Third-Party API Dependency & Quota Bottlenecks",
                    description="Heavy reliance on external services, LLM providers, or third-party APIs without fallback caching.",
                    category="dependency",
                    probability="High",
                    impact="High",
                    severity_score=20,
                    early_warning_signs=["HTTP 429 rate limit errors", "Provider status incidents", "Latency spikes"],
                    mitigation_strategy="Implement local embeddings fallback, aggressive response caching, and client retry backoff.",
                    contingency_plan="Switch automatically to local heuristic parser or secondary LLM provider endpoint.",
                    status="identified",
                    source_reference="Uploaded Technical Specifications",
                )
            )
            critical_factors.append("API service latency and rate limits")
            delay_days += 5

        # Heuristic Pattern 2: Schedule / Missed Deadlines / Scope Creep
        if any(w in context_lower for w in ["deadline", "delay", "behind schedule", "milestone slip", "overdue", "late"]):
            risks.append(
                RiskItem(
                    id="RSK-02",
                    risk_title="Milestone Delivery Slippage on Core Features",
                    description="Project documents indicate timeline pressures or sprint deliverable delays.",
                    category="schedule",
                    probability="High",
                    impact="Medium",
                    severity_score=15,
                    early_warning_signs=["Sprint velocity dropping", "Spillover tasks accumulating across sprints"],
                    mitigation_strategy="Scope triage: convert nice-to-have features into post-release backlog items.",
                    contingency_plan="Reallocate team engineering pairs to unblock critical path modules.",
                    status="mitigating",
                    source_reference="Sprint Meeting Notes & Backlog",
                )
            )
            critical_factors.append("Sprint velocity variance and task spillover")
            delay_days += 7

        # Heuristic Pattern 3: Resource / Team Skill Constraints
        if any(w in context_lower for w in ["unassigned", "single point of failure", "skill gap", "turnover", "workload"]):
            risks.append(
                RiskItem(
                    id="RSK-03",
                    risk_title="Key-Person Dependency & Resource Constraints",
                    description="Certain architectural modules have single assignees without peer knowledge cross-training.",
                    category="resource",
                    probability="Medium",
                    impact="High",
                    severity_score=16,
                    early_warning_signs=["Task bottlenecking around one developer", "PR reviews stalling"],
                    mitigation_strategy="Mandate architecture documentation, peer code pairing, and shared ownership.",
                    contingency_plan="Cross-train adjacent engineers on core RAG and ingestion pipelines.",
                    status="identified",
                    source_reference="Task Allocation Board",
                )
            )
            critical_factors.append("Developer bandwidth saturation")
            delay_days += 4

        # Heuristic Pattern 4: Incomplete Documentation & Spec Ambiguity
        if any(w in context_lower for w in ["tbd", "unclear", "missing requirement", "incomplete", "vague"]):
            risks.append(
                RiskItem(
                    id="RSK-04",
                    risk_title="Ambiguous Requirements & Scope Creep",
                    description="SRS and notes contain TBD items or unspecified acceptance criteria, risking rework.",
                    category="scope_creep",
                    probability="Medium",
                    impact="Medium",
                    severity_score=12,
                    early_warning_signs=["Frequent requirement debates in standups", "Mid-sprint task re-definitions"],
                    mitigation_strategy="Hold backlog grooming sessions with strict Definition of Ready (DoR).",
                    contingency_plan="Lock Milestone 1 scope and defer dynamic revisions to Milestone 2.",
                    status="identified",
                    source_reference="Project Proposal & SRS",
                )
            )
            critical_factors.append("Requirement ambiguity requiring rework")
            delay_days += 3

        # Default risks if clean document
        if not risks:
            risks = [
                RiskItem(
                    id="RSK-01",
                    risk_title="Vector Store Scaling & High Query Latency",
                    description="Document corpus growth may elevate query embedding computation and search latency.",
                    category="technical",
                    probability="Medium",
                    impact="Medium",
                    severity_score=12,
                    early_warning_signs=["Query times exceeding 800ms", "Index load spikes"],
                    mitigation_strategy="Implement in-memory numpy normalization, indexing caches, and batch vector search.",
                    contingency_plan="Pre-compute document embeddings during ingestion background workers.",
                    status="identified",
                ),
                RiskItem(
                    id="RSK-02",
                    risk_title="Cross-Document Schedule Sync Latency",
                    description="Asynchronous document updates between meeting notes and task boards lead to stale intelligence.",
                    category="schedule",
                    probability="Low",
                    impact="Medium",
                    severity_score=8,
                    early_warning_signs=["Inconsistent task statuses across artifacts"],
                    mitigation_strategy="Automated periodic RAG re-indexing upon new artifact uploads.",
                    contingency_plan="Alert team members when contradictory dates are detected.",
                    status="identified",
                ),
            ]
            critical_factors = ["Vector index query throughput", "Asynchronous team artifact synchronization"]

        # Determine overall forecast
        if delay_days >= 10:
            status = "At Risk"
            narrative = f"Project exhibits significant schedule pressure with estimated {delay_days} days of potential deliverable delay across critical path modules."
        elif delay_days > 0:
            status = "At Risk"
            narrative = f"Moderate schedule risks detected; estimated delay buffer is ~{delay_days} days. Proactive mitigation recommended."
        else:
            status = "On Track"
            narrative = "Project milestones and deliverables are within acceptable variance thresholds. No critical schedule delays identified."

        forecast = DeliveryForecast(
            forecast_status=status,
            predicted_delay_days=delay_days,
            confidence_level=0.88,
            critical_path_factors=critical_factors if critical_factors else ["Document ingestion stability", "Multi-agent orchestration"],
            forecast_narrative=narrative,
            recommendations=[
                "Prioritize closing unassigned critical path tasks in the current sprint.",
                "Enforce Definition of Ready (DoR) on all user stories prior to implementation.",
                "Utilize local embedding fallbacks to prevent external API quota bottlenecks.",
            ],
        )

        return risks, forecast
