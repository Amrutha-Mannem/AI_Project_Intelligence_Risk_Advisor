import uuid
from typing import List
from app.models.document import DocumentChunk, DocumentMetadata
from app.config import settings


class DocumentChunker:
    """
    Intelligent recursive project document chunker.
    Preserves semantic boundaries (headings, paragraphs, bullet lists)
    and maintains configurable character overlap to prevent context truncation.
    """

    def __init__(self, chunk_size: int = None, chunk_overlap: int = None):
        self.chunk_size = chunk_size or settings.chunk_size
        self.chunk_overlap = chunk_overlap or settings.chunk_overlap
        self.separators = ["\n\n", "\n### ", "\n## ", "\n# ", "\n- ", "\n", ". ", " "]

    def chunk_document(
        self, text: str, document_id: str, metadata: DocumentMetadata
    ) -> List[DocumentChunk]:
        if not text.strip():
            return []

        raw_splits = self._split_text(text, self.separators)
        chunks: List[DocumentChunk] = []

        current_char = 0
        for idx, chunk_content in enumerate(raw_splits):
            chunk_content = chunk_content.strip()
            if not chunk_content:
                continue

            char_start = text.find(chunk_content, current_char)
            if char_start == -1:
                char_start = current_char
            char_end = char_start + len(chunk_content)
            current_char = max(char_start + 1, current_char)

            chunk = DocumentChunk(
                chunk_id=f"{document_id}_chk_{idx}_{uuid.uuid4().hex[:6]}",
                document_id=document_id,
                source_name=metadata.file_name,
                file_type=metadata.file_type,
                content=chunk_content,
                chunk_index=idx,
                char_start=char_start,
                char_end=char_end,
                metadata={
                    "file_name": metadata.file_name,
                    "file_type": metadata.file_type,
                    "word_count": len(chunk_content.split()),
                    **metadata.custom_metadata,
                },
            )
            chunks.append(chunk)

        return chunks

    def _split_text(self, text: str, separators: List[str]) -> List[str]:
        """
        Recursively splits text into blocks within chunk_size with overlap.
        """
        final_chunks: List[str] = []
        # First split by major separator
        separator = separators[0] if separators else " "
        splits = text.split(separator) if separator in text else [text]

        current_doc: List[str] = []
        total_len = 0

        for s in splits:
            s_len = len(s)
            if s_len > self.chunk_size and len(separators) > 1:
                # Sub-split oversized chunk
                sub_splits = self._split_text(s, separators[1:])
                for sub in sub_splits:
                    if total_len + len(sub) > self.chunk_size and current_doc:
                        doc_str = separator.join(current_doc)
                        final_chunks.append(doc_str)
                        # Overlap
                        current_doc = self._get_overlap_tokens(current_doc, separator)
                        total_len = sum(len(x) for x in current_doc)
                    current_doc.append(sub)
                    total_len += len(sub)
            else:
                if total_len + s_len > self.chunk_size and current_doc:
                    doc_str = separator.join(current_doc)
                    final_chunks.append(doc_str)
                    current_doc = self._get_overlap_tokens(current_doc, separator)
                    total_len = sum(len(x) for x in current_doc)

                current_doc.append(s)
                total_len += s_len

        if current_doc:
            final_chunks.append(separator.join(current_doc))

        return [c for c in final_chunks if c.strip()]

    def _get_overlap_tokens(self, tokens: List[str], separator: str) -> List[str]:
        overlap_tokens: List[str] = []
        current_len = 0
        for token in reversed(tokens):
            if current_len + len(token) <= self.chunk_overlap:
                overlap_tokens.insert(0, token)
                current_len += len(token)
            else:
                break
        return overlap_tokens
