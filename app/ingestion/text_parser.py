from pathlib import Path
from typing import Tuple, Dict, Any


def parse_text(file_path: Path) -> Tuple[str, Dict[str, Any]]:
    """
    Parses plain text (.txt) and Markdown (.md) documents,
    extracting clean content and line/structure metadata.
    """
    encodings = ["utf-8", "utf-8-sig", "latin-1", "cp1252"]
    content = ""
    used_encoding = "utf-8"

    for enc in encodings:
        try:
            with open(file_path, "r", encoding=enc) as f:
                content = f.read()
            used_encoding = enc
            break
        except UnicodeDecodeError:
            continue

    metadata = {
        "encoding": used_encoding,
        "is_markdown": file_path.suffix.lower() == ".md",
    }

    return content, metadata
