# Project #4: Cross-Border Tax Optimization Agent
## "TaxCompass" - AI-Powered Cross-Border Tax Analysis

**Tagline:** Smart tax residency analysis and optimization for international professionals

---

## Executive Summary

**Value Proposition:** Automates complex cross-border tax residency determination and scenario modeling that currently requires $2,000-5,000 in professional fees.

**Target Market:** 
- Primary: Canadian professionals moving to UAE, US, UK, Singapore
- Secondary: Expats moving to Canada
- Tertiary: Digital nomads navigating multiple tax jurisdictions

**Revenue Model:**
- Freemium: Basic residency check (free)
- Pro: Full analysis + scenario modeling ($99-199 one-time)
- Enterprise: API access for accountants/advisors ($299/month)

**Technical Approach:** Multi-agent system with strong privacy guarantees, no data retention by default

---

## Repository Structure

```
taxcompass/
├── README.md
├── LICENSE (AGPL-3.0 for OSS, commercial licensing available)
├── .gitignore
├── .env.example
├── docker-compose.yml
├── pyproject.toml
│
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI app
│   │   ├── config.py            # Settings management
│   │   ├── schemas/             # Pydantic models
│   │   │   ├── user.py
│   │   │   ├── residency.py
│   │   │   ├── scenario.py
│   │   │   └── report.py
│   │   ├── agents/              # Agent implementations
│   │   │   ├── base.py
│   │   │   ├── document_ingestor.py
│   │   │   ├── residency_analyzer.py
│   │   │   ├── scenario_modeler.py
│   │   │   ├── form_generator.py
│   │   │   └── advisor.py
│   │   ├── graph/               # LangGraph workflows
│   │   │   ├── residency_workflow.py
│   │   │   └── optimization_workflow.py
│   │   ├── rag/                 # Tax law knowledge base
│   │   │   ├── vectorstore.py
│   │   │   ├── embeddings.py
│   │   │   └── retrievers.py
│   │   ├── api/                 # API routes
│   │   │   ├── v1/
│   │   │   │   ├── auth.py
│   │   │   │   ├── analysis.py
│   │   │   │   ├── scenarios.py
│   │   │   │   └── reports.py
│   │   ├── services/
│   │   │   ├── auth_service.py
│   │   │   ├── encryption_service.py
│   │   │   ├── pdf_service.py
│   │   │   └── payment_service.py
│   │   ├── db/
│   │   │   ├── models.py        # SQLAlchemy models
│   │   │   └── session.py
│   │   └── utils/
│   │       ├── security.py
│   │       ├── validators.py
│   │       └── formatters.py
│   ├── tests/
│   │   ├── unit/
│   │   ├── integration/
│   │   └── fixtures/
│   └── scripts/
│       ├── seed_tax_data.py
│       └── migrate.py
│
├── frontend/
│   ├── package.json
│   ├── next.config.js
│   ├── tailwind.config.js
│   ├── src/
│   │   ├── app/                 # Next.js 14 app router
│   │   │   ├── page.tsx         # Landing page
│   │   │   ├── auth/
│   │   │   ├── dashboard/
│   │   │   ├── analysis/
│   │   │   └── scenarios/
│   │   ├── components/
│   │   │   ├── ui/              # shadcn/ui components
│   │   │   ├── forms/
│   │   │   ├── visualizations/
│   │   │   └── reports/
│   │   ├── lib/
│   │   │   ├── api.ts           # API client
│   │   │   ├── auth.ts
│   │   │   └── utils.ts
│   │   └── hooks/
│   └── public/
│
├── knowledge_base/              # Tax law documents (not in git)
│   ├── canada/
│   │   ├── cra_folio_s5_f1_c1.pdf
│   │   ├── form_nr73_guide.pdf
│   │   └── treaties/
│   ├── usa/
│   ├── uae/
│   └── uk/
│
├── docs/
│   ├── architecture.md
│   ├── agent_design.md
│   ├── security.md
│   ├── api_reference.md
│   └── deployment.md
│
└── infrastructure/
    ├── terraform/
    │   ├── main.tf
    │   └── variables.tf
    └── k8s/
        ├── deployment.yaml
        └── service.yaml
```

