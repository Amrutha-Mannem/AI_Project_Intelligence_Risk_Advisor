import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_root_index():
    response = client.get("/")
    assert response.status_code == 200
    assert "AI Project Intelligence & Risk Advisor" in response.text


def test_system_status():
    response = client.get("/api/export/status")
    assert response.status_code == 200
    data = response.json()
    assert "active_provider" in data


def test_rag_stats():
    response = client.get("/api/rag/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_chunks" in data


def test_chat_query():
    payload = {"query": "What are the project blockers?", "top_k": 3}
    response = client.post("/api/chat/query", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert isinstance(data["citations"], list)
    assert isinstance(data["suggested_followups"], list)


def test_export_markdown():
    response = client.get("/api/export/markdown")
    # If analysis has been run, returns markdown
    if response.status_code == 200:
        assert "# AI Project Intelligence & Risk Advisor Report" in response.text
