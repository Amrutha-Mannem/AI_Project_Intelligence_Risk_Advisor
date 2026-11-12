import os
from pathlib import Path
import docx
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

SAMPLES_DIR = Path(__file__).resolve().parent

def create_meeting_notes():
    txt_content = """# Sprint 3 Retrospective & Standup Meeting Notes
Date: 2026-11-10
Attendees: Sarah (Tech Lead), David (Frontend), Priya (Backend), Alex (ML/Data), Elena (Product Owner)

## Executive Summary
The team reviewed progress on the Unified Project Intelligence Platform. While the Core Ingestion and Text Parsers are ahead of schedule, the RAG embedding vector store and third-party LLM quota management are experiencing friction.

## Sprint Blockers & Critical Impediments
- BLOCKER: Alex reported that external third-party API rate limits (HTTP 429) are causing vector batch embedding failures during load testing. Currently blocking RAG Pipeline Milestone 1 verification.
  - Action: Implement local embeddings fallback (SentenceTransformers MiniLM) and request an enterprise API tier.
  - Owner: Alex | Priority: Critical
- BLOCKER: Frontend team waiting on API contract specifications for the conversational assistant citations modal.
  - Action: Priya to publish OpenAPI schema and Swagger specs by Wednesday.
  - Owner: Priya | Priority: High

## Delivery & Milestone Challenges
- Target Milestone 1 delivery is set for Week 2.
- Due to API rate limit troubleshooting, schedule variance has slipped by an estimated 5 days.
- If Alex cannot resolve the embeddings batching by Friday, Milestone 1 sign-off will slip to Week 3.

## Decisions Made
1. Out of Scope for Phase 1: Native iOS/Android mobile apps and direct SAP/Oracle ERP integration are explicitly deferred to Phase 2.
2. We must enforce Definition of Ready (DoR) on all user stories prior to implementation.
3. Every API endpoint must return clickable citation references grounded in the uploaded artifacts.

## Action Items
1. ACT-01: Alex to integrate offline Scikit-Learn TF-IDF / SentenceTransformer fallback for embedding pipeline. (Due: Nov 14)
2. ACT-02: Priya to implement Pydantic validation schemas for ChatQuery and IngestionResult. (Due: Nov 13)
3. ACT-03: David to build glassmorphism UI with radar chart for Project Health metrics. (Due: Nov 15)
4. ACT-04: Elena to conduct backlog grooming for Documentation Generation user stories. (Due: Nov 16)
"""
    with open(SAMPLES_DIR / "sprint_meeting_notes.txt", "w", encoding="utf-8") as f:
        f.write(txt_content)
    print("Created sprint_meeting_notes.txt")


def create_tasks_csv():
    data = [
        {"Task_ID": "TSK-101", "Module": "Ingestion", "Title": "Develop PDF, DOCX, CSV parsers", "Assignee": "Priya", "Status": "Completed", "Priority": "High", "Est_Days": 3, "Due_Date": "2026-11-05"},
        {"Task_ID": "TSK-102", "Module": "RAG Pipeline", "Title": "Implement Document Chunker with Overlap", "Assignee": "Alex", "Status": "Completed", "Priority": "High", "Est_Days": 2, "Due_Date": "2026-11-07"},
        {"Task_ID": "TSK-103", "Module": "RAG Pipeline", "Title": "Embeddings generation & Vector Store indexing", "Assignee": "Alex", "Status": "Blocked", "Priority": "Critical", "Est_Days": 4, "Due_Date": "2026-11-10"},
        {"Task_ID": "TSK-104", "Module": "Multi-Agent", "Title": "Scope & Deliverable Extraction Agent", "Assignee": "Sarah", "Status": "In Progress", "Priority": "High", "Est_Days": 3, "Due_Date": "2026-11-12"},
        {"Task_ID": "TSK-105", "Module": "Multi-Agent", "Title": "Risk Detection & Delivery Forecasting Agent", "Assignee": "Sarah", "Status": "In Progress", "Priority": "High", "Est_Days": 3, "Due_Date": "2026-11-13"},
        {"Task_ID": "TSK-106", "Module": "Multi-Agent", "Title": "Blocker & Action Item Identification Agent", "Assignee": "Sarah", "Status": "Todo", "Priority": "Medium", "Est_Days": 2, "Due_Date": "2026-11-14"},
        {"Task_ID": "TSK-107", "Module": "Documentation", "Title": "User Stories and Risk Register Generator", "Assignee": "Elena", "Status": "Todo", "Priority": "Medium", "Est_Days": 3, "Due_Date": "2026-11-16"},
        {"Task_ID": "TSK-108", "Module": "Health Scoring", "Title": "Holistic 100-point Project Health Scorer", "Assignee": "Sarah", "Status": "Todo", "Priority": "High", "Est_Days": 2, "Due_Date": "2026-11-17"},
        {"Task_ID": "TSK-109", "Module": "Assistant", "Title": "Grounded Conversational RAG Assistant", "Assignee": "Priya", "Status": "Todo", "Priority": "Critical", "Est_Days": 4, "Due_Date": "2026-11-19"},
        {"Task_ID": "TSK-110", "Module": "Frontend", "Title": "Interactive Web Dashboard & Health Radar", "Assignee": "David", "Status": "In Progress", "Priority": "High", "Est_Days": 5, "Due_Date": "2026-11-20"},
    ]
    df = pd.DataFrame(data)
    df.to_csv(SAMPLES_DIR / "tasks_backlog.csv", index=False)
    print("Created tasks_backlog.csv")


