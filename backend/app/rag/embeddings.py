"""
Embeddings configuration for RAG
Handles text embeddings using Ollama
"""
from langchain_community.embeddings import OllamaEmbeddings
from app.config import settings
import logging

logger = logging.getLogger(__name__)


def get_embeddings():
    """
    Get embeddings model for vector store
    Uses Ollama with nomic-embed-text model

    Returns:
        Embeddings instance
    """
    try:
        embeddings = OllamaEmbeddings(
            base_url=settings.OLLAMA_BASE_URL,
            model="nomic-embed-text",
        )
        logger.info("Initialized Ollama embeddings with nomic-embed-text")
        return embeddings
    except Exception as e:
        logger.error(f"Failed to initialize embeddings: {str(e)}")
        raise