---

## Tech Stack (Deliberate Choices)

### Backend

**Core Framework:**
- **FastAPI** (not Flask/Django)
  - Why: Async native, auto OpenAPI docs, Pydantic integration, fast
  - Type safety critical for financial calculations
  - Easy WebSocket support for streaming agent responses

**Agent Framework:**
- **LangGraph** (not CrewAI/AutoGen)
  - Why: Production-ready, owned by LangChain (stable), great observability
  - Stateful workflows crucial for multi-step analysis
  - Easy to add human-in-the-loop checkpoints
  - Built-in persistence

**LLM Provider:**
- **Primary: Ollama + Llama 3.1 70B** for privacy-first deployment
  - Why: No data leaves infrastructure, GDPR/privacy compliant
  - Can quantize to 8-bit for reasonable inference on 1x A100
  - Free inference costs
- **Fallback: Azure OpenAI** (GPT-4) for complex reasoning
  - Why: Better at multi-step tax logic
  - Customer can choose (privacy vs accuracy tradeoff)
  - Use with strict data processing agreements

**Vector Store:**
- **Qdrant** (not Pinecone/Weaviate)
  - Why: OSS, self-hostable, fast, good filtering
  - Rust-based = performant
  - Better than ChromaDB for production
  - Easy Docker deployment

**Database:**
- **PostgreSQL 16** with pgvector extension
  - Why: ACID transactions (critical for payments)
  - Row-level security for multi-tenancy
  - Encryption at rest available
  - Mature, well-understood

**Document Processing:**
- **PyMuPDF** (not PyPDF2)
  - Why: Fast, accurate text extraction
  - Good for tax forms (complex layouts)
- **Unstructured.io** for complex docs
  - Why: Handles tables, images in PDFs well

**Observability:**
- **Phoenix** for LLM traces
- **Sentry** for error tracking
- **Prometheus + Grafana** for metrics

### Frontend

**Framework:**
- **Next.js 14** with App Router (not React SPA)
  - Why: SSR for SEO (important for commercialization)
  - API routes = simpler deployment
  - Image optimization built-in
  - TypeScript native

**UI Library:**
- **shadcn/ui** + Tailwind CSS (not Material UI)
  - Why: Copy-paste components, full control
  - Beautiful defaults
  - No runtime JS overhead
  - Easy customization for branding

**State Management:**
- **Zustand** (not Redux)
  - Why: Simple, TypeScript-first
  - No boilerplate
  - Good for this use case (not complex state)

**Charts:**
- **Recharts** (not Chart.js)
  - Why: React-native, declarative, responsive
  - Good for scenario comparison visualizations

**Authentication:**
- **NextAuth.js** (now Auth.js)
  - Why: Easy OAuth integration
  - Session management built-in
  - Works with API routes

### Infrastructure

**Containerization:**
- **Docker + Docker Compose** for local dev
- **Kubernetes** for production (optional, start with single VM)

**Deployment:**
- **Recommended: Hetzner Cloud** (not AWS)
  - Why: 1/3 the cost, EU-based (GDPR), good performance
  - CX51: 8 vCPU, 32GB RAM, €46/month vs AWS ~$150
- **Alternative: Railway** for quick MVP
  - Why: Dead simple, git-based deployment, free tier
  - Move to Hetzner when ready to scale

**CDN:**
- **Cloudflare** (free tier)
  - Why: DDoS protection, caching, good for static assets

**CI/CD:**
- **GitHub Actions**
  - Why: Free for public repos, good ecosystem

---

## Agent Architecture

### Agent Orchestration (LangGraph State Machine)

```
User Input
    ↓
[Document Ingestor Agent]
    ↓
[Residency Analyzer Agent] ←→ [Tax Law RAG]
    ↓
[Scenario Modeler Agent] (runs N scenarios in parallel)
    ↓
[Advisor Agent] (synthesizes recommendations)
    ↓
[Report Generator] (optional)
    ↓
[Form Filler Agent] (optional, premium feature)
```

