from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from app.rag.vector_store import VectorStore
from app.rag.retriever import HybridRetriever
from app.agents.llm_provider import LLMProvider


class BaseAgent(ABC):
    """
    Abstract Base Agent for the Project Intelligence Pipeline.
    Provides uniform access to RAG knowledge base context,
    LLM invocation, and fallback heuristics.
    """

    def __init__(self, name: str, role: str, vector_store: VectorStore, retriever: HybridRetriever, llm: LLMProvider):
        self.name = name
        self.role = role
        self.vector_store = vector_store
        self.retriever = retriever
        self.llm = llm

    def get_relevant_context(self, queries: List[str], top_k: int = 6) -> str:
        """
        Retrieves grounded chunk excerpts across a set of topic queries.
        Prioritizes user-uploaded documents over sample demo documents.
        """
        import re
        user_chunks = [c for c in self.vector_store.chunks if not c.document_id.startswith("sample_")]
        has_user_docs = len(user_chunks) > 0

        seen_chunks = set()
        context_snippets = []

        for q in queries:
            results = self.retriever.retrieve(q, top_k=top_k)
            for chunk, score, citation in results:
                # If user uploaded documents exist, ONLY include chunks from user uploaded documents!
                if has_user_docs and chunk.document_id.startswith("sample_"):
                    continue
                if chunk.chunk_id not in seen_chunks:
                    seen_chunks.add(chunk.chunk_id)
                    clean_source = re.sub(r"^doc_[a-f0-9]{8}_", "", chunk.source_name)
                    context_snippets.append(
                        f"--- Source: {clean_source} (Chunk #{chunk.chunk_index}) ---\n{chunk.content}"
                    )

        if not context_snippets and self.vector_store.chunks:
            pool = user_chunks if has_user_docs else self.vector_store.chunks
            for chunk in pool[:8]:
                clean_source = re.sub(r"^doc_[a-f0-9]{8}_", "", chunk.source_name)
                context_snippets.append(
                    f"--- Source: {clean_source} (Chunk #{chunk.chunk_index}) ---\n{chunk.content}"
                )

        return "\n\n".join(context_snippets)

    @abstractmethod
    def run(self, **kwargs) -> Any:
        pass
