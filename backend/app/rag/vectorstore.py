"""
Vector Store Management
Handles Qdrant vector database operations
"""
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from langchain_community.vectorstores import Qdrant
from typing import List, Dict, Any, Optional
import logging

from app.config import settings
from app.rag.embeddings import get_embeddings

logger = logging.getLogger(__name__)


class VectorStoreManager:
    """Manages Qdrant vector store operations"""

    def __init__(self):
        self.client = QdrantClient(
            host=settings.QDRANT_HOST,
            port=settings.QDRANT_PORT,
        )
        self.collection_name = settings.QDRANT_COLLECTION_NAME
        self.embeddings = get_embeddings()

    def ensure_collection_exists(self, vector_size: int = 768):
        """
        Ensure the collection exists, create if it doesn't

        Args:
            vector_size: Size of embedding vectors (768 for nomic-embed-text)
        """
        try:
            collections = self.client.get_collections().collections
            collection_names = [c.name for c in collections]

            if self.collection_name not in collection_names:
                logger.info(f"Creating collection '{self.collection_name}'")
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=vector_size,
                        distance=Distance.COSINE
                    )
                )
                logger.info(f"Collection '{self.collection_name}' created successfully")
            else:
                logger.info(f"Collection '{self.collection_name}' already exists")
        except Exception as e:
            logger.error(f"Failed to ensure collection exists: {str(e)}")
            raise

    def get_vectorstore(self) -> Qdrant:
        """
        Get LangChain Qdrant vector store instance

        Returns:
            Qdrant vectorstore instance
        """
        return Qdrant(
            client=self.client,
            collection_name=self.collection_name,
            embeddings=self.embeddings,
        )

    def add_documents(
        self,
        texts: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None
    ) -> List[str]:
        """
        Add documents to the vector store

        Args:
            texts: List of text documents to add
            metadatas: Optional list of metadata dicts for each document

        Returns:
            List of document IDs
        """
        try:
            vectorstore = self.get_vectorstore()
            ids = vectorstore.add_texts(texts=texts, metadatas=metadatas)
            logger.info(f"Added {len(texts)} documents to vector store")
            return ids
        except Exception as e:
            logger.error(f"Failed to add documents: {str(e)}")
            raise

    def search(
        self,
        query: str,
        k: int = 5,
        filter: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents

        Args:
            query: Search query
            k: Number of results to return
            filter: Optional metadata filter

        Returns:
            List of search results with content and metadata
        """
        try:
            vectorstore = self.get_vectorstore()
            results = vectorstore.similarity_search_with_score(
                query=query,
                k=k,
                filter=filter
            )

            return [
                {
                    "content": doc.page_content,
                    "metadata": doc.metadata,
                    "score": score
                }
                for doc, score in results
            ]
        except Exception as e:
            logger.error(f"Search failed: {str(e)}")
            raise

    def get_collection_info(self) -> Dict[str, Any]:
        """
        Get information about the collection

        Returns:
            Dict with collection statistics
        """
        try:
            info = self.client.get_collection(self.collection_name)
            return {
                "name": self.collection_name,
                "vectors_count": info.vectors_count,
                "points_count": info.points_count,
                "status": info.status
            }
        except Exception as e:
            logger.error(f"Failed to get collection info: {str(e)}")
            raise


# Singleton instance
_vector_store_manager = None


def get_vector_store_manager() -> VectorStoreManager:
    """Get or create vector store manager singleton"""
    global _vector_store_manager
    if _vector_store_manager is None:
        _vector_store_manager = VectorStoreManager()
        _vector_store_manager.ensure_collection_exists()
    return _vector_store_manager