### Agent Descriptions

**1. Document Ingestor Agent**
- **Purpose:** Extract structured data from uploaded documents
- **Inputs:** PDFs (pay stubs, employment contracts, leases, bank statements)
- **Tools:**
  - PyMuPDF for text extraction
  - GPT-4-vision or Llama 3.2 Vision for complex layouts
  - Pydantic validators for structured output
- **Outputs:** Structured JSON with user profile
- **Security:** Process in-memory only, no disk writes unless explicitly saved

**2. Residency Analyzer Agent**
- **Purpose:** Determine tax residency status for both countries
- **Inputs:** User profile, country pair (e.g., Canada → UAE)
- **Tools:**
  - RAG over tax authority documents (CRA folios, IRS pubs)
  - Specialized prompts for each country's residency tests
  - Confidence scoring for each determination
- **Outputs:**
  ```python
  class ResidencyDetermination(BaseModel):
      origin_country: str
      destination_country: str
      origin_residency_status: Literal["resident", "non-resident", "deemed-resident"]
      destination_residency_status: Literal["resident", "non-resident"]
      confidence: float
      key_factors: List[str]
      residential_ties_score: Dict[str, int]
      recommendations: List[str]
  ```

**3. Scenario Modeler Agent**
- **Purpose:** Run parallel what-if scenarios
- **Scenarios:**
  - Baseline: Current situation
  - Scenario A: Family moves together
  - Scenario B: Family stays in origin country
  - Scenario C: Sell vs rent property
  - Scenario D: Timing variations (leave mid-year vs Jan 1)
- **Calculations:**
  - Tax liability in each country
  - Departure tax calculations
  - After-tax income comparison
  - 3-year cumulative impact
- **Outputs:** Comparative analysis with visualizations

**4. Advisor Agent**
- **Purpose:** Synthesize findings into actionable recommendations
- **Inputs:** All prior agent outputs
- **Reasoning:** Multi-step chain-of-thought
- **Outputs:**
  - Top 3 recommendations
  - Action checklist
  - Risk warnings
  - Timeline suggestion
  - "When to consult a professional" flags

**5. Form Filler Agent** (Premium Feature)
- **Purpose:** Pre-populate tax forms with user data
- **Forms Supported:**
  - Canada: NR73, T1 departure section, T1161, NR6
  - USA: Form 8840, Form 1040-NR
  - UK: P85
- **Outputs:** PDF with filled forms + instructions
- **Security:** Forms generated on-demand, not stored

---

## Data Models (Pydantic Schemas)

### Core Models

```python
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Literal
from datetime import date
from decimal import Decimal

class UserProfile(BaseModel):
    """User's tax situation profile"""
    # Personal
    citizenship: List[str]
    current_country: str
    destination_country: str
    departure_date: date
    
    # Family
    marital_status: Literal["single", "married", "common_law"]
    has_spouse: bool
    spouse_location: Optional[str]
    has_dependents: bool
    dependents_location: Optional[str]
    
    # Property
    owns_home_origin: bool
    home_disposition: Optional[Literal["sell", "rent", "keep_vacant"]]
    owns_home_destination: bool
    
    # Employment
    employment_type: Literal["employee", "self_employed", "business_owner"]
    employer_country: str
    annual_income: Decimal
    
    # Financial
    has_rental_property: bool
    investment_accounts_balance: Optional[Decimal]
    rrsp_balance: Optional[Decimal]
    tfsa_balance: Optional[Decimal]
    unrealized_capital_gains: Optional[Decimal]
    
    # Ties (scoring system)
    ties_score: Dict[str, int] = Field(default_factory=dict)

class ResidencyAnalysis(BaseModel):
    """Output from residency analyzer"""
    origin_status: Literal["resident", "non-resident", "factual-resident", "deemed-resident"]
    destination_status: Literal["resident", "non-resident"]
    confidence: float = Field(ge=0.0, le=1.0)
    reasoning: str
    key_factors: List[str]
    red_flags: List[str]
    recommendations: List[str]

class TaxCalculation(BaseModel):
    """Tax calculation for a scenario"""
    scenario_name: str
    origin_tax: Decimal
    destination_tax: Decimal
    departure_tax: Optional[Decimal]
    total_tax: Decimal
    after_tax_income: Decimal
    effective_rate: float

class ScenarioComparison(BaseModel):
    """Comparison of multiple scenarios"""
    baseline: TaxCalculation
    scenarios: List[TaxCalculation]
    best_scenario: str
    worst_scenario: str
    savings_vs_worst: Decimal
    three_year_impact: Decimal

class ActionPlan(BaseModel):
    """Actionable recommendations"""
    priority_actions: List[str]
    timeline: Dict[str, List[str]]  # "3_months_before": [actions]
    forms_to_file: List[str]
    documents_needed: List[str]
    professional_help_needed: bool
    professional_help_reason: Optional[str]
    estimated_cost: Dict[str, Decimal]  # breakdown of one-time costs
```

