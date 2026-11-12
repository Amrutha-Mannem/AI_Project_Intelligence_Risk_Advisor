import pytest
from app.deps import orchestrator, vector_store, embedder, chunker
from app.ingestion.parser import DocumentParser
from app.config import settings


@pytest.fixture(scope="module", autouse=True)
def populate_vector_store():
    # Index meeting notes and tasks CSV
    samples = [
        settings.samples_dir / "sprint_meeting_notes.txt",
        settings.samples_dir / "tasks_backlog.csv",
    ]
    for p in samples:
        if p.exists():
            text, meta = DocumentParser.parse(p)
            chunks = chunker.chunk_document(text, f"test_{p.stem}", meta)
            embeddings = embedder.embed_documents([c.content for c in chunks])
            vector_store.add_chunks(chunks, embeddings)


def test_scope_agent():
    report = orchestrator.scope_agent.run()
    assert report.project_title
    assert len(report.in_scope_items) > 0
    assert len(report.key_deliverables) > 0


def test_risk_forecast_agent():
    risks, forecast = orchestrator.risk_agent.run()
    assert len(risks) > 0
    assert forecast.forecast_status in ["On Track", "At Risk", "Critical Delay"]
    assert isinstance(forecast.predicted_delay_days, int)


def test_blocker_action_agent():
    blockers, action_items = orchestrator.blocker_agent.run()
    assert len(blockers) > 0
    assert len(action_items) > 0
    assert blockers[0].severity in ["critical", "high", "medium", "low"]


def test_doc_generator_agent():
    bundle = orchestrator.doc_agent.run()
    assert len(bundle.user_stories) > 0
    assert len(bundle.missing_documentation_gaps) > 0
    story = bundle.user_stories[0]
    assert story.as_a and story.i_want_to and story.so_that


def test_health_scorer_algorithm():
    analysis = orchestrator.run_full_pipeline()
    health = analysis["health_report"]
    assert 0.0 <= health["overall_score"] <= 100.0
    assert "health_grade" in health
    assert len(health["categories"]) == 5
    assert "Planning" in health["radar_metrics"]
