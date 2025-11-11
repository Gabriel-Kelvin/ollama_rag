"""
Service for vector store operations using ChromaDB.
"""
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Optional
from core.adapters.ollama_adapter import OllamaAdapter
from core.utils.config import get_settings


class VectorStoreService:
    """Service for managing vector store operations."""
    
    def __init__(self):
        self.persist_dir = get_settings().chroma_persist_dir
        self.client = chromadb.PersistentClient(
            path=self.persist_dir,
            settings=Settings(anonymized_telemetry=False)
        )
        self.ollama = OllamaAdapter()
    
    async def create_collection(self, collection_name: str):
        """Create a new collection (knowledge base)."""
        try:
            self.client.get_or_create_collection(name=collection_name)
        except Exception as e:
            raise Exception(f"Error creating collection: {str(e)}")
    
    async def add_documents(self, documents: List[Dict], collection_name: str):
        """
        Add documents to a collection.
        
        Args:
            documents: List of dicts with 'text' and 'metadata' keys
            collection_name: Name of the collection
        """
        collection = self.client.get_or_create_collection(name=collection_name)
        
        texts = [doc["text"] for doc in documents]
        metadatas = [doc.get("metadata", {}) for doc in documents]
        ids = [f"{collection_name}_{i}" for i in range(len(documents))]
        
        # Generate embeddings using Ollama
        embeddings = []
        for text in texts:
            embedding = await self.ollama.embed(text)
            embeddings.append(embedding)
        
        collection.add(
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas,
            ids=ids
        )
    
    async def search(self, query: str, collection_name: str, top_k: int = 5) -> List[Dict]:
        """
        Search for similar documents in a collection.
        
        Args:
            query: Search query
            collection_name: Name of the collection
            top_k: Number of results to return
            
        Returns:
            List of similar documents with metadata
        """
        collection = self.client.get_or_create_collection(name=collection_name)
        
        # Generate query embedding
        query_embedding = await self.ollama.embed(query)
        
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
        
        # Format results
        formatted_results = []
        if results["documents"] and len(results["documents"][0]) > 0:
            for i in range(len(results["documents"][0])):
                formatted_results.append({
                    "text": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                    "distance": results["distances"][0][i] if results["distances"] else None
                })
        
        return formatted_results
    
    def list_collections(self) -> List[str]:
        """List all collections (knowledge bases)."""
        collections = self.client.list_collections()
        return [col.name for col in collections]

