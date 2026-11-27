from typing import Dict, Any, List
from fastapi import APIRouter
from pydantic import BaseModel
from app.deps import vector_store, retriever

router = APIRouter(prefix="/api/rag", tags=["RAG Pipeline"])


class SearchRequest(BaseModel):
    query: str
    top_k: int = 5


@router.post("/query")
@router.post("/search")
async def rag_query(req: SearchRequest):
    if len(vector_store.chunks) == 0:
        return {"results": [], "total": 0, "query": req.query}

    results = retriever.retrieve(req.query, top_k=req.top_k)
    return {
        "query": req.query,
        "total": len(results),
        "results": [
            {
                "chunk_id":    chunk.chunk_id,
                "source_name": chunk.source_name,
                "file_type":   chunk.file_type,
                "chunk_index": chunk.chunk_index,
                "excerpt":     chunk.content[:350] + ("..." if len(chunk.content) > 350 else ""),
                "score":       round(float(score), 4),
            }
            for chunk, score, _citation in results
        ],
    }


@router.get("/stats")
async def rag_stats():
    return vector_store.get_stats()
