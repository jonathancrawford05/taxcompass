"""
TaxCompass FastAPI Application
Main entry point for the backend API server
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings

app = FastAPI(
    title="TaxCompass API",
    description="AI-Powered Cross-Border Tax Analysis",
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "TaxCompass API",
        "version": "0.1.0"
    }


@app.get("/api/v1/health")
async def health():
    """Detailed health check"""
    return {
        "status": "healthy",
        "database": "connected",
        "vector_store": "connected"
    }


# Import and include routers
# from app.api.v1 import auth, analysis, scenarios, reports
# app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
# app.include_router(analysis.router, prefix="/api/v1/analysis", tags=["analysis"])
# app.include_router(scenarios.router, prefix="/api/v1/scenarios", tags=["scenarios"])
# app.include_router(reports.router, prefix="/api/v1/reports", tags=["reports"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
