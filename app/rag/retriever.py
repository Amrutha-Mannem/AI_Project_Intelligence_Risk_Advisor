import re
from typing import List, Tuple
from app.models.chat import Citation
from app.models.document import DocumentChunk
from app.rag.embedder import Embedder
from app.rag.vector_store import VectorStore


class HybridRetriever:
    """
    Hybrid Retriever combining dense semantic vector search with
    lexical keyword scoring for robust technical terminology retrieval.
    """

    def __init__(self, vector_store: VectorStore, embedder: Embedder):
        self.vector_store = vector_store
        self.embedder = embedder

    def retrieve(self, query: str, top_k: int = 5) -> List[Tuple[DocumentChunk, float, Citation]]:
        if not query.strip() or len(self.vector_store.chunks) == 0:
            return []

        # 1. Dense Semantic Search
        query_vec = self.embedder.embed_query(query)
        # Retrieve a broader pool for reranking
        pool_size = min(len(self.vector_store.chunks), max(top_k * 3, 10))
        semantic_results = self.vector_store.search(query_vec, top_k=pool_size)

        # 2. Lexical keyword boost
        query_tokens = set(re.findall(r"\w+", query.lower()))
        reranked_results = []

        for chunk, sem_score in semantic_results:
            chunk_tokens = set(re.findall(r"\w+", chunk.content.lower()))
            overlap = len(query_tokens.intersection(chunk_tokens))
            lexical_score = overlap / max(len(query_tokens), 1)

            # Combined score: 70% semantic + 30% lexical keyword overlap
            hybrid_score = (0.7 * max(sem_score, 0.0)) + (0.3 * lexical_score)
            reranked_results.append((chunk, hybrid_score))

        # Sort by hybrid score descending
        reranked_results.sort(key=lambda x: x[1], reverse=True)
        top_results = reranked_results[:top_k]

        citations: List[Tuple[DocumentChunk, float, Citation]] = []
        for chunk, score in top_results:
            # Create a concise excerpt (first 240 chars or surrounding key sentence)
            excerpt = chunk.content[:240].strip()
            if len(chunk.content) > 240:
                excerpt += "..."

            citation = Citation(
                document_name=chunk.source_name,
                chunk_id=chunk.chunk_id,
                score=round(float(score), 4),
                excerpt=excerpt,
                file_type=chunk.file_type,
            )
            citations.append((chunk, score, citation))

        return citations
