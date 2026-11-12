# AI Project Intelligence & Risk Advisor

An intelligent, multi-agent platform where software engineering teams and student project groups upload varied project artifacts — proposal PDFs, SRS specifications (.docx), task lists (.csv), sprint meeting notes (.txt), or progress updates (.md) — and receive automated intelligence, risk forecasts, blocker resolution, agile documentation, and a grounded conversational assistant.

![Dashboard Preview](static/index.html)

---

## 🌟 Key Features

1. **Multi-Format Document Ingestion Engine:**
   - Ingests **PDF**, **DOCX**, **CSV**, **TXT**, and **Markdown** documents.
   - Extracts tabular data from PDFs and DOCX files.
   - Converts CSV task backlogs into semantically enriched key-value records.

2. **RAG Knowledge Base & Hybrid Retrieval:**
   - Recursive character chunking preserving hierarchical section boundaries with configurable character overlap.
   - 384-dimensional dense semantic embeddings with sub-word n-gram support and SentenceTransformers fallback.
   - Persistent vector index with normalized cosine similarity search and lexical BM25-style keyword boosting.

3. **Multi-Agent Analysis Pipeline:**
   - **Scope & Deliverable Agent:** Maps in-scope capabilities, explicit out-of-scope boundaries, and deliverable milestones.
   - **Risk Detection & Forecasting Agent:** Calculates quantitative 1–25 severity scores (Probability $\times$ Impact), early warning signs, mitigation strategies, and forecasts delivery delays.
   - **Blocker & Action Item Agent:** Extracts active sprint impediments, unassigned tasks, and prioritized next steps.
   - **Agile Documentation Generator:** Synthesizes structured Agile User Stories in canonical format (`As a... I want to... So that...`) with Gherkin acceptance criteria and highlights critical documentation gaps.

4. **100-Point Holistic Project Health Scorer:**
   - Objective quantitative algorithm scoring across 5 weighted dimensions: Planning (20%), Timeline (25%), Risk Exposure (25%), Documentation (15%), and Blocker Resolution (15%).
   - Generates Grade ratings (A, B, C, D) and interactive 5-axis Radar Chart data.

5. **Grounded Conversational Project Assistant:**
   - Natural language Q&A interface strictly grounded in uploaded project artifacts.
   - Returns interactive source document citations with exact excerpts and similarity scores.

6. **Interactive Web Dashboard:**
   - Responsive Single-Page Application (SPA) built with Tailwind CSS, Chart.js, Lucide icons, and glassmorphism design.
   - One-click sample artifact loader for immediate demonstration.
   - Export reports as Markdown and JSON.

---

## 🚀 Quickstart Guide

### 1. Installation

Ensure Python 3.10+ is installed:

```bash
git clone <repo-url>
cd ai_project_intelligence_risk_advisor
pip install -r requirements.txt
```

### 2. Run the Application Server

Start the FastAPI application:

```bash
python main.py
```

The server will launch at:
👉 **`http://127.0.0.1:8000`**

Open this URL in your web browser to access the interactive dashboard!

### 3. Immediate 1-Click Demo Testing

1. In the top navigation bar, click **"Load Samples"**.
2. The system will automatically index 5 realistic project artifacts pre-packaged in `samples/`:
   - `proposal_project.pdf` (Project Proposal)
   - `srs_specifications.docx` (Requirements Specification)
   - `sprint_meeting_notes.txt` (Sprint standup & blockers)
   - `tasks_backlog.csv` (10-task sprint backlog)
   - `progress_update.md` (Bi-weekly progress report)
3. Click **"Run Multi-Agent Analysis"** to execute all 4 agents and view the health dashboard, risk heatmap matrix, user stories, and radar chart!
4. Navigate to the **"Grounded Assistant"** tab to test conversational queries with citations.

---

## 🧪 Running Automated Tests

Run the full test suite with Pytest:

```bash
python -m pytest tests/ -v
```

All 18 unit and integration tests verify:
- Parsing of PDF, DOCX, CSV, TXT, and MD files.
- Chunking, vector indexing, similarity search, and hybrid retriever.
- Scope, Risk, Blocker, Documentation agents, and Health scoring.
- FastAPI REST endpoints.

---

## 📂 Repository Structure

```
ai_project_intelligence_risk_advisor/
├── app/
│   ├── api/                   # FastAPI route controllers
│   ├── agents/                # Scope, Risk, Blocker, DocGen agents & Orchestrator
│   ├── analytics/             # 100-point Health Scoring algorithm
│   ├── assistant/             # RAG-grounded Conversational Assistant
│   ├── ingestion/             # PDF, DOCX, CSV, TXT, MD document parsers
│   ├── models/                # Pydantic schemas (Document, Project, Health, Chat)
│   ├── rag/                   # Chunker, Embedder, Vector Store, Hybrid Retriever
│   ├── config.py              # Application settings and environment variables
│   └── deps.py                # Singleton service dependencies
├── samples/                   # Pre-generated realistic project artifacts
│   ├── proposal_project.pdf
│   ├── srs_specifications.docx
│   ├── tasks_backlog.csv
│   ├── sprint_meeting_notes.txt
│   ├── progress_update.md
│   └── generate_samples.py
├── static/                    # Responsive SPA Web Dashboard
│   ├── index.html             # UI with Tailwind, Chart.js, Lucide
│   ├── app.js                 # Frontend application logic
│   └── styles.css             # Glassmorphism styling
├── tests/                     # Automated unit and integration tests
│   ├── test_ingestion.py
│   ├── test_rag.py
│   ├── test_agents.py
│   └── test_api.py
├── architecture_design.md     # Milestone 1 Architectural Study & Design Document
├── main.py                    # Server entrypoint
├── requirements.txt           # Dependencies
└── README.md                  # Project documentation
```

---

## ⚙️ Configuration & LLM Providers

The application runs **100% locally out of the box** using the built-in deterministic Project Intelligence Engine.

To enable advanced generative LLM reasoning, configure an API key either:
1. In the web dashboard by clicking the **Settings (gear icon)** button in the top right.
2. In a `.env` file:
   ```env
   GEMINI_API_KEY="your-gemini-key"
   # or
   OPENAI_API_KEY="your-openai-key"
   ```

---

## 📜 Milestone 1 Deliverables Summary

- **Study & Architecture Document:** [`architecture_design.md`](architecture_design.md)
- **Multi-Format Ingestion Module:** [`app/ingestion/`](app/ingestion/)
- **Unified RAG Pipeline:** [`app/rag/`](app/rag/)
- **Multi-Agent Pipeline & Scoring:** [`app/agents/`](app/agents/) and [`app/analytics/`](app/analytics/)
- **Test Suite:** 18 passing tests in [`tests/`](tests/)
- **Dashboard:** [`static/index.html`](static/index.html)