def create_progress_md():
    md_content = """# Bi-Weekly Sprint Progress Update & Advisory Report
**Project:** AI Project Intelligence & Risk Advisor  
**Reporting Period:** Week 2  
**Overall Status:** Amber / At Risk (Schedule pressure on RAG Vector Store)

## 1. Accomplishments This Period
- Successfully implemented unified document parser supporting PDF, DOCX, CSV, and TXT artifacts.
- Created recursive document chunking engine preserving heading hierarchies and metadata tags.
- Built normalized cosine similarity vector search engine with on-disk index persistence.
- Initialized multi-agent orchestrator scaffolding for scope and risk extraction.

## 2. Schedule Variance & Delivery Challenges
- **Milestone 1 Completion:** Currently tracking 4 days behind original schedule due to external API throttling during embedding generation.
- **Critical Path Bottleneck:** Alex is currently the sole engineer working on vector store indexing (Key-Person Dependency). Cross-training Priya to co-own vector indexing.
- **Forecast:** Estimated delivery slip of 5 to 7 days if external API quota is not supplemented with local models.

## 3. High-Priority Risks Identified
1. **API Rate Limiting & Latency Spikes (Severity 20/25):** Third-party LLM providers experiencing intermittent throttling under bulk document load.
2. **Missing Test Automation Suite (Severity 15/25):** No automated regression testing currently verifies PDF table parsing fidelity.
3. **Requirement Drift in Health Scoring (Severity 12/25):** Stakeholders debating subjective vs objective weights for health score calculation.

## 4. Key Decisions & Out-of-Scope Confirmations
- Out of scope: Direct Jira Cloud webhook bi-directional synchronization deferred to Phase 2.
- In-Scope: Instant one-click Markdown & JSON report export for sprint retrospectives.
"""
    with open(SAMPLES_DIR / "progress_update.md", "w", encoding="utf-8") as f:
        f.write(md_content)
    print("Created progress_update.md")


def create_srs_docx():
    doc = docx.Document()
    doc.add_heading("System Requirements Specification (SRS)", 0)
    doc.add_paragraph("Project: AI Project Intelligence & Risk Advisor")
    doc.add_paragraph("Author: Systems Architecture Team | Version: 1.0")

    doc.add_heading("1. Project Scope & Purpose", level=1)
    doc.add_paragraph(
        "Software engineering teams and academic project groups suffer from fragmented planning, undetected schedule risks, and missing documentation. "
        "The objective is to establish an intelligent, multi-agent platform where teams upload project artifacts (PDF, DOCX, CSV, TXT) and receive automated "
        "scope extraction, risk forecasts, blocker resolutions, and an interactive grounded conversational assistant."
    )

    doc.add_heading("2. In-Scope Modules & Deliverables", level=1)
    doc.add_paragraph("- DEL-01: Document Ingestion Pipeline supporting PDF, DOCX, CSV, and plain text.")
    doc.add_paragraph("- DEL-02: RAG Pipeline with recursive chunking, dense vector embeddings, and persistent indexing.")
    doc.add_paragraph("- DEL-03: Scope and Deliverable Extraction Agent for automated boundary mapping.")
    doc.add_paragraph("- DEL-04: Risk Detection & Delivery Forecasting Agent computing quantitative severity scores.")
    doc.add_paragraph("- DEL-05: Blocker and Action Item Identification Agent for sprint impediments.")
    doc.add_paragraph("- DEL-06: Documentation Generation Agent producing User Stories with Acceptance Criteria.")
    doc.add_paragraph("- DEL-07: Holistic 100-Point Project Health Scoring Algorithm with category breakdowns.")
    doc.add_paragraph("- DEL-08: Conversational Project Intelligence Assistant grounded strictly in uploaded documents.")

    doc.add_heading("3. Explicit Out-of-Scope Items", level=1)
    doc.add_paragraph("- OOS-01: Native mobile applications (iOS and Android); web dashboard is fully responsive.")
    doc.add_paragraph("- OOS-02: Direct real-time bidirectional syncing with enterprise SAP/Oracle ERP databases.")

    doc.add_heading("4. Non-Functional & Security Requirements", level=1)
    doc.add_paragraph("- Retrieval latency must remain under 1.5 seconds for semantic vector queries.")
    doc.add_paragraph("- System must function seamlessly offline using local embeddings and heuristic agents when API keys are not supplied.")

    table = doc.add_table(rows=1, cols=3)
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = "Milestone"
    hdr_cells[1].text = "Deliverables"
    hdr_cells[2].text = "Target Timeline"

    row_data = [
        ("Milestone 1", "RAG Pipeline & Multi-Format Ingestion", "Week 1 - 2"),
        ("Milestone 2", "Multi-Agent Risk & Scope Extraction", "Week 3"),
        ("Milestone 3", "Interactive Dashboard & Health Scoring", "Week 4"),
    ]
    for m, d, t in row_data:
        row = table.add_row().cells
        row[0].text = m
        row[1].text = d
        row[2].text = t

    doc.save(SAMPLES_DIR / "srs_specifications.docx")
    print("Created srs_specifications.docx")


