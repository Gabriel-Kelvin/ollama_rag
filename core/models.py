"""
Shared data models for the application.
"""
from typing import Optional
from pydantic import BaseModel, Field


class DocumentMeta(BaseModel):
    """Metadata for a document."""
    
    id: str = Field(description="Unique document identifier")
    kb_name: str = Field(description="Knowledge base name")
    filename: str = Field(description="Original filename")
    bytes: int = Field(description="File size in bytes", ge=0)
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "doc_123",
                "kb_name": "kb_default",
                "filename": "example.pdf",
                "bytes": 102400
            }
        }


class Chunk(BaseModel):
    """A document chunk with optional vector embedding."""
    
    id: str = Field(description="Unique chunk identifier")
    text: str = Field(description="Chunk text content")
    vector: Optional[list[float]] = Field(
        default=None,
        description="Vector embedding for the chunk"
    )
    metadata: Optional[dict] = Field(
        default=None,
        description="Additional metadata (source, chunk_index, etc.)"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "chunk_123",
                "text": "This is a sample chunk of text.",
                "vector": [0.1, 0.2, 0.3, ...],
                "metadata": {
                    "source": "example.pdf",
                    "chunk_index": 0
                }
            }
        }


class RetrievalResult(BaseModel):
    """Result from vector similarity search."""
    
    text: str = Field(description="Retrieved text content")
    score: float = Field(description="Similarity score", ge=0.0, le=1.0)
    doc_id: str = Field(description="Source document identifier")
    metadata: Optional[dict] = Field(
        default=None,
        description="Additional metadata from the source document"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "This is a retrieved chunk of text.",
                "score": 0.85,
                "doc_id": "doc_123",
                "metadata": {
                    "source": "example.pdf",
                    "chunk_index": 0
                }
            }
        }

