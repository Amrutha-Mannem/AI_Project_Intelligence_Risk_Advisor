# AI Project Intelligence & Risk Advisor

> **An intelligent platform that transforms scattered project documents into actionable insights, risk forecasts, and automated project management guidance.**

---

## Project Details

| Field | Details |
|---|---|
| **Author** | Amrutha Varshini |
| **GitHub** | [Amrutha-Mannem](https://github.com/Amrutha-Mannem) |
| **Repository** | [AI_Project_Intelligence_Risk_Advisor](https://github.com/Amrutha-Mannem/AI_Project_Intelligence_Risk_Advisor) |
| **Version** | 1.0.0 |
| **Tech Stack** | Python 3.13, FastAPI, RAG, Multi-Agent Pipeline, HTML/CSS/JS |

---

## Project Statement

Software development teams and student project groups frequently struggle with incomplete planning, missed deadlines, undetected risks, and poor documentation. While teams do generate project-related documents — proposals, meeting notes, sprint updates, task lists, and progress reports — extracting actionable intelligence from these scattered artifacts manually is time-consuming and often overlooked. This results in reactive problem-solving instead of proactive project management.

The objective of this project is to develop an **AI Project Intelligence & Risk Advisor** — an intelligent platform where teams upload their existing project documents and receive automated insights, risk forecasts, and actionable recommendations. The system accepts any combination of inputs — project proposal PDFs, SRS documents, meeting notes, progress update texts, or task list CSVs — and builds a unified project knowledge base using RAG. A multi-agent pipeline then analyses this knowledge base to surface scope, risks, blockers, and action items automatically.

---

## Features

### Document Ingestion Module
- Supports **PDF**, **DOCX**, **CSV**, **TXT**, and **XLSX** formats
- Automatic text extraction with chunking (500-token chunks, 50-token overlap)
- Embedding generation using `sentence-transformers`
- In-memory vector store with cosine-similarity search

### RAG Pipeline
- Semantic document chunking and embedding
- Top-K retrieval with cosine similarity scoring
- Context-aware query expansion for short prompts
- Multi-document knowledge base across all uploaded files

### Multi-Agent Pipeline
| Agent | Responsibility |
|---|---|
| **Scope & Deliverable Extraction Agent** | Identifies milestones, deliverables, and project scope from documents |
| **Risk & Schedule Forecasting Agent** | Detects risks, severity levels, and predicts delivery timelines |
| **Blocker & Impediment Detection Agent** | Surfaces blockers, dependencies, and impediments from meeting notes |
| **Action Item Identification Agent** | Extracts pending tasks, owners, and deadlines from meeting notes |

### Project Health Scoring
- Composite health score (0–100) across four dimensions:
  - **Timeline** — schedule adherence and milestone completion
  - **Scope** — scope creep and deliverable clarity
  - **Risk** — count and severity of open risks
  - **Documentation** — completeness of project artifacts
- Real-time status: `healthy`, `at_risk`, or `critical`

### Conversational Assistant
- RAG-powered chatbot for natural-language Q&A over project documents
- Context-aware responses grounded in uploaded document content
- Session-based conversation history

### Web Dashboard
- Interactive single-page dashboard with real-time analysis
- Document upload with drag-and-drop support
- Risk visualization, health score gauges, and agent output cards
- Export full project intelligence report (JSON/PDF)

---

## Project Documents

The `docs/` folder contains all project management artifacts:

| Document | Description |
|---|---|
| [`Agile_Template_v0.1.xlsx`](docs/Agile_Template_v0.1.xlsx) | Sprint backlog with 10 user stories across 5 sprints |
| [`Defect_Tracker_Template_v0.1.xlsx`](docs/Defect_Tracker_Template_v0.1.xlsx) | 5 defects tracked and resolved during development |
| [`Unit_Test_Plan_v0.1.xlsx`](docs/Unit_Test_Plan_v0.1.xlsx) | 10 unit test cases with Pass/Fail results |

---

## Project Milestones

### Milestone 1 — Architecture, Ingestion & RAG Pipeline ✅
1. Studied RAG architecture, multi-agent design patterns, and project management fundamentals
2. Designed system architecture, agent roles, RAG pipeline, and document data models
3. Developed document ingestion module — PDF, DOCX, CSV, TXT, XLSX support
4. Implemented RAG pipeline — document chunking, embedding generation, and vector store indexing

### Milestone 2 — Multi-Agent Pipeline & Dashboard ✅
1. Developed **Scope & Deliverable Extraction Agent** using keyword + semantic analysis
2. Built **Risk & Schedule Forecasting Agent** with severity classification (HIGH/MEDIUM/LOW)
3. Implemented **Blocker & Impediment Detection Agent** scanning meeting notes
4. Created **Action Item Identification Agent** extracting tasks with owners and deadlines
5. Validated all agent outputs using sample project documents across PDF, DOCX, CSV, and TXT formats
6. Built interactive web dashboard with health scoring, risk charts, and conversational assistant
7. Added export functionality for full project intelligence reports

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                   Web Dashboard                      │
│           (HTML / CSS / JavaScript)                  │
└───────────────────┬─────────────────────────────────┘
                    │ HTTP REST
┌───────────────────▼─────────────────────────────────┐
│              FastAPI Backend (main.py)               │
├─────────┬──────────┬──────────┬──────────┬──────────┤
│ /ingest │  /agents │  /health │  /chat   │  /export │
└────┬────┴────┬─────┴────┬─────┴────┬─────┴──────────┘
     │         │          │          │
┌────▼───┐  ┌──▼─────────▼──┐  ┌────▼──────┐
│Document│  │ Multi-Agent    │  │   RAG     │
│Ingestion│  │ Orchestrator  │  │ Pipeline  │
│Module  │  │               │  │           │
└────┬───┘  │ ■ Scope Agent │  │ ■ Chunk   │
     │      │ ■ Risk Agent  │  │ ■ Embed   │
     │      │ ■ Blocker Agt │  │ ■ Index   │
     │      │ ■ Action Item │  │ ■ Retrieve│
     │      └───────────────┘  └───────────┘
     │
┌────▼────────────────────────────────────────────────┐
│          Vector Store (In-Memory, Cosine Similarity) │
│          Sentence-Transformers Embeddings            │
└─────────────────────────────────────────────────────┘
```

---

## Project Structure

```
AI_Project_Intelligence_Risk_Advisor/
├── main.py                     # FastAPI application entry point
├── requirements.txt            # Python dependencies
├── architecture_design.md      # System architecture documentation
├── README.md                   # This file
│
├── app/
│   ├── config.py               # Application configuration
│   ├── deps.py                 # Dependency injection
│   ├── models/
│   │   ├── document.py         # Document & Chunk models
│   │   ├── project.py          # Project, Risk, Blocker, ActionItem models
│   │   └── health.py           # Health scoring models
│   ├── ingestion/
│   │   └── parser.py           # Multi-format document parser
│   ├── rag/
│   │   └── pipeline.py         # RAG chunking, embedding & retrieval
│   ├── agents/
│   │   └── orchestrator.py     # Multi-agent orchestration pipeline
│   ├── analytics/
│   │   └── health_scorer.py    # Project health scoring module
│   ├── assistant/
│   │   └── chat.py             # Conversational RAG assistant
│   └── api/
│       ├── routes_ingest.py    # Document upload endpoints
│       ├── routes_agents.py    # Agent analysis endpoints
│       ├── routes_health.py    # Health score endpoints
│       ├── routes_chat.py      # Chat assistant endpoints
│       ├── routes_rag.py       # RAG query endpoints
│       └── routes_export.py    # Report export endpoints
│
├── static/
│   ├── index.html              # Web dashboard
│   ├── app.js                  # Dashboard JavaScript
│   └── styles.css              # Dashboard styles
│
├── docs/
│   ├── Agile_Template_v0.1.xlsx          # Sprint backlog (10 user stories)
│   ├── Defect_Tracker_Template_v0.1.xlsx # Defect tracking (5 defects)
│   └── Unit_Test_Plan_v0.1.xlsx          # Unit test plan (10 test cases)
│
├── samples/                    # Sample project documents for testing
└── tests/                      # Automated test suite
```

---

## Setup & Installation

### Prerequisites
- Python 3.10 or higher
- pip

### 1. Clone the Repository
```bash
git clone https://github.com/Amrutha-Mannem/AI_Project_Intelligence_Risk_Advisor.git
cd AI_Project_Intelligence_Risk_Advisor
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure API Key (Optional)
Create a `.env` file in the project root for enhanced AI responses:
```env
GEMINI_API_KEY=your_gemini_api_key_here
# or
OPENAI_API_KEY=your_openai_api_key_here
```
> **Note:** The system works fully without an API key using the built-in local intelligence engine.

### 4. Run the Application
```bash
python main.py
```

Open your browser and navigate to: **http://127.0.0.1:8000**

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/ingest` | Upload project documents |
| `POST` | `/api/agents/analyze` | Run multi-agent analysis |
| `GET` | `/api/health` | Get project health score |
| `POST` | `/api/chat` | Chat with RAG assistant |
| `POST` | `/api/rag/query` | Semantic search over documents |
| `GET` | `/api/export/report` | Export full intelligence report |
| `GET` | `/docs` | Swagger API documentation |

---

## Testing

Run the test suite:
```bash
python -m pytest tests/ -v
```

All 10 unit test cases are documented in [`docs/Unit_Test_Plan_v0.1.xlsx`](docs/Unit_Test_Plan_v0.1.xlsx).

---

## Technologies Used

| Technology | Purpose |
|---|---|
| **Python 3.13** | Core language |
| **FastAPI** | REST API backend |
| **Uvicorn** | ASGI server |
| **sentence-transformers** | Document embeddings |
| **pdfplumber / PyPDF2** | PDF parsing |
| **python-docx** | DOCX parsing |
| **pandas / openpyxl** | CSV / XLSX parsing |
| **scikit-learn** | Cosine similarity search |
| **Pydantic v2** | Data validation & modelling |
| **HTML / CSS / JS** | Web dashboard frontend |

---

## Author

**Amrutha Varshini**
- GitHub: [@Amrutha-Mannem](https://github.com/Amrutha-Mannem)
- Repository: [AI_Project_Intelligence_Risk_Advisor](https://github.com/Amrutha-Mannem/AI_Project_Intelligence_Risk_Advisor)

---

*Built as part of the AI Project Intelligence & Risk Advisor project — an intelligent platform for automated project insights, risk forecasting, and multi-agent document analysis.*
