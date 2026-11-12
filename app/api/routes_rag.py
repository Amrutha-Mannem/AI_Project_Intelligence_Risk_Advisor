from typing import Dict, Any, List
from fastapi import APIRouter
from pydantic import BaseModel
from app.deps import vector_store, retriever

router = APIRouter(prefix="/api/rag", tags=["RAG Pipeline"])


class SearchRequest(BaseModel):
    query: str
    top_k: int = 5


@router.post("/search")
async def semantic_search(req: SearchRequest):
    results = retriever.retrieve(req.query, top_k=req.top_k)
    return {
        "query": req.query,
        "count": len(results),
        "results": [
            {
                "chunk_id": chunk.chunk_id,
                "document_id": chunk.document_id,
                "source_name": chunk.source_name,
                "file_type": chunk.file_type,
                "score": round(score, 4),
                "excerpt": citation.excerpt,
                "full_content": chunk.content,
                "metadata": chunk.metadata,
            }
            for chunk, score, citation in results
        ],
    }


@router.get("/stats")
async def get_rag_stats() -> Dict[str, Any]:
    return vector_store.get_stats()


@router.get("/chunks")
async def get_all_chunks(limit: int = 100, offset: int = 0):
    chunks = vector_store.get_all_chunks()
    paginated = chunks[offset : offset + limit]
    return {
        "total": len(chunks),
        "limit": limit,
        "offset": offset,
        "chunks": [c.model_dump() for c in paginated],
    }
