import json
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any
import numpy as np
from app.models.document import DocumentChunk
from app.config import settings


class VectorStore:
    """
    Self-contained, persistent Vector Store utilizing optimized NumPy matrix operations.
    Guarantees zero-lock conflicts, cross-platform persistence, and instant cosine similarity search.
    """

    def __init__(self, index_dir: Path = None):
        self.index_dir = index_dir or settings.index_dir
        self.metadata_file = self.index_dir / "chunks_metadata.json"
        self.embeddings_file = self.index_dir / "embeddings.npy"

        self.chunks: List[DocumentChunk] = []
        self.embeddings: Optional[np.ndarray] = None
        self.load()

    def add_chunks(self, chunks: List[DocumentChunk], embeddings: np.ndarray):
        if not chunks:
            return

        embeddings = np.array(embeddings, dtype=np.float32)

        # Ensure normalized vectors for unit-length cosine similarity
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        normalized_embeddings = embeddings / norms

        if self.embeddings is None or len(self.chunks) == 0:
            self.embeddings = normalized_embeddings
            self.chunks = list(chunks)
        else:
            self.embeddings = np.vstack([self.embeddings, normalized_embeddings])
            self.chunks.extend(chunks)

        self.save()

    def search(
        self,
        query_vector: np.ndarray,
        top_k: int = 5,
        filter_meta: Optional[Dict[str, Any]] = None,
    ) -> List[Tuple[DocumentChunk, float]]:
        if self.embeddings is None or len(self.chunks) == 0:
            return []

        query_vec = np.array(query_vector, dtype=np.float32).flatten()
        q_norm = np.linalg.norm(query_vec)
        if q_norm > 0:
            query_vec = query_vec / q_norm

        # Cosine similarity dot product
        similarities = np.dot(self.embeddings, query_vec)

        # Apply optional metadata filtering
        ranked_indices = np.argsort(similarities)[::-1]
        results: List[Tuple[DocumentChunk, float]] = []

        for idx in ranked_indices:
            chunk = self.chunks[idx]
            score = float(similarities[idx])

            if filter_meta:
                match = True
                for k, v in filter_meta.items():
                    if getattr(chunk, k, None) != v and chunk.metadata.get(k) != v:
                        match = False
                        break
                if not match:
                    continue

            results.append((chunk, score))
            if len(results) >= top_k:
                break

        return results

    def delete_document(self, document_id: str) -> int:
        if not self.chunks or self.embeddings is None:
            return 0

        keep_indices = [i for i, c in enumerate(self.chunks) if c.document_id != document_id]
        removed_count = len(self.chunks) - len(keep_indices)

        if removed_count > 0:
            self.chunks = [self.chunks[i] for i in keep_indices]
            if len(self.chunks) > 0:
                self.embeddings = self.embeddings[keep_indices]
            else:
                self.embeddings = None
            self.save()

        return removed_count

    def clear(self):
        self.chunks = []
        self.embeddings = None
        if self.metadata_file.exists():
            self.metadata_file.unlink()
        if self.embeddings_file.exists():
            self.embeddings_file.unlink()

    def save(self):
        self.index_dir.mkdir(parents=True, exist_ok=True)
        chunks_data = [chunk.model_dump() for chunk in self.chunks]
        with open(self.metadata_file, "w", encoding="utf-8") as f:
            json.dump(chunks_data, f, indent=2)

        if self.embeddings is not None and len(self.embeddings) > 0:
            np.save(self.embeddings_file, self.embeddings)

    def load(self):
        if self.metadata_file.exists() and self.embeddings_file.exists():
            try:
                with open(self.metadata_file, "r", encoding="utf-8") as f:
                    chunks_data = json.load(f)
                self.chunks = [DocumentChunk(**item) for item in chunks_data]
                self.embeddings = np.load(self.embeddings_file)
            except Exception as e:
                print(f"[VectorStore] Failed to load existing index: {e}. Starting fresh.")
                self.chunks = []
                self.embeddings = None

    def get_stats(self) -> Dict[str, Any]:
        doc_ids = {c.document_id for c in self.chunks}
        file_names = {c.source_name for c in self.chunks}
        return {
            "total_chunks": len(self.chunks),
            "total_documents": len(doc_ids),
            "indexed_files": list(file_names),
            "vector_dimension": self.embeddings.shape[1] if self.embeddings is not None else 0,
        }

    def get_all_chunks(self) -> List[DocumentChunk]:
        return list(self.chunks)
