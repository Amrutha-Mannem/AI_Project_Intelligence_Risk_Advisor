import uuid
import shutil
from pathlib import Path
from typing import List, Dict, Any
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.config import settings
from app.ingestion.parser import DocumentParser
from app.models.document import IngestionResult
from app.deps import chunker, embedder, vector_store, orchestrator

router = APIRouter(prefix="/api/ingest", tags=["Document Ingestion"])


@router.post("/upload", response_model=List[IngestionResult])
async def upload_documents(files: List[UploadFile] = File(...)):
    if not files:
        raise HTTPException(status_code=400, detail="No files provided for upload.")

    results: List[IngestionResult] = []

    for file in files:
        ext = Path(file.filename).suffix.lower()
        if ext not in DocumentParser.SUPPORTED_EXTENSIONS:
            results.append(
                IngestionResult(
                    document_id="",
                    file_name=file.filename,
                    file_type=ext.replace(".", ""),
                    chunks_created=0,
                    total_characters=0,
                    total_words=0,
                    status="error",
                    message=f"Unsupported format {ext}. Supported: {list(DocumentParser.SUPPORTED_EXTENSIONS)}",
                )
            )
            continue

        doc_id = f"doc_{uuid.uuid4().hex[:8]}"
        saved_path = settings.upload_dir / f"{doc_id}_{file.filename}"

        # Clean user-facing file name
        clean_name = file.filename

        try:
            # Save uploaded file
            with open(saved_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            # Parse document
            raw_text, metadata = DocumentParser.parse(saved_path)
            metadata.file_name = clean_name

            # Chunk document and assign clean source name
            chunks = chunker.chunk_document(raw_text, document_id=doc_id, metadata=metadata)
            for c in chunks:
                c.source_name = clean_name

            # Automatically clear any demo sample files so they don't contaminate the real project
            sample_ids = [c.document_id for c in vector_store.chunks if c.document_id.startswith("sample_")]
            for s_id in set(sample_ids):
                vector_store.delete_document(s_id)

            if chunks:
                chunk_texts = [c.content for c in chunks]
                embeddings = embedder.embed_documents(chunk_texts)
                vector_store.add_chunks(chunks, embeddings)

            results.append(
                IngestionResult(
                    document_id=doc_id,
                    file_name=clean_name,
                    file_type=metadata.file_type,
                    chunks_created=len(chunks),
                    total_characters=metadata.char_count,
                    total_words=metadata.word_count,
                    status="success",
                    message=f"Successfully parsed and indexed {len(chunks)} chunks.",
                    preview=raw_text[:200] + "..." if len(raw_text) > 200 else raw_text,
                )
            )
        except Exception as e:
            results.append(
                IngestionResult(
                    document_id=doc_id,
                    file_name=file.filename,
                    file_type=ext.replace(".", ""),
                    chunks_created=0,
                    total_characters=0,
                    total_words=0,
                    status="error",
                    message=f"Parsing error: {str(e)}",
                )
            )

    # Invalidate cached analysis so next run is strictly on the new documents
    if any(r.status == "success" for r in results):
        orchestrator.last_analysis = None

    return results


@router.post("/load-samples", response_model=List[IngestionResult])
async def load_sample_documents():
    """
    Loads all sample project artifacts from the samples directory into the knowledge base.
    """
    sample_files = list(settings.samples_dir.glob("*.*"))
    supported_samples = [f for f in sample_files if DocumentParser.is_supported(f)]

    if not supported_samples:
        raise HTTPException(status_code=404, detail="No sample files found in samples directory.")

    results: List[IngestionResult] = []

    for file_path in supported_samples:
        doc_id = f"sample_{file_path.stem[:12]}"
        # Avoid duplicate indexing if already indexed
        existing = [c for c in vector_store.chunks if c.document_id == doc_id]
        if existing:
            results.append(
                IngestionResult(
                    document_id=doc_id,
                    file_name=file_path.name,
                    file_type=file_path.suffix.replace(".", ""),
                    chunks_created=len(existing),
                    total_characters=sum(len(c.content) for c in existing),
                    total_words=sum(len(c.content.split()) for c in existing),
                    status="success",
                    message="Already indexed in knowledge base.",
                )
            )
            continue

        try:
            raw_text, metadata = DocumentParser.parse(file_path)
            chunks = chunker.chunk_document(raw_text, document_id=doc_id, metadata=metadata)
            if chunks:
                chunk_texts = [c.content for c in chunks]
                embeddings = embedder.embed_documents(chunk_texts)
                vector_store.add_chunks(chunks, embeddings)

            results.append(
                IngestionResult(
                    document_id=doc_id,
                    file_name=file_path.name,
                    file_type=metadata.file_type,
                    chunks_created=len(chunks),
                    total_characters=metadata.char_count,
                    total_words=metadata.word_count,
                    status="success",
                    message=f"Successfully indexed sample ({len(chunks)} chunks).",
                    preview=raw_text[:200] + "..." if len(raw_text) > 200 else raw_text,
                )
            )
        except Exception as e:
            results.append(
                IngestionResult(
                    document_id=doc_id,
                    file_name=file_path.name,
                    file_type=file_path.suffix.replace(".", ""),
                    chunks_created=0,
                    total_characters=0,
                    total_words=0,
                    status="error",
                    message=f"Error indexing sample: {str(e)}",
                )
            )

    return results


@router.get("/documents")
async def list_documents() -> List[Dict[str, Any]]:
    """
    Returns summarized list of distinct documents indexed in the vector store.
    If user has uploaded documents, sample demo files are excluded from the web interface.
    """
    user_chunks = [c for c in vector_store.chunks if not c.document_id.startswith("sample_")]
    target_chunks = user_chunks if len(user_chunks) > 0 else vector_store.chunks

    doc_map: Dict[str, Dict[str, Any]] = {}
    for chunk in target_chunks:
        d_id = chunk.document_id
        if d_id not in doc_map:
            clean_name = re.sub(r"^doc_[a-f0-9]{8}_", "", chunk.source_name)
            doc_map[d_id] = {
                "document_id": d_id,
                "file_name": clean_name,
                "file_type": chunk.file_type,
                "chunks_count": 0,
                "total_chars": 0,
                "total_words": 0,
                "is_sample": d_id.startswith("sample_"),
            }
        doc_map[d_id]["chunks_count"] += 1
        doc_map[d_id]["total_chars"] += len(chunk.content)
        doc_map[d_id]["total_words"] += len(chunk.content.split())

    return list(doc_map.values())


@router.delete("/documents/{document_id}")
async def delete_document(document_id: str):
    removed = vector_store.delete_document(document_id)
    if removed == 0:
        raise HTTPException(status_code=404, detail="Document not found in vector index.")
    orchestrator.last_analysis = None
    return {"status": "success", "message": f"Deleted {removed} chunks for document {document_id}"}


@router.post("/clear")
@router.delete("/clear")
async def clear_all_documents():
    vector_store.clear()
    orchestrator.last_analysis = None
    return {"status": "success", "message": "Cleared all documents and vector indices."}
