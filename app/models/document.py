from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class DocumentMetadata(BaseModel):
    file_name: str
    file_type: str  # 'pdf', 'docx', 'csv', 'txt', 'md'
    file_size_bytes: int
    char_count: int
    word_count: int
    line_count: int
    uploaded_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    custom_metadata: Dict[str, Any] = Field(default_factory=dict)


class DocumentChunk(BaseModel):
    chunk_id: str
    document_id: str
    source_name: str
    file_type: str
    content: str
    chunk_index: int
    char_start: int
    char_end: int
    metadata: Dict[str, Any] = Field(default_factory=dict)


class IngestionResult(BaseModel):
    document_id: str
    file_name: str
    file_type: str
    chunks_created: int
    total_characters: int
    total_words: int
    status: str  # 'success', 'warning', 'error'
    message: str
    preview: Optional[str] = None
