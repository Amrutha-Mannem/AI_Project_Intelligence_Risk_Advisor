import os
import pytest
from pathlib import Path
from app.ingestion.parser import DocumentParser
from app.config import settings

SAMPLES_DIR = settings.samples_dir


def test_parser_supported_extensions():
    assert DocumentParser.is_supported(Path("test.pdf"))
    assert DocumentParser.is_supported(Path("test.docx"))
    assert DocumentParser.is_supported(Path("test.csv"))
    assert DocumentParser.is_supported(Path("test.txt"))
    assert DocumentParser.is_supported(Path("test.md"))
    assert not DocumentParser.is_supported(Path("test.exe"))


def test_parse_meeting_notes():
    path = SAMPLES_DIR / "sprint_meeting_notes.txt"
    assert path.exists(), "Sample meeting notes should exist"
    text, meta = DocumentParser.parse(path)
    assert len(text) > 0
    assert meta.file_type == "txt"
    assert meta.word_count > 50
    assert "Sprint 3" in text


def test_parse_tasks_csv():
    path = SAMPLES_DIR / "tasks_backlog.csv"
    assert path.exists(), "Sample tasks backlog should exist"
    text, meta = DocumentParser.parse(path)
    assert len(text) > 0
    assert meta.file_type == "csv"
    assert "TSK-101" in text
    assert meta.custom_metadata.get("total_rows", 0) >= 10


def test_parse_progress_md():
    path = SAMPLES_DIR / "progress_update.md"
    assert path.exists(), "Sample progress update should exist"
    text, meta = DocumentParser.parse(path)
    assert len(text) > 0
    assert meta.file_type == "md"
    assert "Milestone 1" in text


def test_parse_srs_docx():
    path = SAMPLES_DIR / "srs_specifications.docx"
    assert path.exists(), "Sample SRS docx should exist"
    text, meta = DocumentParser.parse(path)
    assert len(text) > 0
    assert meta.file_type == "docx"
    assert "System Requirements Specification" in text


def test_parse_proposal_pdf():
    path = SAMPLES_DIR / "proposal_project.pdf"
    assert path.exists(), "Sample proposal PDF should exist"
    text, meta = DocumentParser.parse(path)
    assert len(text) > 0
    assert meta.file_type == "pdf"
    assert "AI Project Intelligence" in text
