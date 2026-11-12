from typing import Optional
from fastapi import APIRouter, Response, HTTPException
from pydantic import BaseModel
from app.deps import orchestrator, llm_provider

router = APIRouter(prefix="/api/export", tags=["Export & Settings"])


class KeyUpdateRequest(BaseModel):
    gemini_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None


@router.post("/settings/keys")
async def update_api_keys(req: KeyUpdateRequest):
    llm_provider.update_keys(
        gemini_key=req.gemini_api_key,
        openai_key=req.openai_api_key,
    )
    return {
        "status": "success",
        "active_provider": llm_provider.get_active_provider_name(),
        "gemini_configured": bool(llm_provider.gemini_key),
        "openai_configured": bool(llm_provider.openai_key),
    }


@router.get("/status")
async def get_system_status():
    return {
        "active_provider": llm_provider.get_active_provider_name(),
        "gemini_configured": bool(llm_provider.gemini_key),
        "openai_configured": bool(llm_provider.openai_key),
    }


@router.get("/markdown")
async def export_markdown_report():
    analysis = orchestrator.get_latest_analysis()
    if not analysis:
        raise HTTPException(status_code=400, detail="No project analysis available. Run the multi-agent pipeline first.")

    scope = analysis.get("scope_report", {})
    forecast = analysis.get("delivery_forecast", {})
    health = analysis.get("health_report", {})
    risks = analysis.get("risks", [])
    blockers = analysis.get("blockers", [])
    actions = analysis.get("action_items", [])
    docs = analysis.get("documentation", {})
    user_stories = docs.get("user_stories", [])

    md_lines = [
        f"# AI Project Intelligence & Risk Advisor Report",
        f"**Project Title:** {scope.get('project_title', 'Project Intelligence')}",
        f"**Objective:** {scope.get('project_objective', '')}",
        f"**Overall Health:** {health.get('overall_score', 'N/A')}/100 ({health.get('health_grade', '')})",
        f"**Delivery Forecast:** {forecast.get('forecast_status', '')} (Estimated delay: {forecast.get('predicted_delay_days', 0)} days)",
        "\n---\n",
        "## Executive Summary",
        health.get("executive_summary", ""),
        "\n## Health Dimension Breakdown",
    ]

    for cat in health.get("categories", []):
        md_lines.append(f"- **{cat.get('category_name')}:** {cat.get('score')}/100 [{cat.get('status').upper()}]")
        md_lines.append(f"  *Advice:* {cat.get('improvement_advice')}")

    md_lines.append("\n## Active Critical Risks (Risk Matrix)")
    md_lines.append("| ID | Title | Category | Severity Score | Probability | Impact | Mitigation |")
    md_lines.append("|---|---|---|---|---|---|---|")
    for r in risks:
        md_lines.append(f"| {r.get('id')} | {r.get('risk_title')} | {r.get('category')} | {r.get('severity_score')} | {r.get('probability')} | {r.get('impact')} | {r.get('mitigation_strategy')} |")

    md_lines.append("\n## Active Blockers & Impediments")
    md_lines.append("| ID | Blocker Title | Severity | Owner | Impacted Milestone | Suggested Resolution |")
    md_lines.append("|---|---|---|---|---|---|")
    for b in blockers:
        md_lines.append(f"| {b.get('id')} | {b.get('title')} | {b.get('severity')} | {b.get('assigned_owner')} | {b.get('impacted_deliverable')} | {b.get('suggested_resolution')} |")

    md_lines.append("\n## Action Items & Next Steps")
    md_lines.append("| ID | Task Description | Assignee | Priority | Due Date | Status |")
    md_lines.append("|---|---|---|---|---|---|")
    for a in actions:
        md_lines.append(f"| {a.get('id')} | {a.get('task_description')} | {a.get('assignee')} | {a.get('priority')} | {a.get('due_date')} | {a.get('status')} |")

    md_lines.append("\n## Generated Agile User Stories")
    for us in user_stories:
        md_lines.append(f"### {us.get('id')}: {us.get('title')} ({us.get('estimated_story_points')} pts - {us.get('priority')})")
        md_lines.append(f"- **As a:** {us.get('as_a')}")
        md_lines.append(f"- **I want to:** {us.get('i_want_to')}")
        md_lines.append(f"- **So that:** {us.get('so_that')}")
        md_lines.append("- **Acceptance Criteria:**")
        for ac in us.get("acceptance_criteria", []):
            md_lines.append(f"  - {ac}")
        md_lines.append("")

    content = "\n".join(md_lines)
    return Response(content=content, media_type="text/markdown", headers={"Content-Disposition": "attachment; filename=project_intelligence_report.md"})


@router.get("/json")
async def export_json_report():
    analysis = orchestrator.get_latest_analysis()
    if not analysis:
        raise HTTPException(status_code=400, detail="No project analysis available.")
    return analysis
