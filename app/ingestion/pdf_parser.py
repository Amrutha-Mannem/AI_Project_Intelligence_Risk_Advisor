import io
from pathlib import Path
from typing import Tuple, List, Dict, Any


def parse_pdf(file_path: Path) -> Tuple[str, Dict[str, Any]]:
    """
    Extracts text and metadata from a PDF file.
    Uses pdfplumber for accurate layout and table extraction,
    with PyPDF2 fallback if needed.
    """
    extracted_text_pages: List[str] = []
    metadata: Dict[str, Any] = {"page_count": 0, "has_tables": False}

    try:
        import pdfplumber
        with pdfplumber.open(file_path) as pdf:
            metadata["page_count"] = len(pdf.pages)
            for idx, page in enumerate(pdf.pages, start=1):
                page_text = page.extract_text() or ""
                # Also check for tables and format them
                tables = page.extract_tables()
                if tables:
                    metadata["has_tables"] = True
                    for table in tables:
                        table_str = "\n".join(
                            [" | ".join([str(cell or "").strip() for cell in row]) for row in table if any(row)]
                        )
                        page_text += f"\n\n[Table Page {idx}]:\n{table_str}\n"

                if page_text.strip():
                    extracted_text_pages.append(f"--- Page {idx} ---\n{page_text.strip()}")
    except Exception as e:
        # PyPDF2 fallback
        import PyPDF2
        with open(file_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            metadata["page_count"] = len(reader.pages)
            for idx, page in enumerate(reader.pages, start=1):
                text = page.extract_text() or ""
                if text.strip():
                    extracted_text_pages.append(f"--- Page {idx} ---\n{text.strip()}")

    full_text = "\n\n".join(extracted_text_pages)
    return full_text, metadata
