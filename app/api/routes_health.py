from fastapi import APIRouter, HTTPException
from app.deps import orchestrator, vector_store

router = APIRouter(prefix="/api/health", tags=["Project Health Scoring"])


@router.get("/score")
async def get_health_score():
    latest = orchestrator.get_latest_analysis()
    if not latest:
        if len(vector_store.chunks) > 0:
            latest = orchestrator.run_full_pipeline()
        else:
            raise HTTPException(status_code=400, detail="No project documents available to compute health.")

    return latest.get("health_report", {})
