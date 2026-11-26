from typing import Dict, Any
from fastapi import APIRouter, HTTPException
from app.deps import orchestrator, vector_store

router = APIRouter(prefix="/api/agents", tags=["Multi-Agent Pipeline"])


def _require_docs():
    if len(vector_store.chunks) == 0:
        raise HTTPException(
            status_code=400,
            detail="Knowledge base is empty. Upload documents or load sample artifacts first.",
        )


@router.post("/run")
async def run_full_pipeline() -> Dict[str, Any]:
    _require_docs()
    return orchestrator.run_full_pipeline()


@router.get("/latest")
async def get_latest_analysis():
    latest = orchestrator.get_latest_analysis()
    if not latest:
        if len(vector_store.chunks) > 0:
            return orchestrator.run_full_pipeline()
        return {"status": "empty", "message": "No analysis yet. Ingest documents and trigger pipeline."}
    return latest


@router.post("/scope")
async def run_scope_agent():
    _require_docs()
    return orchestrator.scope_agent.run().model_dump()


@router.post("/risks")
async def run_risk_agent():
    _require_docs()
    risks, forecast = orchestrator.risk_agent.run()
    return {
        "risks": [r.model_dump() for r in risks],
        "delivery_forecast": forecast.model_dump(),
    }


@router.post("/blockers")
async def run_blocker_agent():
    _require_docs()
    blockers, action_items = orchestrator.blocker_agent.run()   # fixed: was self_b typo
    return {
        "blockers": [b.model_dump() for b in blockers],
        "action_items": [a.model_dump() for a in action_items],
    }


@router.post("/documentation")
async def run_documentation_agent():
    _require_docs()
    doc_bundle = orchestrator.doc_agent.run()
    return doc_bundle.model_dump()
