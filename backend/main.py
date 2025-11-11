"""
FastAPI backend main application.
"""
import logging
from fastapi import FastAPI, UploadFile, File, HTTPException, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import httpx

from core.services.ingestion_service import IngestionService
from core.services.retrieval_service import RetrievalService
from core.services.rag_service import RAGService
from core.adapters import get_vector_store_adapter, get_llm_adapter, get_embedding_adapter
from core.utils.config import get_settings
from backend.auth import verify_token

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Ollama RAG API", version="1.0.0")

# CORS middleware - allow all origins for demo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
ingestion_service = IngestionService()
retrieval_service = RetrievalService()
rag_service = RAGService()
vector_store = get_vector_store_adapter()
settings = get_settings()


def delete_vectors_by_filename(kb_name: str, filename: str) -> int:
    """
    Helper function to delete all vectors for a given filename from the vector store.
    Returns the number of vectors deleted.
    """
    from qdrant_client.models import Filter, FieldCondition, MatchValue
    
    deleted_count = 0
    adapter_type = type(vector_store).__name__
    
    if adapter_type == "QdrantVectorStoreAdapter":
        # Method 1: Try using filter
        all_points_to_delete = []
        try:
            offset = None
            while True:
                scroll_result = vector_store.client.scroll(
                    collection_name=kb_name,
                    scroll_filter=Filter(
                        must=[
                            FieldCondition(
                                key="filename",
                                match=MatchValue(value=filename)
                            )
                        ]
                    ),
                    limit=100,
                    offset=offset
                )
                
                points, next_offset = scroll_result
                if points:
                    all_points_to_delete.extend([point.id for point in points])
                if next_offset is None:
                    break
                offset = next_offset
        except Exception:
            # Method 2: Manual search fallback
            offset = None
            while True:
                scroll_all = vector_store.client.scroll(
                    collection_name=kb_name,
                    limit=100,
                    offset=offset
                )
                points, next_offset = scroll_all
                if points:
                    for point in points:
                        payload = point.payload or {}
                        if payload.get("filename", "") == filename:
                            all_points_to_delete.append(point.id)
                if next_offset is None:
                    break
                offset = next_offset
        
        # Delete in batches
        if all_points_to_delete:
            batch_size = 100
            for i in range(0, len(all_points_to_delete), batch_size):
                batch = all_points_to_delete[i:i + batch_size]
                try:
                    vector_store.client.delete(
                        collection_name=kb_name,
                        points_selector=batch,
                        wait=True
                    )
                    deleted_count += len(batch)
                except Exception as e:
                    logger.warning(f"Error deleting batch: {str(e)}")
    else:
        # In-memory adapter
        doc_ids = set()
        if hasattr(vector_store, 'collections') and kb_name in vector_store.collections:
            for point_data in vector_store.collections[kb_name].values():
                payload = point_data.get("payload", {})
                if payload.get("filename") == filename:
                    doc_id = payload.get("doc_id")
                    if doc_id:
                        doc_ids.add(doc_id)
        for doc_id in doc_ids:
            vector_store.delete_doc(kb_name, doc_id)
        deleted_count = len(doc_ids)
    
    return deleted_count


# Request/Response models
class CreateKBRequest(BaseModel):
    name: str


class DeleteKBRequest(BaseModel):
    name: str


class IndexRequest(BaseModel):
    kb_name: str
    filename: str


class RetrieveRequest(BaseModel):
    query: str
    kb_name: str
    top_k: Optional[int] = None


class ChatRequest(BaseModel):
    kb_name: str
    query: str  # Frontend sends 'query' not 'question'
    history: Optional[List[Dict[str, str]]] = []
    top_k: Optional[int] = None


class HealthResponse(BaseModel):
    status: str
    ollama: Dict[str, Any]
    qdrant: Dict[str, Any]
    backend_mode: str


# API Endpoints
@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Ollama RAG API", "status": "running", "version": "1.0.0"}


