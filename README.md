# TaxCompass 🧭

**AI-Powered Cross-Border Tax Analysis**

Smart tax residency analysis and optimization for international professionals.

## Overview

TaxCompass automates complex cross-border tax residency determination and scenario modeling that currently requires $2,000-5,000 in professional fees.

### Target Users
- Canadian professionals moving to UAE, US, UK, Singapore
- Expats moving to Canada
- Digital nomads navigating multiple tax jurisdictions

## Features (Phase 1 MVP)

- [ ] Basic residency determination (Canada → UAE)
- [ ] Manual data input form
- [ ] RAG over CRA tax folios
- [ ] Simple scenario comparison (2 scenarios)
- [ ] Basic PDF report generation

## Tech Stack

**Backend:**
- FastAPI (async, type-safe)
- LangGraph (agent orchestration)
- Ollama + Llama 3.1 (privacy-first LLM)
- Qdrant (vector store)
- PostgreSQL 16 + pgvector

**Frontend:**
- Next.js 14 (App Router)
- shadcn/ui + Tailwind CSS
- Zustand (state management)
- Recharts (visualizations)

## Quick Start

### Prerequisites
- Python 3.11+
- Poetry
- Docker & Docker Compose
- Node.js 20+

### Backend Setup

```bash
cd backend
poetry install
poetry run uvicorn app.main:app --reload
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

### Full Stack (Docker)

```bash
docker-compose up -d
```

## Project Structure

```
taxcompass/
├── backend/
│   ├── app/
│   │   ├── main.py           # FastAPI application
│   │   ├── config.py         # Settings management
│   │   ├── schemas/          # Pydantic models
│   │   ├── agents/           # LangGraph agents
│   │   ├── graph/            # Workflow definitions
│   │   ├── rag/              # Vector store & retrievers
│   │   ├── api/              # API routes
│   │   ├── services/         # Business logic
│   │   └── db/               # Database models
│   └── tests/
├── frontend/                 # Next.js application
├── knowledge_base/           # Tax documents (not in git)
├── docs/                     # Documentation
└── infrastructure/           # Terraform, K8s configs
```

## Documentation

- [Architecture Overview](docs/architecture.md)
- [Agent Design](docs/agent_design.md) (coming soon)
- [API Reference](docs/api_reference.md) (coming soon)
- [Security](docs/security.md) (coming soon)

## License

AGPL-3.0 - See [LICENSE](LICENSE) for details.

Commercial licensing available for organizations requiring proprietary deployment.

## Disclaimer

⚠️ **TaxCompass is an analysis tool, not professional tax advice.**

Always consult a qualified tax professional before making decisions based on this tool's output. Tax laws are complex and vary by jurisdiction and individual circumstances.

---

Built with ❤️ for the global mobility community
