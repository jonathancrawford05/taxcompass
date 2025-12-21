"""
Retrievers for RAG
Provides context retrieval from vector store
"""
from typing import List, Dict, Any, Optional
import logging

from app.rag.vectorstore import get_vector_store_manager

logger = logging.getLogger(__name__)


class TaxLawRetriever:
    """Retrieves relevant tax law context for queries"""

    def __init__(self, k: int = 5):
        """
        Initialize retriever

        Args:
            k: Number of documents to retrieve
        """
        self.k = k
        self.vector_store = get_vector_store_manager()

    async def retrieve(
        self,
        query: str,
        country: Optional[str] = None,
        k: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant tax law documents

        Args:
            query: Query string describing what to search for
            country: Optional country filter (e.g., "CA" for Canada)
            k: Optional override for number of results

        Returns:
            List of relevant documents with metadata
        """
        num_results = k or self.k

        # Build filter if country specified
        filter_dict = None
        if country:
            filter_dict = {"country": country}

        try:
            results = self.vector_store.search(
                query=query,
                k=num_results,
                filter=filter_dict
            )

            logger.info(
                f"Retrieved {len(results)} documents for query: '{query[:50]}...'"
            )

            return results
        except Exception as e:
            logger.error(f"Retrieval failed: {str(e)}")
            return []

    def format_context(self, results: List[Dict[str, Any]]) -> str:
        """
        Format retrieved documents into context string for LLM

        Args:
            results: List of retrieved documents

        Returns:
            Formatted context string
        """
        if not results:
            return "No relevant tax law context found."

        context_parts = []
        for i, result in enumerate(results, 1):
            metadata = result.get("metadata", {})
            source = metadata.get("source", "Unknown")
            country = metadata.get("country", "Unknown")

            context_parts.append(
                f"[Document {i} - {country} - {source}]\n"
                f"{result['content']}\n"
            )

        return "\n---\n".join(context_parts)
