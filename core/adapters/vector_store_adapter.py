"""
Vector database adapter with in-memory and Qdrant implementations.
"""
import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
from core.utils.config import get_settings

logger = logging.getLogger(__name__)


class VectorStoreAdapter(ABC):
    """Abstract base class for vector store adapters."""
    
    @abstractmethod
    def ensure_kb(self, kb: str) -> None:
        """
        Ensure a knowledge base (collection) exists, creating it if necessary.
        
        Args:
            kb: Knowledge base name
        """
        pass
    
    @abstractmethod
    def upsert(self, kb: str, points: List[Dict[str, Any]]) -> None:
        """
        Insert or update points in a knowledge base.
        
        Args:
            kb: Knowledge base name
            points: List of point dictionaries with 'id', 'vector', 'payload' keys.
                    Example: [{"id": "1", "vector": [0.1, 0.2, ...], "payload": {"text": "...", "doc_id": "..."}}]
        """
        pass
    
    @abstractmethod
    def query(self, kb: str, vector: List[float], top_k: int) -> List[Dict[str, Any]]:
        """
        Query a knowledge base for similar vectors.
        
        Args:
            kb: Knowledge base name
            vector: Query vector
            top_k: Number of results to return
            
        Returns:
            List of result dictionaries with 'id', 'score', 'payload' keys
        """
        pass
    
    @abstractmethod
    def delete_doc(self, kb: str, doc_id: str) -> None:
        """
        Delete all points associated with a document.
        
        Args:
            kb: Knowledge base name
            doc_id: Document identifier
        """
        pass
    
    @abstractmethod
    def list_docs(self, kb: str) -> List[str]:
        """
        List all unique document IDs in a knowledge base.
        
        Args:
            kb: Knowledge base name
            
        Returns:
            List of document IDs
        """
        pass
    
    @abstractmethod
    def list_kbs(self) -> List[str]:
        """
        List all knowledge bases (collections).
        
        Returns:
            List of knowledge base names
        """
        pass
    
    @abstractmethod
    def delete_kb(self, kb: str) -> None:
        """
        Delete a knowledge base (collection).
        
        Args:
            kb: Knowledge base name
        """
        pass


class InMemoryVectorStoreAdapter(VectorStoreAdapter):
    """In-memory vector store adapter using Python dictionaries."""
    
    def __init__(self):
        """Initialize in-memory store."""
        self.collections: Dict[str, Dict[str, Dict[str, Any]]] = {}
        logger.info("🔷 Using IN-MEMORY vector store (demo mode)")
    
    def ensure_kb(self, kb: str) -> None:
        """Ensure knowledge base exists."""
        if kb not in self.collections:
            self.collections[kb] = {}
            logger.debug(f"Created in-memory knowledge base: {kb}")
    
    def upsert(self, kb: str, points: List[Dict[str, Any]]) -> None:
        """Insert or update points."""
        self.ensure_kb(kb)
        
        for point in points:
            point_id = point.get("id")
            if not point_id:
                raise ValueError("Point must have an 'id' field")
            
            self.collections[kb][point_id] = {
                "vector": point.get("vector", []),
                "payload": point.get("payload", {})
            }
        
        logger.debug(f"Upserted {len(points)} points to KB: {kb}")
    
    def query(self, kb: str, vector: List[float], top_k: int) -> List[Dict[str, Any]]:
        """Query for similar vectors using cosine similarity."""
        self.ensure_kb(kb)
        
        if not vector:
            return []
        
        # Calculate cosine similarity for all points
        results = []
        for point_id, point_data in self.collections[kb].items():
            stored_vector = point_data.get("vector", [])
            if not stored_vector or len(stored_vector) != len(vector):
                continue
            
            # Cosine similarity
            dot_product = sum(a * b for a, b in zip(vector, stored_vector))
            norm_a = sum(a * a for a in vector) ** 0.5
            norm_b = sum(b * b for b in stored_vector) ** 0.5
            
            if norm_a == 0 or norm_b == 0:
                score = 0.0
            else:
                score = dot_product / (norm_a * norm_b)
            
            results.append({
                "id": point_id,
                "score": score,
                "payload": point_data.get("payload", {})
            })
        
        # Sort by score (descending) and return top_k
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]
    
    def delete_doc(self, kb: str, doc_id: str) -> None:
        """Delete all points associated with a document."""
        self.ensure_kb(kb)
        
        deleted_count = 0
        points_to_delete = []
        
        for point_id, point_data in self.collections[kb].items():
            payload = point_data.get("payload", {})
            if payload.get("doc_id") == doc_id:
                points_to_delete.append(point_id)
        
        for point_id in points_to_delete:
            del self.collections[kb][point_id]
            deleted_count += 1
        
        logger.debug(f"Deleted {deleted_count} points for doc_id: {doc_id} from KB: {kb}")
    
    def list_docs(self, kb: str) -> List[str]:
        """List all unique document IDs."""
        self.ensure_kb(kb)
        
        doc_ids = set()
        for point_data in self.collections[kb].values():
            payload = point_data.get("payload", {})
            doc_id = payload.get("doc_id")
            if doc_id:
                doc_ids.add(doc_id)
        
        return sorted(list(doc_ids))
    
    def list_kbs(self) -> List[str]:
        """List all knowledge bases."""
        return sorted(list(self.collections.keys()))
    
    def delete_kb(self, kb: str) -> None:
        """Delete a knowledge base."""
        if kb in self.collections:
            del self.collections[kb]
            logger.info(f"Deleted in-memory knowledge base: {kb}")