@app.get("/parser-status")
async def parser_status():
    """Check if document parsers are available."""
    from core.utils.parsing_utils import PDF_AVAILABLE, DOCX_AVAILABLE
    
    return {
        "pdf_parser": "available" if PDF_AVAILABLE else "not available (install pypdf2)",
        "docx_parser": "available" if DOCX_AVAILABLE else "not available (install python-docx)",
        "note": "If parsers show as 'not available' but packages are installed, restart the backend server."
    }


@app.get("/debug/file-text/{kb_name}/{filename:path}")
async def debug_file_text(kb_name: str, filename: str):
    """Debug endpoint to see what text is actually stored for a file."""
    from urllib.parse import unquote
    from core.utils.file_utils import get_file_path
    from core.utils.parsing_utils import parse_file
    from qdrant_client.models import Filter, FieldCondition, MatchValue
    
    filename = unquote(filename)
    logger.info(f"🔍 Debug: Checking text for file: {filename} in KB: {kb_name}")
    
    result = {
        "filename": filename,
        "kb_name": kb_name,
        "file_exists": False,
        "file_path": None,
        "parsed_text_preview": None,
        "parsed_text_length": 0,
        "vectors_in_store": [],
        "is_mock_text": False
    }
    
    # Check if file exists on disk
    file_path = get_file_path(filename, kb_name)
    if file_path:
        result["file_exists"] = True
        result["file_path"] = file_path
        
        # Try to parse it now
        try:
            parsed_text = parse_file(file_path)
            result["parsed_text_length"] = len(parsed_text) if parsed_text else 0
            result["parsed_text_preview"] = parsed_text[:500] if parsed_text else None
            result["is_mock_text"] = parsed_text.startswith("Mock text from") if parsed_text else False
        except Exception as e:
            result["parse_error"] = str(e)
    
    # Check what's in the vector store
    try:
        adapter_type = type(vector_store).__name__
        if adapter_type == "QdrantVectorStoreAdapter":
            offset = None
            sample_texts = []
            while len(sample_texts) < 3:
                scroll_result = vector_store.client.scroll(
                    collection_name=kb_name,
                    scroll_filter=Filter(
                        must=[
                            FieldCondition(
                                key="filename",
                                match=MatchValue(value=filename)
                            )
                        ]
                    ),
                    limit=3,
                    offset=offset
                )
                points, next_offset = scroll_result
                if points:
                    for point in points:
                        payload = point.payload or {}
                        text = payload.get("text", "")
                        sample_texts.append({
                            "point_id": str(point.id),
                            "text_preview": text[:200] if text else "",
                            "text_length": len(text) if text else 0,
                            "is_mock": text.startswith("Mock text from") if text else False
                        })
                if next_offset is None:
                    break
                offset = next_offset
            
            result["vectors_in_store"] = sample_texts
            result["vector_count"] = len(sample_texts)
    except Exception as e:
        result["vector_store_error"] = str(e)
    
    return result


