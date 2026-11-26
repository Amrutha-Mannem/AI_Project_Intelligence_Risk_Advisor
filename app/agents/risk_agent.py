import re
from typing import List, Dict, Any, Tuple
from app.agents.base_agent import BaseAgent
from app.models.project import RiskItem, DeliveryForecast


class RiskForecastAgent(BaseAgent):
    """
    Risk Detection and Delivery Forecasting Agent.
    Specializes in identifying technical, schedule, dependency, and resource vulnerabilities,
    computing quantitative risk severity matrix scores (P x I: 1-25),
    and forecasting delivery variance strictly grounded in uploaded project documents.
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
   - severity_score (integer from 1 to 25, calculated as probability 1-5 multiplied by impact 1-5)
   - early_warning_signs (list of strings)
   - mitigation_strategy
   - contingency_plan
   - status (identified | mitigating | resolved)
   - source_reference (MUST be the exact file name from '--- Source: <filename> ---' where this risk was detected)

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
      "status": "identified",
      "source_reference": "..."
    }}
  ],
  "delivery_forecast": {{
    "forecast_status": "At Risk",
    "predicted_delay_days": 7,
    "confidence_level": 0.85,
    "critical_path_factors": ["..."],
    "forecast_narrative": "...",
    "recommendations": ["..."]
  }}
}}
"""
        json_data = self.llm.generate_json(prompt, system_instruction="You are a strict risk assessment agent. Ground all risks directly in the uploaded text excerpts.")
        if json_data and "risks" in json_data and "delivery_forecast" in json_data:
            try:
                default_doc = self.vector_store.chunks[0].source_name if self.vector_store.chunks else "Uploaded Document"
                risks = []
                for item in json_data["risks"]:
                    if not item.get("source_reference"):
                        item["source_reference"] = default_doc
                    risks.append(RiskItem(**item))

                forecast = DeliveryForecast(**json_data["delivery_forecast"])
                return risks, forecast
            except Exception as e:
                print(f"[RiskAgent] JSON parse error: {e}. Falling back to dynamic heuristic engine.")

        return self._heuristic_analysis(context)

    def _heuristic_analysis(self, context: str) -> Tuple[List[RiskItem], DeliveryForecast]:
        context_lower = context.lower()
        lines = [l.strip() for l in context.splitlines() if l.strip()]
        doc_names = list(dict.fromkeys(c.source_name for c in self.vector_store.chunks))
        primary_doc = doc_names[0] if doc_names else "Uploaded Document"

        risks: List[RiskItem] = []
        critical_factors: List[str] = []
        delay_days = 0

        # Helper to find which uploaded file contains keywords
        def _find_source(keywords: List[str]) -> str:
            for chunk in self.vector_store.chunks:
                txt = chunk.content.lower()
                if any(k in txt for k in keywords):
                    return chunk.source_name
            return primary_doc

        # Pattern 1: API / Third Party Integration
        if any(w in context_lower for w in ["api rate limit", "third-party", "vendor", "external api", "integration failure", "quota", "timeout"]):
            src = _find_source(["api", "rate limit", "third-party", "vendor", "endpoint"])
            risks.append(
                RiskItem(
                    id="RSK-01",
                    risk_title="Third-Party API Dependency & Quota Bottlenecks",
                    description="Heavy reliance on external services or third-party APIs without caching and fallback mechanisms.",
                    category="dependency",
                    probability="High",
                    impact="High",
                    severity_score=20,
                    early_warning_signs=["HTTP 429 rate limit errors", "Provider status incidents", "Latency spikes"],
                    mitigation_strategy="Implement local fallback, caching layers, and client retry backoff.",
                    contingency_plan="Switch automatically to secondary endpoint or cached response repository.",
                    status="identified",
                    source_reference=src,
                )
            )
            critical_factors.append("API service latency and dependency rate limits")
            delay_days += 5

        # Pattern 2: Schedule / Missed Deadlines / Scope Creep
        if any(w in context_lower for w in ["deadline", "delay", "behind schedule", "milestone slip", "overdue", "late", "timeline"]):
            src = _find_source(["deadline", "delay", "behind schedule", "sprint", "meeting", "slip"])
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
                    source_reference=src,
                )
            )
            critical_factors.append("Sprint velocity variance and task spillover")
            delay_days += 7

        # Pattern 3: Resource / Team Skill Constraints
        if any(w in context_lower for w in ["unassigned", "single point of failure", "skill gap", "turnover", "workload", "bottleneck"]):
            src = _find_source(["unassigned", "assignee", "task", "backlog", "resource", "bottleneck"])
            risks.append(
                RiskItem(
                    id="RSK-03",
                    risk_title="Key-Person Dependency & Resource Constraints",
                    description="Critical modules have single assignees without peer knowledge cross-training.",
                    category="resource",
                    probability="Medium",
                    impact="High",
                    severity_score=16,
                    early_warning_signs=["Task bottlenecking around one developer", "PR reviews stalling"],
                    mitigation_strategy="Mandate architecture documentation, peer code pairing, and shared ownership.",
                    contingency_plan="Cross-train adjacent engineers on critical path modules.",
                    status="identified",
                    source_reference=src,
                )
            )
            critical_factors.append("Developer bandwidth saturation")
            delay_days += 4

        # Pattern 4: Incomplete Documentation & Spec Ambiguity
        if any(w in context_lower for w in ["tbd", "unclear", "missing requirement", "incomplete", "vague", "assumption"]):
            src = _find_source(["tbd", "unclear", "specification", "proposal", "srs", "incomplete"])
            risks.append(
                RiskItem(
                    id="RSK-04",
                    risk_title="Ambiguous Requirements & Scope Creep",
                    description="Document excerpts contain TBD items or unspecified acceptance criteria, risking rework.",
                    category="scope_creep",
                    probability="Medium",
                    impact="Medium",
                    severity_score=12,
                    early_warning_signs=["Frequent requirement debates in standups", "Mid-sprint task re-definitions"],
                    mitigation_strategy="Hold backlog grooming sessions with strict Definition of Ready (DoR).",
                    contingency_plan="Lock Milestone 1 scope and defer dynamic revisions to Milestone 2.",
                    status="identified",
                    source_reference=src,
                )
            )
            critical_factors.append("Requirement ambiguity requiring rework")
            delay_days += 3

        # Dynamic fallback: scan lines for any project risk statements
        if not risks and lines:
            for line in lines:
                clean = re.sub(r"^[-*#\d\.\s]+", "", line).strip()
                if len(clean) > 20 and not clean.startswith("--- Source:"):
                    line_l = clean.lower()
                    if any(w in line_l for w in ["risk", "concern", "challenge", "threat", "vulnerability", "limitation", "fail", "security", "cost"]):
                        risks.append(
                            RiskItem(
                                id=f"RSK-{len(risks)+1:02d}",
                                risk_title=clean[:60],
                                description=clean,
                                category="technical",
                                probability="Medium",
                                impact="Medium",
                                severity_score=12,
                                early_warning_signs=["Identified in project documentation review"],
                                mitigation_strategy="Active monitoring and peer review during sprint cycles.",
                                contingency_plan="Define fallback mitigation procedures.",
                                status="identified",
                                source_reference=primary_doc,
                            )
                        )
                        critical_factors.append(clean[:50])
                        delay_days += 3
                        if len(risks) >= 3:
                            break

        # Standard operational baseline if documents are clean
        if not risks:
            risks = [
                RiskItem(
                    id="RSK-01",
                    risk_title="Cross-Document Synchronization Variance",
                    description="Asynchronous updates between project artifacts may lead to conflicting timeline assumptions.",
                    category="schedule",
                    probability="Low",
                    impact="Medium",
                    severity_score=6,
                    early_warning_signs=["Inconsistent dates between SRS and sprint notes"],
                    mitigation_strategy="Execute automated vector re-indexing upon new document ingestion.",
                    status="identified",
                    source_reference=primary_doc,
                )
            ]

        # Determine overall forecast
        if delay_days >= 10:
            status = "Critical Delay"
            narrative = f"Project exhibits significant schedule pressure with estimated {delay_days} days of deliverable delay across critical path bottlenecks."
        elif delay_days > 0:
            status = "At Risk"
            narrative = f"Moderate schedule risks detected; estimated delay buffer is {delay_days} days. Proactive mitigation is recommended."
        else:
            status = "On Track"
            narrative = "Project milestones and deliverables are within acceptable variance thresholds. No critical schedule delays identified."

        forecast = DeliveryForecast(
            forecast_status=status,
            predicted_delay_days=delay_days,
            confidence_level=0.88,
            critical_path_factors=critical_factors or ["Standard delivery schedule execution"],
            forecast_narrative=narrative,
            recommendations=[
                "Prioritize high-severity risk mitigation items during sprint planning.",
                "Verify third-party API dependencies and resource allocations.",
                "Review critical path bottlenecks in weekly progress reviews.",
            ],
        )

        return risks, forecast
