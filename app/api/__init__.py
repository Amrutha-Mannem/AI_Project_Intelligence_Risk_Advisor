from fastapi import APIRouter
from app.api.routes_ingest import router as ingest_router
from app.api.routes_rag import router as rag_router
from app.api.routes_agents import router as agents_router
from app.api.routes_health import router as health_router
from app.api.routes_chat import router as chat_router
from app.api.routes_export import router as export_router

api_router = APIRouter()
api_router.include_router(ingest_router)
api_router.include_router(rag_router)
api_router.include_router(agents_router)
api_router.include_router(health_router)
api_router.include_router(chat_router)
api_router.include_router(export_router)

__all__ = ["api_router"]