---

## Security & Privacy Architecture

### Security Requirements

**Data Classification:**
- **Tier 1 (Highly Sensitive):** 
  - Financial account numbers
  - SSN/SIN
  - Passwords
  - Tax returns
  - **Handling:** Encrypt at rest (AES-256), in transit (TLS 1.3), minimize retention
  
- **Tier 2 (Sensitive):**
  - Income amounts
  - Asset values
  - Personal information
  - **Handling:** Encrypt at rest, aggregate for analytics only with consent
  
- **Tier 3 (Public):**
  - Tax law documents
  - General scenarios
  - **Handling:** Standard security

### Privacy-First Design

**1. Data Minimization:**
- Don't ask for data you don't need
- No SSN/SIN collection (not needed for residency analysis)
- Optional document upload (can manually enter data)

**2. Zero-Knowledge Architecture:**
- **Client-side encryption option:** User encrypts sensitive docs with their key before upload
- **Ephemeral processing:** Documents processed in-memory, deleted after extraction
- **No default retention:** User must explicitly "save" analysis
- **Export-only:** User can download full report and delete all data

**3. Access Controls:**
- Row-level security in PostgreSQL
- Each user can only access their data
- Admin access logged and audited
- No employee access to user data without explicit permission

**4. Compliance:**
- **GDPR Ready:**
  - Right to access: API endpoint for data export
  - Right to erasure: Hard delete with verification
  - Data portability: JSON export
  - Consent management: Explicit opt-in for each feature
- **CCPA Compliance:** Same rights as GDPR
- **SOC 2 Type II Ready:** Audit logging, encryption, access controls

### Security Implementation

```python
# backend/app/services/encryption_service.py

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
import os
import base64

class EncryptionService:
    """Handle encryption of sensitive data"""
    
    def __init__(self):
        self.master_key = os.environ["MASTER_ENCRYPTION_KEY"]
    
    def encrypt_field(self, plaintext: str, user_salt: str) -> str:
        """Encrypt with user-specific key derived from master key"""
        # Derive user-specific key
        kdf = PBKDF2(...)
        key = base64.urlsafe_b64encode(kdf.derive(user_salt.encode()))
        cipher = Fernet(key)
        return cipher.encrypt(plaintext.encode()).decode()
    
    def decrypt_field(self, ciphertext: str, user_salt: str) -> str:
        """Decrypt with user-specific key"""
        kdf = PBKDF2(...)
        key = base64.urlsafe_b64encode(kdf.derive(user_salt.encode()))
        cipher = Fernet(key)
        return cipher.decrypt(ciphertext.encode()).decode()

# Database model with encrypted fields
class UserData(Base):
    __tablename__ = "user_data"
    
    id = Column(UUID, primary_key=True)
    user_id = Column(UUID, ForeignKey("users.id"))
    
    # Encrypted fields
    income_encrypted = Column(Text)  # Store encrypted
    assets_encrypted = Column(Text)
    
    # Non-sensitive fields
    citizenship = Column(String)
    current_country = Column(String)
    
    # Audit
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    accessed_at = Column(DateTime)
```