@app.get("/health", response_model=HealthResponse)
async def health():
    """
    Health check endpoint that verifies connections to Ollama and Qdrant.
    """
    logger.info("🔍 Health check requested")
    
    ollama_status = {"status": "unknown", "url": settings.ollama_url}
    qdrant_status = {"status": "unknown", "url": settings.qdrant_url}
    
    # Check Ollama if enabled
    if settings.use_ollama:
        try:
            client = httpx.Client(timeout=5.0)
            response = client.get(f"{settings.ollama_url}/api/tags")
            if response.status_code == 200:
                ollama_status = {
                    "status": "connected",
                    "url": settings.ollama_url,
                    "model": settings.chat_model
                }
            else:
                ollama_status = {
                    "status": "error",
                    "url": settings.ollama_url,
                    "error": f"HTTP {response.status_code}"
                }
        except Exception as e:
            ollama_status = {
                "status": "error",
                "url": settings.ollama_url,
                "error": str(e)
            }
    else:
        ollama_status = {"status": "disabled", "url": settings.ollama_url}
    
    # Check Qdrant if enabled
    if settings.use_qdrant:
        try:
            vector_store.ensure_kb("health_check_temp")
            qdrant_status = {
                "status": "connected",
                "url": settings.qdrant_url
            }
            # Clean up test collection
            try:
                # Note: Qdrant client doesn't have a direct delete_collection method in all versions
                # We'll just leave it or handle it gracefully
                pass
            except:
                pass
        except Exception as e:
            qdrant_status = {
                "status": "error",
                "url": settings.qdrant_url,
                "error": str(e)
            }
    else:
        qdrant_status = {"status": "disabled", "url": settings.qdrant_url}
    
    overall_status = "healthy" if (
        ollama_status.get("status") in ["connected", "disabled"] and
        qdrant_status.get("status") in ["connected", "disabled"]
    ) else "degraded"
    
    return HealthResponse(
        status=overall_status,
        ollama=ollama_status,
        qdrant=qdrant_status,
        backend_mode=type(vector_store).__name__
    )


@app.get("/knowledge-bases")
async def list_knowledge_bases(user: dict = Depends(verify_token)):
    """List all knowledge bases."""
    logger.info(f"📚 Listing knowledge bases for user {user.get('email')}")
    try:
        from core.utils.file_utils import list_kb_files
        
        # Get all collections from vector store
        kb_list = vector_store.list_kbs()
        
        # Don't auto-create default KB - let users start with empty list
        # Users can create their own KBs as needed
        
        # Format response to match frontend expectations with actual document counts
        kbs = []
        for kb_name in kb_list:
            try:
                # Count actual files in the KB
                files = list_kb_files(kb_name)
                doc_count = len(files)
            except:
                doc_count = 0
            
            kbs.append({
                "name": kb_name,
                "created_at": None,
                "doc_count": doc_count
            })
        
        return kbs
    except Exception as e:
        logger.error(f"Error listing knowledge bases: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/knowledge-bases/{kb_name}/files")
async def list_kb_files(kb_name: str):
    """List all files in a knowledge base."""
    logger.info(f"📁 Listing files in KB: {kb_name}")
    try:
        from core.utils.file_utils import list_kb_files
        
        # Get files from disk
        disk_files = list_kb_files(kb_name)
        
        # Also get files from vector store to check for orphaned vectors
        vector_files = set()
        try:
            adapter_type = type(vector_store).__name__
            if adapter_type == "QdrantVectorStoreAdapter":
                offset = None
                while True:
                    scroll_result = vector_store.client.scroll(
                        collection_name=kb_name,
                        limit=100,
                        offset=offset
                    )
                    points, next_offset = scroll_result
                    if points:
                        for point in points:
                            payload = point.payload or {}
                            stored_filename = payload.get("filename", "")
                            if stored_filename:
                                vector_files.add(stored_filename)
                    if next_offset is None:
                        break
                    offset = next_offset
        except Exception as e:
            logger.warning(f"Could not check vector store for files: {str(e)}")
        
        # Find orphaned files (in vector store but not on disk)
        orphaned = list(vector_files - set(disk_files))
        
        return {
            "kb_name": kb_name,
            "files": disk_files,
            "vector_store_files": list(vector_files),
            "orphaned_vectors": orphaned
        }
    except Exception as e:
        logger.error(f"Error listing files: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/knowledge-bases/{kb_name}/cleanup-orphaned")