def create_proposal_pdf():
    pdf_path = SAMPLES_DIR / "proposal_project.pdf"
    doc = SimpleDocTemplate(str(pdf_path), pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    title_style = ParagraphStyle(
        "TitleStyle",
        parent=styles["Heading1"],
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#1e293b"),
        spaceAfter=12,
    )
    h2_style = ParagraphStyle(
        "H2Style",
        parent=styles["Heading2"],
        fontSize=14,
        leading=18,
        textColor=colors.HexColor("#3b82f6"),
        spaceBefore=12,
        spaceAfter=6,
    )
    body_style = ParagraphStyle(
        "BodyStyle",
        parent=styles["Normal"],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#334155"),
        spaceAfter=8,
    )

    story.append(Paragraph("AI Project Intelligence & Risk Advisor - Project Proposal", title_style))
    story.append(Paragraph("<b>Target Domain:</b> Software Development & Team Collaboration Intelligence", body_style))
    story.append(Spacer(1, 10))

    story.append(Paragraph("1. Executive Summary & Problem Statement", h2_style))
    story.append(Paragraph(
        "Modern development teams face fragmented artifacts across chat notes, SRS documents, and task lists. "
        "Manually synthesizing these artifacts leads to reactive management, unspotted blockers, and missed delivery milestones. "
        "This project proposes an AI Project Intelligence & Risk Advisor powered by RAG and a multi-agent pipeline.",
        body_style
    ))

    story.append(Paragraph("2. Strategic Objectives", h2_style))
    story.append(Paragraph("• Construct a unified project knowledge base accepting PDF, DOCX, CSV, and plain text artifacts.", body_style))
    story.append(Paragraph("• Automatically extract project scope boundaries, risks, blockers, and deliverable roadmaps.", body_style))
    story.append(Paragraph("• Calculate an objective 100-point project health score across 5 vital dimensions.", body_style))
    story.append(Paragraph("• Deliver a conversational assistant grounded with verifiable source document citations.", body_style))

    story.append(Paragraph("3. Preliminary Risk Assessment", h2_style))
    risk_data = [
        ["Risk ID", "Risk Description", "Category", "Probability", "Impact", "Mitigation"],
        ["RSK-01", "Third-party LLM API rate limits", "Dependency", "High", "High", "Local SentenceTransformers fallback"],
        ["RSK-02", "Single developer bottleneck on vector indexing", "Resource", "Medium", "High", "Cross-train backend engineers"],
        ["RSK-03", "Incomplete acceptance criteria in meeting notes", "Scope", "Medium", "Medium", "Agile User Story Generator Agent"],
    ]
    t = Table(risk_data, colWidths=[50, 160, 60, 60, 50, 130])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 8),
        ("FONTSIZE", (0, 1), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    story.append(t)

    doc.build(story)
    print("Created proposal_project.pdf")


if __name__ == "__main__":
    create_meeting_notes()
    create_tasks_csv()
    create_progress_md()
    create_srs_docx()
    create_proposal_pdf()
    print("ALL 5 SAMPLE ARTIFACTS GENERATED SUCCESSFULLY!")
