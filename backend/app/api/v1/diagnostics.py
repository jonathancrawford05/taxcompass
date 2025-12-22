"""
System diagnostics endpoint
Tests each component of the system
"""
import logging
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models import User
from app.rag.vectorstore import get_vector_store_manager
from app.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/diagnostics")
async def system_diagnostics(db: Session = Depends(get_db)):
    """
    Check all system components
    """
    results = {
        "database": "unknown",
        "vector_store": "unknown",
        "ollama": "unknown",
        "demo_user": "unknown",
        "errors": []
    }

    # Test database
    try:
        user_count = db.query(User).count()
        results["database"] = f"connected ({user_count} users)"
    except Exception as e:
        results["database"] = "failed"
        results["errors"].append(f"Database: {str(e)}")

    # Test vector store
    try:
        vs_manager = get_vector_store_manager()
        info = vs_manager.get_collection_info()
        results["vector_store"] = f"connected ({info.get('points_count', 0)} documents)"
    except Exception as e:
        results["vector_store"] = "failed"
        results["errors"].append(f"Vector Store: {str(e)}")

    # Test Ollama
    try:
        from langchain_community.llms import Ollama
        llm = Ollama(
            base_url=settings.OLLAMA_BASE_URL,
            model=settings.OLLAMA_MODEL,
            timeout=5
        )
        response = llm.invoke("Test")
        results["ollama"] = "connected"
    except Exception as e:
        results["ollama"] = "failed"
        results["errors"].append(f"Ollama: {str(e)}")

    # Check demo user
    try:
        demo_user = db.query(User).filter(User.email == "demo@taxcompass.io").first()
        if demo_user:
            results["demo_user"] = f"exists (id: {demo_user.id})"
        else:
            results["demo_user"] = "not created yet"
    except Exception as e:
        results["errors"].append(f"Demo User: {str(e)}")

    results["overall_status"] = "healthy" if not results["errors"] else "degraded"

    return results
