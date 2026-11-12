from typing import List, Dict, Any
from app.models.project import ScopeReport, RiskItem, DeliveryForecast, BlockerItem, ActionItem, DocumentationBundle
from app.models.health import ProjectHealthReport, HealthCategoryScore


class HealthScorer:
    """
    Project Health Scoring Algorithm.
    Computes an objective, multi-dimensional 100-point project health score
    based on scope clarity, schedule variance, risk exposure, blocker severity,
    and documentation completeness.
    """

    def compute_health(
        self,
        scope_report: ScopeReport,
        risks: List[RiskItem],
        forecast: DeliveryForecast,
        blockers: List[BlockerItem],
        action_items: List[ActionItem],
        doc_bundle: DocumentationBundle,
        total_documents: int,
    ) -> ProjectHealthReport:

        # 1. Planning & Scope Completeness (Weight 20%)
        # Based on defined deliverables, clear scope items, out-of-scope boundaries
        planning_base = 70.0
        if len(scope_report.in_scope_items) >= 4:
            planning_base += 15.0
        if len(scope_report.key_deliverables) >= 3:
            planning_base += 10.0
        if len(scope_report.out_of_scope_items) >= 1:
            planning_base += 5.0
        planning_score = min(100.0, max(20.0, planning_base))
        planning_cat = HealthCategoryScore(
            category_name="Planning & Scope Definition",
            score=round(planning_score, 1),
            weight=0.20,
            status="healthy" if planning_score >= 80 else ("warning" if planning_score >= 60 else "critical"),
            findings=[
                f"{len(scope_report.in_scope_items)} in-scope functional items identified",
                f"{len(scope_report.key_deliverables)} milestones/deliverables tracked",
                f"{len(scope_report.out_of_scope_items)} out-of-scope boundaries delineated",
            ],
            improvement_advice="Formalize acceptance criteria on all secondary deliverables to prevent mid-cycle scope drift.",
        )

        # 2. Timeline & Schedule Variance (Weight 25%)
        # Penalties based on predicted delay days and forecast status
        timeline_base = 95.0
        timeline_base -= min(50.0, forecast.predicted_delay_days * 3.5)
        if forecast.forecast_status == "Critical Delay":
            timeline_base -= 25.0
        elif forecast.forecast_status == "At Risk":
            timeline_base -= 12.0
        timeline_score = min(100.0, max(15.0, timeline_base))
        timeline_cat = HealthCategoryScore(
            category_name="Timeline & Schedule Adherence",
            score=round(timeline_score, 1),
            weight=0.25,
            status="healthy" if timeline_score >= 80 else ("warning" if timeline_score >= 60 else "critical"),
            findings=[
                f"Forecast Status: {forecast.forecast_status}",
                f"Estimated schedule delay buffer: {forecast.predicted_delay_days} days",
                f"{len(forecast.critical_path_factors)} critical path bottlenecks identified",
            ],
            improvement_advice="Rebalance sprint capacity to unblock critical path activities.",
        )

        # 3. Risk Exposure & Mitigation (Weight 25%)
        # Penalties based on high-severity risks and unresolved items
        high_risks = [r for r in risks if r.severity_score >= 15]
        med_risks = [r for r in risks if 8 <= r.severity_score < 15]
        risk_base = 90.0 - (len(high_risks) * 12.0) - (len(med_risks) * 5.0)
        risk_score = min(100.0, max(15.0, risk_base))
        risk_cat = HealthCategoryScore(
            category_name="Risk Exposure & Mitigation",
            score=round(risk_score, 1),
            weight=0.25,
            status="healthy" if risk_score >= 80 else ("warning" if risk_score >= 60 else "critical"),
            findings=[
                f"{len(high_risks)} high-severity risks (score >= 15)",
                f"{len(med_risks)} medium-severity risks",
                f"{len([r for r in risks if r.mitigation_strategy])} risks have proactive mitigation plans",
            ],
            improvement_advice="Implement automated fallback mechanisms for third-party API dependencies.",
        )

        # 4. Documentation & Story Coverage (Weight 15%)
        doc_base = 65.0
        if doc_bundle.user_stories:
            doc_base += min(25.0, len(doc_bundle.user_stories) * 5.0)
        doc_base -= min(20.0, len(doc_bundle.missing_documentation_gaps) * 4.0)
        doc_score = min(100.0, max(20.0, doc_base))
        doc_cat = HealthCategoryScore(
            category_name="Documentation Completeness",
            score=round(doc_score, 1),
            weight=0.15,
            status="healthy" if doc_score >= 80 else ("warning" if doc_score >= 60 else "critical"),
            findings=[
                f"{len(doc_bundle.user_stories)} structured user stories generated",
                f"{len(doc_bundle.missing_documentation_gaps)} critical documentation gaps identified",
            ],
            improvement_advice="Draft test automation specifications and operational runbooks.",
        )

        # 5. Blocker Severity & Impediments (Weight 15%)
        crit_blockers = [b for b in blockers if b.severity == "critical" and b.status != "resolved"]
        high_blockers = [b for b in blockers if b.severity == "high" and b.status != "resolved"]
        blocker_base = 95.0 - (len(crit_blockers) * 20.0) - (len(high_blockers) * 10.0)
        blocker_score = min(100.0, max(10.0, blocker_base))
        blocker_cat = HealthCategoryScore(
            category_name="Blocker & Impediment Resolution",
            score=round(blocker_score, 1),
            weight=0.15,
            status="healthy" if blocker_score >= 80 else ("warning" if blocker_score >= 60 else "critical"),
            findings=[
                f"{len(crit_blockers)} critical unresolved blockers",
                f"{len(high_blockers)} high-priority open blockers",
                f"{len(action_items)} actionable follow-up items mapped",
            ],
            improvement_advice="Assign dedicated owners to all open critical blockers immediately.",
        )

        # Weighted Composite Score
        categories = [planning_cat, timeline_cat, risk_cat, doc_cat, blocker_cat]
        overall_score = sum(cat.score * cat.weight for cat in categories)
        overall_score = round(max(0.0, min(100.0, overall_score)), 1)

        # Health Grade
        if overall_score >= 85.0:
            health_grade = "A (Excellent)"
        elif overall_score >= 70.0:
            health_grade = "B (Good)"
        elif overall_score >= 50.0:
            health_grade = "C (At Risk)"
        else:
            health_grade = "D (Critical)"

        # Executive Summary
        executive_summary = (
            f"The project currently maintains an overall health score of {overall_score}/100 [{health_grade}]. "
            f"Delivery forecast is rated '{forecast.forecast_status}' with an estimated schedule variance of {forecast.predicted_delay_days} days. "
            f"There are {len(high_risks)} high-severity risks and {len(crit_blockers)} critical blockers requiring team intervention."
        )

        # Positives
        top_positives = []
        if planning_score >= 75:
            top_positives.append("Well-articulated scope definition and milestone roadmap.")
        if len(action_items) >= 3:
            top_positives.append(f"Strong action item accountability with {len(action_items)} tracked tasks.")
        if len(doc_bundle.user_stories) >= 3:
            top_positives.append(f"Agile user story coverage established with {len(doc_bundle.user_stories)} structured stories.")
        if not top_positives:
            top_positives.append("Baseline project artifacts ingested into unified RAG knowledge base.")

        # Vulnerabilities
        top_vulnerabilities = []
        if forecast.predicted_delay_days > 0:
            top_vulnerabilities.append(f"Schedule pressure resulting in estimated {forecast.predicted_delay_days}-day delivery delay.")
        if high_risks:
            top_vulnerabilities.append(f"{len(high_risks)} elevated risks threatening milestone delivery.")
        if crit_blockers:
            top_vulnerabilities.append(f"{len(crit_blockers)} critical blockers halting developer progress.")
        if not top_vulnerabilities:
            top_vulnerabilities.append("Monitor third-party dependencies as project corpus expands.")

        # Immediate Actions
        immediate_actions = [
            f"Resolve blocker: {crit_blockers[0].title}" if crit_blockers else "Review sprint backlog priorities.",
            f"Execute mitigation for risk: {high_risks[0].risk_title}" if high_risks else "Maintain weekly risk register reviews.",
            "Complete missing technical documentation items (Test Plan & Runbooks).",
        ]

        radar_metrics = {
            "Planning": planning_score,
            "Timeline": timeline_score,
            "Risk": risk_score,
            "Docs": doc_score,
            "Blockers": blocker_score,
        }

        return ProjectHealthReport(
            overall_score=overall_score,
            health_grade=health_grade,
            radar_metrics=radar_metrics,
            categories=categories,
            executive_summary=executive_summary,
            top_positives=top_positives,
            top_vulnerabilities=top_vulnerabilities,
            recommended_immediate_actions=immediate_actions,
        )
