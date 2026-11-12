from app.rag.chunker import DocumentChunker
from app.rag.embedder import Embedder
from app.rag.vector_store import VectorStore
from app.rag.retriever import HybridRetriever
from app.agents.llm_provider import LLMProvider
from app.agents.orchestrator import ProjectIntelligenceOrchestrator
from app.assistant.project_assistant import ProjectIntelligenceAssistant

# Singleton shared services
chunker = DocumentChunker()
embedder = Embedder()
vector_store = VectorStore()
retriever = HybridRetriever(vector_store, embedder)
llm_provider = LLMProvider()
orchestrator = ProjectIntelligenceOrchestrator(vector_store, retriever, llm_provider)
assistant = ProjectIntelligenceAssistant(vector_store, retriever, llm_provider)
