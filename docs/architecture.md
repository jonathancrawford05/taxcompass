# TaxCompass Architecture

## Overview

TaxCompass is a multi-agent system built with LangGraph that analyzes cross-border tax residency and provides optimization recommendations.

## System Architecture

```
┌─────────────────┐
│   Frontend      │
│   (Next.js 14)  │
└────────┬────────┘
         │
         │ HTTP/WebSocket
         │
┌────────▼────────┐
│   Backend API   │
│   (FastAPI)     │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
┌───▼──┐  ┌──▼────┐
│ LLM  │  │  RAG  │
│(Oll.)│  │(Qdrnt)│
└──────┘  └───────┘
```

## Components

### 1. Frontend (Next.js 14)
- App Router for SSR
- shadcn/ui for components
- Zustand for state management
- Recharts for visualizations

### 2. Backend (FastAPI)
- RESTful API
- WebSocket for agent streaming
- Authentication & authorization
- Rate limiting

### 3. Agent System (LangGraph)
- Document Ingestor Agent
- Residency Analyzer Agent
- Scenario Modeler Agent
- Advisor Agent
- Form Filler Agent (Premium)

### 4. Data Layer
- PostgreSQL (user data, analyses)
- Qdrant (tax law knowledge base)
- Redis (caching, rate limiting)

### 5. LLM Layer
- Primary: Ollama + Llama 3.1
- Fallback: Azure OpenAI GPT-4

## Security Architecture

- End-to-end encryption
- Row-level security in PostgreSQL
- Zero-knowledge processing option
- GDPR & CCPA compliant

## Deployment Architecture

### Development
- Docker Compose for local development
- Hot reload for both frontend and backend

### Production
- Hetzner Cloud VPS (recommended)
- Cloudflare CDN
- Kubernetes (optional, for scaling)

## Data Flow

1. User submits information via frontend
2. Backend validates and sanitizes input
3. Agents process data through LangGraph workflow
4. RAG retrieves relevant tax laws
5. LLM analyzes and generates recommendations
6. Results streamed back to frontend
7. User can generate reports/forms

## Coming Soon

Detailed documentation for:
- Agent design patterns
- API reference
- Security best practices
- Deployment guide
