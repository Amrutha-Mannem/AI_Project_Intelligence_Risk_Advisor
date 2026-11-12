from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class Citation(BaseModel):
    document_name: str
    chunk_id: str
    score: float
    excerpt: str
    file_type: str


class ChatQuery(BaseModel):
    query: str
    top_k: int = 5
    conversation_history: List[Dict[str, str]] = Field(default_factory=list)


class ChatResponse(BaseModel):
    query: str
    answer: str
    citations: List[Citation]
    confidence_score: float
    suggested_followups: List[str]