async def cleanup_orphaned_vectors(kb_name: str):
    """
    Clean up orphaned vectors (vectors in store but files deleted from disk).
    """
    logger.info(f"🧹 Cleaning up orphaned vectors in KB: {kb_name}")
    try:
        from core.utils.file_utils import list_kb_files
        from qdrant_client.models import Filter, FieldCondition, MatchValue
        
        # Get files from disk
        disk_files = set(list_kb_files(kb_name))
        
        # Get all files from vector store
        adapter_type = type(vector_store).__name__
        if adapter_type != "QdrantVectorStoreAdapter":
            return {"message": "Cleanup only supported for Qdrant", "deleted": 0}
        
        orphaned_files = set()
        all_points = []
        offset = None
        
        while True:
            scroll_result = vector_store.client.scroll(
                collection_name=kb_name,
                limit=100,
                offset=offset
            )
            points, next_offset = scroll_result
            if points:
                for point in points:
                    payload = point.payload or {}
                    stored_filename = payload.get("filename", "")
                    if stored_filename and stored_filename not in disk_files:
                        orphaned_files.add(stored_filename)
                        all_points.append((point.id, stored_filename))
            if next_offset is None:
                break
            offset = next_offset
        
        # Delete orphaned vectors
        deleted_count = 0
        if all_points:
            points_to_delete = [pid for pid, fname in all_points if fname in orphaned_files]
            if points_to_delete:
                batch_size = 100
                for i in range(0, len(points_to_delete), batch_size):
                    batch = points_to_delete[i:i + batch_size]
                    vector_store.client.delete(
                        collection_name=kb_name,
                        points_selector=batch,
                        wait=True
                    )
                    deleted_count += len(batch)
        
        return {
            "message": f"Cleanup complete",
            "orphaned_files": list(orphaned_files),
            "deleted_vectors": deleted_count
        }
    except Exception as e:
        logger.error(f"Error cleaning up orphaned vectors: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/knowledge-bases/{kb_name}/files/{filename:path}")
async def delete_kb_file(kb_name: str, filename: str):
    """
    Delete a file from a knowledge base.
    Uses {filename:path} to handle special characters in filenames.
    """
    # URL decode the filename in case it was encoded
    from urllib.parse import unquote
    filename = unquote(filename)
    logger.info(f"🗑️ Deleting file: {filename} from KB: {kb_name}")
    try:
        from core.utils.file_utils import delete_kb_file, get_file_path
        from qdrant_client.models import Filter, FieldCondition, MatchValue
        
        # Check if file exists
        file_path = get_file_path(filename, kb_name)
        if not file_path:
            raise HTTPException(status_code=404, detail=f"File '{filename}' not found in KB '{kb_name}'")
        
        # Delete from vector store - find all points with this filename and delete them
        logger.info(f"   Deleting vectors for file: {filename}")
        try:
            deleted_count = delete_vectors_by_filename(kb_name, filename)
            if deleted_count > 0:
                logger.info(f"   ✓ Successfully deleted {deleted_count} vectors from vector store")
            else:
                logger.warning(f"   ⚠️ No vectors found for filename: '{filename}'")
        except Exception as e:
            logger.warning(f"   Error deleting from vector store (continuing with file deletion): {str(e)}")
        
        # Delete file from disk
        success = delete_kb_file(filename, kb_name)
        
        if success:
            return {
                "message": f"File '{filename}' deleted successfully",
                "filename": filename,
                "kb_name": kb_name
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to delete file")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting file: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/knowledge-bases", status_code=201)
async def create_knowledge_base(request: CreateKBRequest, user: dict = Depends(verify_token)):
    """Create a new knowledge base."""
    logger.info(f"📚 Creating knowledge base: {request.name} for user {user.get('email')}")
    try:
        vector_store.ensure_kb(request.name)
        return {
            "message": f"Knowledge base '{request.name}' created successfully",
            "kb_name": request.name
        }
    except Exception as e:
        logger.error(f"Error creating knowledge base: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/knowledge-bases/{kb_name}")
