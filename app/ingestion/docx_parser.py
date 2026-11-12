from pathlib import Path
from typing import Tuple, Dict, Any, List
import docx


def parse_docx(file_path: Path) -> Tuple[str, Dict[str, Any]]:
    """
    Extracts text and structure from a DOCX file including
    headings, paragraphs, bullet points, and tables.
    """
    doc = docx.Document(file_path)
    content_blocks: List[str] = []
    heading_count = 0
    paragraph_count = 0
    table_count = len(doc.tables)

    for p in doc.paragraphs:
        text = p.text.strip()
        if not text:
            continue

        style_name = p.style.name.lower() if p.style else ""
        if "heading" in style_name:
            heading_count += 1
            content_blocks.append(f"\n### {text}\n")
        elif "list" in style_name or "bullet" in style_name:
            content_blocks.append(f"- {text}")
        else:
            paragraph_count += 1
            content_blocks.append(text)

    # Process tables in DOCX
    for table_idx, table in enumerate(doc.tables, start=1):
        table_rows: List[str] = []
        for row in table.rows:
            row_cells = [cell.text.strip().replace("\n", " ") for cell in row.cells]
            if any(row_cells):
                table_rows.append(" | ".join(row_cells))
        if table_rows:
            content_blocks.append(f"\n[Table {table_idx}]:\n" + "\n".join(table_rows) + "\n")

    metadata = {
        "heading_count": heading_count,
        "paragraph_count": paragraph_count,
        "table_count": table_count,
    }

    full_text = "\n\n".join(content_blocks)
    return full_text, metadata
