import pytest
from app.rag.chunker import DocumentChunker
from app.rag.embedder import Embedder
from app.rag.vector_store import VectorStore
from app.rag.retriever import HybridRetriever
from app.models.document import DocumentMetadata


def test_chunker_basic():
    chunker = DocumentChunker(chunk_size=150, chunk_overlap=30)
    text = (
        "Project Management Intelligence Platform.\n\n"
        "Deliverables include PDF ingestion, DOCX parsing, and CSV backlog tracking.\n\n"
        "The RAG pipeline provides semantic vector similarity matching and grounded citations."
    )
    meta = DocumentMetadata(
        file_name="test.txt",
        file_type="txt",
        file_size_bytes=len(text),
        char_count=len(text),
        word_count=len(text.split()),
        line_count=3,
    )
    chunks = chunker.chunk_document(text, "doc_test_1", meta)
    assert len(chunks) >= 2
    for c in chunks:
        assert c.document_id == "doc_test_1"
        assert len(c.content) > 0


def test_embedder_and_vector_store(tmp_path):
    embedder = Embedder()
    store = VectorStore(index_dir=tmp_path)
    store.clear()

    chunker = DocumentChunker(chunk_size=200, chunk_overlap=40)
    doc_text = "The system handles risk forecasts and blocker identification using multi-agent pipelines."
    meta = DocumentMetadata(
        file_name="spec.txt",
        file_type="txt",
        file_size_bytes=len(doc_text),
        char_count=len(doc_text),
        word_count=len(doc_text.split()),
        line_count=1,
    )
    chunks = chunker.chunk_document(doc_text, "doc_spec_1", meta)
    assert len(chunks) > 0

    chunk_texts = [c.content for c in chunks]
    embeddings = embedder.embed_documents(chunk_texts)
    assert embeddings.shape[0] == len(chunks)
    assert embeddings.shape[1] == 384

    store.add_chunks(chunks, embeddings)
    assert len(store.chunks) == len(chunks)

    # Search
    q_vec = embedder.embed_query("risk forecast")
    results = store.search(q_vec, top_k=2)
    assert len(results) > 0
    top_chunk, score = results[0]
    assert score > 0.0

    # Hybrid Retriever
    retriever = HybridRetriever(store, embedder)
    hybrid_results = retriever.retrieve("risk forecast", top_k=2)
    assert len(hybrid_results) > 0
    c_res, h_score, citation = hybrid_results[0]
    assert citation.document_name == "spec.txt"
    assert citation.score > 0.0
