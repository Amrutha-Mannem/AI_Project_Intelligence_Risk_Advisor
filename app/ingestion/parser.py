from pathlib import Path
from typing import Tuple, Dict, Any
import re
from app.models.document import DocumentMetadata
from app.ingestion.pdf_parser import parse_pdf
from app.ingestion.docx_parser import parse_docx
from app.ingestion.csv_parser import parse_csv
from app.ingestion.text_parser import parse_text


class DocumentParser:
    """
    Unified ingestion parser supporting PDF, DOCX, CSV, TXT, and MD files.
    Extracts text content, normalizes spacing, and extracts statistical metadata.
    """

    SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".csv", ".txt", ".md"}

    @classmethod
    def is_supported(cls, file_path: Path) -> bool:
        return file_path.suffix.lower() in cls.SUPPORTED_EXTENSIONS

    @classmethod
    def parse(cls, file_path: Path) -> Tuple[str, DocumentMetadata]:
        ext = file_path.suffix.lower()

        if ext == ".pdf":
            raw_text, custom_meta = parse_pdf(file_path)
            file_type = "pdf"
        elif ext == ".docx":
            raw_text, custom_meta = parse_docx(file_path)
            file_type = "docx"
        elif ext == ".csv":
            raw_text, custom_meta = parse_csv(file_path)
            file_type = "csv"
        elif ext in {".txt", ".md"}:
            raw_text, custom_meta = parse_text(file_path)
            file_type = "md" if ext == ".md" else "txt"
        else:
            raise ValueError(f"Unsupported file extension: {ext}. Supported: {cls.SUPPORTED_EXTENSIONS}")

        # Clean up excess whitespace while preserving paragraph breaks
        cleaned_text = re.sub(r"\r\n", "\n", raw_text)
        cleaned_text = re.sub(r"\n{3,}", "\n\n", cleaned_text).strip()

        words = cleaned_text.split()
        lines = cleaned_text.splitlines()

        meta = DocumentMetadata(
            file_name=file_path.name,
            file_type=file_type,
            file_size_bytes=file_path.stat().st_size if file_path.exists() else len(raw_text.encode("utf-8")),
            char_count=len(cleaned_text),
            word_count=len(words),
            line_count=len(lines),
            custom_metadata=custom_meta,
        )

        return cleaned_text, meta