### Authentication & Authorization

```python
# OAuth 2.0 + JWT
# Support: Google, GitHub, email/password

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """Verify JWT and return current user"""
    try:
        payload = jwt.decode(
            credentials.credentials,
            os.environ["JWT_SECRET"],
            algorithms=["HS256"]
        )
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401)
        # Fetch user from DB
        user = await get_user_by_id(user_id)
        return user
    except JWTError:
        raise HTTPException(status_code=401)

# Rate limiting (prevent abuse)
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/v1/analysis")
@limiter.limit("5/hour")  # Free tier: 5 analyses per hour
async def create_analysis(...):
    ...
```

---

## API Design

### RESTful API Structure

```
POST   /api/v1/auth/register
POST   /api/v1/auth/login
POST   /api/v1/auth/logout
GET    /api/v1/auth/me

# Analysis flow
POST   /api/v1/analysis              # Create new analysis
GET    /api/v1/analysis/{id}         # Get analysis
PUT    /api/v1/analysis/{id}         # Update inputs
DELETE /api/v1/analysis/{id}         # Delete
POST   /api/v1/analysis/{id}/run     # Execute agent workflow

# Document upload
POST   /api/v1/documents/upload      # Upload doc for processing
GET    /api/v1/documents/{id}        # Get processed data
DELETE /api/v1/documents/{id}        # Delete

# Scenarios
GET    /api/v1/scenarios/{analysis_id}        # List scenarios
POST   /api/v1/scenarios/{analysis_id}/run    # Run scenario
GET    /api/v1/scenarios/{scenario_id}/result

# Reports
POST   /api/v1/reports/{analysis_id}/generate  # Generate PDF report
GET    /api/v1/reports/{report_id}/download

# Forms (Premium)
GET    /api/v1/forms/supported               # List supported forms
POST   /api/v1/forms/{analysis_id}/fill      # Fill form
GET    /api/v1/forms/{form_id}/download

# WebSocket for real-time agent updates
WS     /api/v1/ws/analysis/{id}              # Stream agent progress
```

### Example API Interaction

```python
# Client side (TypeScript)
const response = await fetch('/api/v1/analysis', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    origin_country: 'CA',
    destination_country: 'AE',
    departure_date: '2025-06-01',
    family_moves: true,
    // ... other fields
  })
});

const { analysis_id } = await response.json();

// Stream agent progress via WebSocket
const ws = new WebSocket(`ws://api.taxcompass.io/api/v1/ws/analysis/${analysis_id}`);
ws.onmessage = (event) => {
  const update = JSON.parse(event.data);
  console.log(`Agent: ${update.agent}, Status: ${update.status}`);
  // Update UI with progress
};

