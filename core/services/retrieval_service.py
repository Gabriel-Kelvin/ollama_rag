"""
Retrieval service for querying the knowledge base.
"""
import logging
from typing import List, Dict, Any
from core.adapters import get_embedding_adapter, get_vector_store_adapter
from core.utils.config import get_settings

logger = logging.getLogger(__name__)


class RetrievalService:
    """Service for retrieving relevant documents from the knowledge base."""
    
    def __init__(self):
        self.embedding_adapter = get_embedding_adapter()
        self.vector_store = get_vector_store_adapter()
        self.settings = get_settings()
        logger.info("🔍 Retrieval Service initialized")
    
    def retrieve(self, query: str, kb_name: str, top_k: int = None) -> List[Dict[str, Any]]:
        """
        Retrieve relevant documents for a query.
        
        Args:
            query: Search query text
            kb_name: Knowledge base name
            top_k: Number of results to return (uses config default if None)
            
        Returns:
            List of retrieval results with text, score, doc_id, and metadata
        """
        top_k = top_k or self.settings.top_k
        
        logger.info(f"🔍 Starting retrieval for KB: {kb_name}")
        logger.info(f"   Query: {query[:100]}{'...' if len(query) > 100 else ''}")
        logger.info(f"   Top K: {top_k}")
        
        # Step 1: Ensure KB exists
        logger.info("   Step 1/3: Ensuring knowledge base exists...")
        self.vector_store.ensure_kb(kb_name)
        logger.info(f"   ✓ KB ready: {kb_name}")
        
        # Step 2: Generate query embedding
        logger.info("   Step 2/3: Generating query embedding...")
        query_embeddings = self.embedding_adapter.embed([query])
        query_vector = query_embeddings[0]
        logger.info(f"   ✓ Query embedding generated (dim: {len(query_vector)})")
        
        # Step 3: Search vector store
        logger.info("   Step 3/3: Searching vector store...")
        search_results = self.vector_store.query(kb_name, query_vector, top_k)
        logger.info(f"   ✓ Found {len(search_results)} results")
        
        # Format results
        formatted_results = []
        for i, result in enumerate(search_results):
            text = result.get("payload", {}).get("text", "")
            filename = result.get("payload", {}).get("filename", "")
            
            formatted_result = {
                "text": text,
                "score": result.get("score", 0.0),
                "doc_id": result.get("payload", {}).get("doc_id", ""),
                "metadata": {
                    "filename": filename,
                    "chunk_index": result.get("payload", {}).get("chunk_index", -1),
                    "point_id": result.get("id", ""),
                    **result.get("payload", {})
                }
            }
            formatted_results.append(formatted_result)
            
            # Log text preview to help debug
            text_preview = text[:50] + "..." if len(text) > 50 else text
            logger.debug(f"   Result {i+1}: score={formatted_result['score']:.4f}, filename={filename}, text_preview='{text_preview}'")
            
            # Warn if mock text detected
            if text.startswith("Mock text from"):
                logger.warning(f"   ⚠️ Result {i+1} contains mock text! File needs to be re-uploaded.")
        
        # Summary
        logger.info(f"✅ Retrieval complete for KB: {kb_name}")
        logger.info(f"   - Results: {len(formatted_results)}")
        logger.info(f"   - Backend mode: {type(self.vector_store).__name__}")
        
        return formatted_results

