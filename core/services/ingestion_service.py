"""
Ingestion service for processing and indexing documents.
"""
import logging
import uuid
from pathlib import Path
from typing import List, Dict, Any
from core.adapters import get_embedding_adapter, get_vector_store_adapter
from core.utils.file_utils import save_uploaded_file, get_file_size
from core.utils.parsing_utils import parse_file
from core.utils.chunking_utils import chunk_text
from core.utils.config import get_settings

logger = logging.getLogger(__name__)


class IngestionService:
    """Service for ingesting documents into the knowledge base."""
    
    def __init__(self):
        self.embedding_adapter = get_embedding_adapter()
        self.vector_store = get_vector_store_adapter()
        self.settings = get_settings()
        logger.info("📦 Ingestion Service initialized")
    
    def ingest_file(
        self,
        file_content: bytes,
        filename: str,
        kb_name: str,
        doc_id: str = None
    ) -> Dict[str, Any]:
        """
        Complete ingestion pipeline: save → parse → chunk → embed → upsert.
        
        Args:
            file_content: File content as bytes
            filename: Original filename
            kb_name: Knowledge base name
            doc_id: Optional document ID (generated if not provided)
            
        Returns:
            Dictionary with ingestion results (doc_id, chunks_count, etc.)
        """
        # Generate doc_id if not provided
        if not doc_id:
            doc_id = str(uuid.uuid4())
        
        logger.info(f"🚀 Starting ingestion for KB: {kb_name}, File: {filename}")
        logger.info(f"   Document ID: {doc_id}")
        
        # Step 1: Save uploaded file
        logger.info("   Step 1/5: Saving file...")
        file_path = save_uploaded_file(file_content, filename, kb_name)
        file_size = get_file_size(file_path)
        logger.info(f"   ✓ File saved: {file_path} ({file_size} bytes)")
        
        # Step 2: Parse file
        logger.info("   Step 2/5: Parsing file...")
        text = parse_file(file_path)
        logger.info(f"   ✓ Parsed text length: {len(text)} characters")
        
        # Warn if mock text detected
        if text and text.startswith("Mock text from"):
            logger.warning(f"   ⚠️ WARNING: Mock text detected! Parser libraries may not be installed or backend needs restart.")
            logger.warning(f"   ⚠️ Parsed text preview: {text[:100]}...")
        elif text and len(text) < 100:
            logger.warning(f"   ⚠️ Very short text extracted ({len(text)} chars). File might be empty or parsing failed.")
            logger.warning(f"   ⚠️ Text preview: {text}")
        else:
            logger.info(f"   ✓ Real text extracted. Preview: {text[:200]}...")
        
        # Step 3: Chunk text
        logger.info("   Step 3/5: Chunking text...")
        chunks = chunk_text(
            text,
            chunk_size=self.settings.chunk_size,
            chunk_overlap=self.settings.chunk_overlap,
            metadata={"source": filename, "doc_id": doc_id}
        )
        logger.info(f"   ✓ Created {len(chunks)} chunks")
        
        # Step 4: Generate embeddings
        logger.info("   Step 4/5: Generating embeddings...")
        texts_to_embed = [chunk["text"] for chunk in chunks]
        embeddings = self.embedding_adapter.embed(texts_to_embed)
        logger.info(f"   ✓ Generated {len(embeddings)} embeddings (dim: {len(embeddings[0]) if embeddings else 0})")
        
        # Step 5: Upsert to vector store
        logger.info("   Step 5/5: Upserting to vector store...")
        self.vector_store.ensure_kb(kb_name)
        
        points = []
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            # Generate unique point ID (Qdrant accepts UUIDs or integers)
            # Use UUID for better uniqueness
            point_id = str(uuid.uuid4())
            points.append({
                "id": point_id,
                "vector": embedding,
                "payload": {
                    "text": chunk["text"],
                    "doc_id": doc_id,
                    "filename": filename,
                    "chunk_index": i,
                    **chunk.get("metadata", {})
                }
            })
        
        self.vector_store.upsert(kb_name, points)
        logger.info(f"   ✓ Upserted {len(points)} points to KB: {kb_name}")
        
        # Summary
        logger.info(f"✅ Ingestion complete for KB: {kb_name}")
        logger.info(f"   - Document ID: {doc_id}")
        logger.info(f"   - Chunks: {len(chunks)}")
        logger.info(f"   - Points: {len(points)}")
        logger.info(f"   - Backend mode: {type(self.vector_store).__name__}")
        
        return {
            "doc_id": doc_id,
            "filename": filename,
            "kb_name": kb_name,
            "chunks_count": len(chunks),
            "points_count": len(points),
            "file_size": file_size,
            "backend_mode": type(self.vector_store).__name__
        }