// Run analysis
await fetch(`/api/v1/analysis/${analysis_id}/run`, {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${token}` }
});

// Get results
const results = await fetch(`/api/v1/analysis/${analysis_id}`);
```

---

## Development Phases

### Phase 1: MVP (4-6 weeks)

**Goal:** Working prototype for Canada → UAE use case only

**Features:**
- ✅ User authentication (email/password only)
- ✅ Manual data entry form (no document upload)
- ✅ Residency analyzer agent (Canada/UAE)
- ✅ Basic scenario modeler (2 scenarios: family moves vs stays)
- ✅ Simple tax calculator
- ✅ Text report generation
- ✅ Responsive UI (mobile-friendly)

**Tech:**
- Backend: FastAPI + SQLite (no Postgres yet)
- Frontend: Next.js + Tailwind
- LLM: Ollama Llama 3.1 8B (runs on laptop)
- Vector Store: Chroma DB (file-based)
- No authentication beyond JWT

**Deliverable:** 
- Working demo
- Hosted on Railway or Vercel (frontend) + Fly.io (backend)
- Public GitHub repo

---

### Phase 2: Production Beta (6-8 weeks)

**Goal:** Production-ready for early adopters, monetization ready

**Features:**
- ✅ OAuth (Google, GitHub)
- ✅ Document upload + extraction (PDFs)
- ✅ Expanded country support (USA, UK, Singapore)
- ✅ 5 scenario comparison
- ✅ Interactive visualizations (charts)
- ✅ PDF report generation
- ✅ Stripe payment integration (one-time purchase)
- ✅ User dashboard (save multiple analyses)
- ✅ Email notifications
- ✅ Admin panel

**Tech Upgrades:**
- PostgreSQL database
- Qdrant vector store
- Azure OpenAI fallback (optional)
- Redis for caching
- Sentry error tracking
- Phoenix observability

**Infrastructure:**
- Hetzner Cloud VPS (CX51)
- Cloudflare CDN
- Automated backups
- GitHub Actions CI/CD

**Deliverable:**
- Beta launch with 50-100 users
- Stripe payment working
- $99 per analysis pricing

---

### Phase 3: Scale & Enterprise (12+ weeks)

**Goal:** Scale to 1000+ users, enterprise features

**Features:**
- ✅ Team/organization accounts
- ✅ API access for accountants
- ✅ Form filling (NR73, T1, etc.)
- ✅ Multi-year projections
- ✅ More countries (10+ total)
- ✅ Treaty analyzer (which treaty applies)
- ✅ Webhook integrations
- ✅ White-label option
- ✅ Affiliate program

**Tech:**
- Kubernetes deployment (multi-region)
- Load balancing
- Horizontal scaling
- Advanced caching
- CDN for static assets
- Comprehensive monitoring

**Business:**
- SaaS pricing ($29/month unlimited)
- Enterprise contracts ($500-2000/month)
- Accountant partnerships

---

## Monetization Strategy

### Pricing Tiers

**Free Tier:**
- 1 basic residency check
- 2 scenario comparison
- View tax law summaries
- No document upload
- No PDF reports

**Pro (One-Time: $99-199):**
- Unlimited analyses (30 days)
- Document upload + extraction
- 5 scenario comparisons
- PDF report generation
- Priority support
- Money-back guarantee if not satisfied

**Enterprise (Monthly: $299-999):**
- API access (100 requests/month)
- White-label option
- Team accounts (5-20 users)
- Custom country coverage
- Dedicated support
- Form filling

**Accountant Partner ($49/analysis):**
- Bulk pricing for tax professionals
- Client management dashboard
- Co-branded reports
- API integration

### Revenue Projections (Conservative)

**Year 1:**
- 500 Pro purchases × $149 = $74,500
- 10 Enterprise × $299/mo × 6mo avg = $17,940
- **Total: ~$92K**

**Year 2:**
- 2000 Pro purchases × $149 = $298,000
- 50 Enterprise × $499/mo × 12mo = $299,400
- 200 Accountant × $49 × 5 analyses = $49,000
- **Total: ~$646K**

---

## Go-to-Market Strategy

### Phase 1: Organic Growth

**Content Marketing:**
- Blog: "Tax residency guides" for each country pair
- SEO for "Canada to UAE tax", "NR73 help", etc.
- Reddit: r/PersonalFinanceCanada, r/expats, r/digitalnomad
- LinkedIn: Share tax optimization tips

**Target Audience:**
- Canadian tech workers considering Middle East
- Consultants on international assignments
- Digital nomads
- Finance/tax subreddits

**Free Tools:**
- Public residency checker (lead gen)
- Tax treaty lookup tool
- Departure tax calculator

---

### Phase 2: Partnerships

**Accountant Network:**
- Offer affiliate commission (20%)
- Provide them with demo accounts
- Co-market to their clients

**Corporate HR:**
- Partner with companies sending employees abroad
- Bulk licensing for relocating employees

**Relocation Services:**
- Integrate with relocation platforms
- Offer as value-add

---

## Success Metrics

### Technical KPIs
- Uptime: >99.5%
- API latency: p95 < 2s
- Agent execution time: <60s for full analysis
- Error rate: <1%

### Product KPIs
- User acquisition: 100/month by month 6
- Conversion rate (free → paid): 10%
- Customer satisfaction: NPS >50
- Time to value: <10 minutes from signup to report

### Business KPIs
- MRR: $5K by month 6, $25K by month 12
- CAC < $50 (organic)
- LTV/CAC > 3
- Churn: <5% monthly

---

## Risk Mitigation

### Technical Risks

**1. LLM Hallucinations (Tax Advice)**
- **Risk:** Model gives incorrect tax advice
- **Mitigation:**
  - Clear disclaimers: "Not professional advice"
  - Confidence scoring on all outputs
  - RAG over authoritative sources only
  - Human-in-loop for high-stakes decisions
  - Recommend professional review for complex cases

**2. Data Breach**
- **Risk:** User financial data compromised
- **Mitigation:**
  - Encryption at rest and in transit
  - Minimal data retention
  - Regular security audits
  - Bug bounty program
  - Cyber insurance

**3. Scaling Issues**
- **Risk:** Can't handle user growth
- **Mitigation:**
  - Horizontal scaling architecture
  - Queue system for agent jobs (Celery)
  - Caching aggressive

### Business Risks

**1. Legal/Regulatory**
- **Risk:** Providing tax advice without license
- **Mitigation:**
  - Clear disclaimers everywhere
  - Position as "analysis tool" not "advice"
  - Consult with lawyer on terms of service
  - Don't claim to replace professionals

**2. Competition**
- **Risk:** TurboTax or H&R Block builds similar
- **Mitigation:**
  - Move fast, build moat with data/users
  - Focus on niche (expats) they ignore
  - Build community
  - Open source (harder to compete with free)

**3. Low Adoption**
- **Risk:** Market too small
- **Mitigation:**
  - Validate with 20 customer interviews first
  - Build landing page, collect emails before coding
  - Offer money-back guarantee
  - Pivot to adjacent use cases (general tax optimization)

---

## Open Source Strategy

### Licensing

**Dual License:**
- **AGPL-3.0** for open source (non-commercial use)
- **Commercial license** for companies wanting to white-label
  - $5K one-time or $500/month
  - Removes AGPL restrictions
  - Includes support

### Community Building

- Transparent development (public roadmap)
- Accept contributions (agents for new countries)
- Documentation-first
- Responsive to issues
- Monthly dev blog updates

### Benefits
- Trust: Users can audit security/privacy
- Contributions: Community adds country support
- Marketing: HN/Reddit loves OSS
- Flexibility: Can self-host for privacy
- Moat: Hard to copy entire ecosystem

---

## Next Steps (Week 1)

1. **Set up repos:**
   ```bash
   mkdir taxcompass
   cd taxcompass
   git init
   # Add structure
   git remote add origin git@github.com:yourusername/taxcompass.git
   git push -u origin main
   ```

2. **Install dependencies:**
   ```bash
   # Backend
   poetry init
   poetry add fastapi uvicorn sqlalchemy pydantic langchain langgraph

   # Frontend
   npx create-next-app@latest frontend --typescript --tailwind --app
   ```

3. **Define schemas:** Start with Pydantic models in `backend/app/schemas/`

4. **Build RAG pipeline:** Collect tax docs, create embeddings

5. **Prototype first agent:** Residency analyzer for Canada only

6. **Build simple UI:** Form to input data, display results

---

## Summary: Why This Stack?

**Lightweight:** No over-engineering, mature tools only
**Secure:** Privacy-first architecture, enterprise-ready
**Scalable:** Can grow from 10 → 10,000 users on same architecture
**Monetizable:** Clear path to revenue
**Portfolio-worthy:** Shows full-stack, ML, production deployment skills
**OSS-first:** Can commercialize without compromising open source values

**Total Tech Debt:** Minimal. Every choice is production-ready OSS.

Would you like me to:
1. Generate the initial `pyproject.toml` and `package.json` files?
2. Write the first agent (Residency Analyzer) implementation?
3. Design the database schema in detail?
4. Create the landing page wireframe?
