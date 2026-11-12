from pathlib import Path
from typing import Tuple, Dict, Any, List
import pandas as pd


def parse_csv(file_path: Path) -> Tuple[str, Dict[str, Any]]:
    """
    Parses CSV files (e.g., task backlogs, sprint status, issue trackers)
    into structured textual representations optimized for RAG chunking and vector search.
    """
    # Detect delimiter
    try:
        df = pd.read_csv(file_path)
    except Exception:
        df = pd.read_csv(file_path, sep=None, engine="python")

    total_rows = len(df)
    columns = [str(c).strip() for c in df.columns]

    lines: List[str] = [
        f"# Tabular Project Artifact: {file_path.name}",
        f"Total Records: {total_rows}",
        f"Columns: {', '.join(columns)}",
        "\n--- Row Records ---",
    ]

    for idx, row in df.iterrows():
        row_fields = []
        for col in columns:
            val = row[col]
            if pd.notna(val) and str(val).strip():
                row_fields.append(f"{col}: {str(val).strip()}")
        if row_fields:
            lines.append(f"Row {idx + 1} -> " + " | ".join(row_fields))

    metadata = {
        "total_rows": total_rows,
        "column_count": len(columns),
        "columns": columns,
    }

    full_text = "\n".join(lines)
    return full_text, metadata