class QdrantVectorStoreAdapter(VectorStoreAdapter):
    """Qdrant vector store adapter."""
    
    def __init__(self, vector_size: int = 768):
        """
        Initialize Qdrant adapter.
        
        Args:
            vector_size: Size of vectors (default: 768 for nomic-embed-text)
        """
        self.settings = get_settings()
        self.qdrant_url = self.settings.qdrant_url
        self.vector_size = vector_size
        
        try:
            self.client = QdrantClient(url=self.qdrant_url)
            logger.info(f"🔷 Using QDRANT vector store at {self.qdrant_url}")
        except Exception as e:
            logger.error(f"Failed to connect to Qdrant at {self.qdrant_url}: {str(e)}")
            raise
    
    def ensure_kb(self, kb: str) -> None:
        """Ensure knowledge base (collection) exists, creating if necessary."""
        try:
            # Check if collection exists
            collections = self.client.get_collections()
            collection_names = [col.name for col in collections.collections]
            
            if kb not in collection_names:
                # Create collection
                self.client.create_collection(
                    collection_name=kb,
                    vectors_config=VectorParams(
                        size=self.vector_size,
                        distance=Distance.COSINE
                    )
                )
                logger.info(f"Created Qdrant collection: {kb}")
            else:
                logger.debug(f"Qdrant collection already exists: {kb}")
        except Exception as e:
            logger.error(f"Error ensuring KB {kb}: {str(e)}")
            raise
    
    def upsert(self, kb: str, points: List[Dict[str, Any]]) -> None:
        """Insert or update points in Qdrant."""
        self.ensure_kb(kb)
        
        try:
            qdrant_points = []
            for point in points:
                point_id = point.get("id")
                vector = point.get("vector", [])
                payload = point.get("payload", {})
                
                if not point_id:
                    raise ValueError("Point must have an 'id' field")
                if not vector:
                    raise ValueError("Point must have a 'vector' field")
                
                # Convert point_id to int or str based on Qdrant requirements
                # Qdrant supports both int and str IDs
                try:
                    point_id_int = int(point_id) if point_id.isdigit() else point_id
                except (ValueError, AttributeError):
                    point_id_int = point_id
                
                qdrant_points.append(
                    PointStruct(
                        id=point_id_int,
                        vector=vector,
                        payload=payload
                    )
                )
            
            self.client.upsert(
                collection_name=kb,
                points=qdrant_points
            )
            logger.debug(f"Upserted {len(points)} points to Qdrant KB: {kb}")
        except Exception as e:
            logger.error(f"Error upserting to KB {kb}: {str(e)}")
            raise
    
    def query(self, kb: str, vector: List[float], top_k: int) -> List[Dict[str, Any]]:
        """Query Qdrant for similar vectors."""
        self.ensure_kb(kb)
        
        if not vector:
            return []
        
        try:
            search_results = self.client.search(
                collection_name=kb,
                query_vector=vector,
                limit=top_k
            )
            
            results = []
            for result in search_results:
                results.append({
                    "id": str(result.id),
                    "score": result.score,
                    "payload": result.payload or {}
                })
            
            return results
        except Exception as e:
            logger.error(f"Error querying KB {kb}: {str(e)}")
            raise
    
    def delete_doc(self, kb: str, doc_id: str) -> None:
        """Delete all points associated with a document."""
        self.ensure_kb(kb)
        
        try:
            # Qdrant doesn't have a direct "delete by payload" method
            # We need to search for points with the doc_id and delete them
            # First, get all points (this is a limitation - Qdrant doesn't support filtering in delete)
            # We'll use scroll to get all points with the doc_id
            
            # Scroll through all points with the doc_id filter
            scroll_result = self.client.scroll(
                collection_name=kb,
                scroll_filter=Filter(
                    must=[
                        FieldCondition(
                            key="doc_id",
                            match=MatchValue(value=doc_id)
                        )
                    ]
                ),
                limit=10000  # Adjust based on expected size
            )
            
            point_ids = [point.id for point in scroll_result[0]]
            
            if point_ids:
                self.client.delete(
                    collection_name=kb,
                    points_selector=point_ids
                )
                logger.debug(f"Deleted {len(point_ids)} points for doc_id: {doc_id} from KB: {kb}")
            else:
                logger.debug(f"No points found for doc_id: {doc_id} in KB: {kb}")
        except Exception as e:
            logger.error(f"Error deleting doc {doc_id} from KB {kb}: {str(e)}")
            raise
    
    def list_docs(self, kb: str) -> List[str]:
        """List all unique document IDs in a knowledge base."""
        self.ensure_kb(kb)
        
        try:
            # Scroll through all points to extract unique doc_ids
            doc_ids = set()
            offset = None
            
            while True:
                scroll_result = self.client.scroll(
                    collection_name=kb,
                    limit=100,
                    offset=offset
                )
                
                points, next_offset = scroll_result
                
                if not points:
                    break
                
                for point in points:
                    payload = point.payload or {}
                    doc_id = payload.get("doc_id")
                    if doc_id:
                        doc_ids.add(str(doc_id))
                
                if next_offset is None:
                    break
                
                offset = next_offset
            
            return sorted(list(doc_ids))
        except Exception as e:
            logger.error(f"Error listing docs from KB {kb}: {str(e)}")
            raise
    
    def list_kbs(self) -> List[str]:
        """List all knowledge bases (collections)."""
        try:
            collections = self.client.get_collections()
            collection_names = [col.name for col in collections.collections]
            return sorted(collection_names)
        except Exception as e:
            logger.error(f"Error listing knowledge bases: {str(e)}")
            raise
    
    def delete_kb(self, kb: str) -> None:
        """Delete a knowledge base (collection)."""
        try:
            # Check if collection exists
            collections = self.client.get_collections()
            collection_names = [col.name for col in collections.collections]
            
            if kb in collection_names:
                self.client.delete_collection(kb)
                logger.info(f"Deleted Qdrant collection: {kb}")
            else:
                logger.warning(f"Collection {kb} does not exist")
        except Exception as e:
            logger.error(f"Error deleting KB {kb}: {str(e)}")
            raise


def get_vector_store_adapter() -> VectorStoreAdapter:
    """
    Factory function to get the appropriate vector store adapter based on config.
    
    Returns:
        VectorStoreAdapter instance (InMemoryVectorStoreAdapter or QdrantVectorStoreAdapter)
    """
    settings = get_settings()
    
    if settings.use_qdrant and not settings.demo_stub_mode:
        logger.info("Initializing Qdrant vector store adapter")
        return QdrantVectorStoreAdapter()
    else:
        logger.info("Initializing in-memory vector store adapter (demo mode)")
        return InMemoryVectorStoreAdapter()