async def delete_knowledge_base(kb_name: str, user: dict = Depends(verify_token)):
    """Delete a knowledge base completely including all data."""
    logger.info(f"🗑️ Deleting knowledge base: {kb_name} for user {user.get('email')}")
    try:
        # First, delete from vector store
        try:
            vector_store.delete_kb(kb_name)
            logger.info(f"   ✓ Deleted collection from vector store: {kb_name}")
        except Exception as e:
            logger.warning(f"   ⚠️ Error deleting from vector store: {str(e)}")
        
        # Delete the directory and all files
        from pathlib import Path
        import shutil
        
        kb_dir = Path("data/uploads") / kb_name
        if kb_dir.exists():
            shutil.rmtree(kb_dir)
            logger.info(f"   ✓ Deleted directory: {kb_dir}")
        
        # Also delete chunks directory if it exists
        chunks_dir = Path("data/chunks") / kb_name
        if chunks_dir.exists():
            shutil.rmtree(chunks_dir)
            logger.info(f"   ✓ Deleted chunks directory: {chunks_dir}")
        
        logger.info(f"✓ Successfully deleted knowledge base: {kb_name}")
        
        return {
            "message": f"Knowledge base '{kb_name}' deleted successfully",
            "kb_name": kb_name,
            "deleted": True
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting knowledge base: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/uploads/{kb_name}")
async def get_uploaded_files(kb_name: str, user: dict = Depends(verify_token)):
    """Get all uploaded files for a knowledge base."""
    logger.info(f"📁 Getting uploaded files for KB: {kb_name}")
    try:
        from core.utils.file_utils import list_kb_files
        from pathlib import Path
        
        disk_files = list_kb_files(kb_name)
        
        # Format response with file details
        files = []
        for filename in disk_files:
            file_path = Path("data/uploads") / kb_name / filename
            if file_path.exists():
                files.append({
                    "filename": filename,
                    "size": file_path.stat().st_size,
                    "kb_name": kb_name,
                    "upload_date": None
                })
        
        return files
    except Exception as e:
        logger.error(f"Error getting uploaded files: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/uploads/{kb_name}/{filename:path}")
async def delete_uploaded_file(kb_name: str, filename: str, user: dict = Depends(verify_token)):
    """Delete an uploaded file and its vectors."""
    logger.info(f"🗑️ Deleting file: {filename} from KB: {kb_name}")
    try:
        from pathlib import Path
        
        # Delete vectors
        deleted = delete_vectors_by_filename(kb_name, filename)
        logger.info(f"   Deleted {deleted} vectors")
        
        # Delete file from disk
        file_path = Path("data/uploads") / kb_name / filename
        if file_path.exists():
            file_path.unlink()
            logger.info(f"   Deleted file from disk")
        
        return {"message": f"File '{filename}' deleted successfully", "vectors_deleted": deleted}
    except Exception as e:
        logger.error(f"Error deleting file: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/indexed/{kb_name}")
async def get_indexed_documents(kb_name: str, user: dict = Depends(verify_token)):
    """Get list of indexed documents in a knowledge base."""
    logger.info(f"📇 Getting indexed documents for KB: {kb_name}")
    try:
        # Get unique filenames from vector store
        indexed_files = set()
        adapter_type = type(vector_store).__name__
        
        if adapter_type == "QdrantVectorStoreAdapter":
            try:
                offset = None
                while True:
                    scroll_result = vector_store.client.scroll(
                        collection_name=kb_name,
                        limit=100,
                        offset=offset,
                        with_payload=True
                    )
                    points, next_offset = scroll_result
                    
                    for point in points:
                        if point.payload and "filename" in point.payload:
                            indexed_files.add(point.payload["filename"])
                    
                    if next_offset is None:
                        break
                    offset = next_offset
            except Exception as e:
                logger.warning(f"Could not get indexed files: {str(e)}")
        
        return {"documents": list(indexed_files)}
    except Exception as e:
        logger.error(f"Error getting indexed documents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    kb_name: Optional[str] = Form(None),
    user: dict = Depends(verify_token)
):
    """
    Upload a file to a knowledge base and automatically index it.
    kb_name can be provided as a form field or defaults to default_collection.
    """
    # Handle empty string or None
    if not kb_name or kb_name.strip() == "":
        kb_name = settings.default_collection
    else:
        kb_name = kb_name.strip()
    
    logger.info(f"📤 Uploading and indexing file: {file.filename} to KB: {kb_name}")
    logger.info(f"   Received kb_name form field: {kb_name}")
    
    try:
        content = await file.read()
        
        # Upload and index in one step
        result = ingestion_service.ingest_file(
            file_content=content,
            filename=file.filename,
            kb_name=kb_name
        )
        
        return {
            "message": "File uploaded and indexed successfully",
            "filename": file.filename,
            "kb_name": kb_name,
            "doc_id": result["doc_id"],
            "chunks_count": result["chunks_count"],
            "points_count": result["points_count"],
            "file_size": result["file_size"]
        }
    except Exception as e:
        logger.error(f"Error uploading/indexing file: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/index")
async def index_file(request: IndexRequest, user: dict = Depends(verify_token)):
    """
    Re-index a file using the ingestion service.
    This will delete old vectors for the file and create new ones with current parsers.
    """
    logger.info(f"📇 Re-indexing file: {request.filename} in KB: {request.kb_name} for user {user.get('email')}")
    
    try:
        # Read the file content
        from core.utils.file_utils import get_file_path
        file_path = get_file_path(request.filename, request.kb_name)
        
        if not file_path:
            raise HTTPException(
                status_code=404,
                detail=f"File '{request.filename}' not found in KB '{request.kb_name}'"
            )
        
        # Delete old vectors for this file first
        logger.info(f"   Deleting old vectors for: {request.filename}")
        deleted_count = delete_vectors_by_filename(request.kb_name, request.filename)
        if deleted_count > 0:
            logger.info(f"   ✓ Deleted {deleted_count} old vectors")
        
        with open(file_path, "rb") as f:
            file_content = f.read()
        
        # Call ingestion service to create new vectors
        result = ingestion_service.ingest_file(
            file_content=file_content,
            filename=request.filename,
            kb_name=request.kb_name
        )
        
        return {
            "message": "File re-indexed successfully",
            "doc_id": result["doc_id"],
            "chunks_count": result["chunks_count"],
            "points_count": result["points_count"],
            "old_vectors_deleted": deleted_count,
            "kb_name": request.kb_name,
            "filename": request.filename
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error indexing file: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/retrieve")
async def retrieve(request: RetrieveRequest, user: dict = Depends(verify_token)):
    """
    Retrieve relevant documents for a query.
    """
    logger.info(f"🔍 Retrieving for query in KB: {request.kb_name} for user {user.get('email')}")
    
    try:
        results = retrieval_service.retrieve(
            query=request.query,
            kb_name=request.kb_name,
            top_k=request.top_k
        )
        
        return {
            "query": request.query,
            "kb_name": request.kb_name,
            "results": results,
            "count": len(results)
        }
    except Exception as e:
        logger.error(f"Error retrieving: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat")
async def chat(request: ChatRequest, user: dict = Depends(verify_token)):
    """
    Run full RAG process: retrieve context and generate answer.
    """
    logger.info(f"💬 Chat request for KB: {request.kb_name} for user {user.get('email')}")
    
    try:
        result = rag_service.query(
            question=request.query,
            kb_name=request.kb_name,
            top_k=request.top_k or 3
        )
        
        # Format response to match frontend expectations
        contexts = []
        if "sources" in result:
            for source in result["sources"]:
                contexts.append({
                    "text": source.get("text", ""),
                    "filename": source.get("filename", ""),
                    "score": source.get("score", 0.0)
                })
        
        return {
            "response": result["answer"],
            "contexts": contexts,
            "kb_name": request.kb_name
        }
    except Exception as e:
        logger.error(f"Error in chat: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
