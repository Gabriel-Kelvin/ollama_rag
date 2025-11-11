"""
Service for document processing and management.
"""
import os
from pathlib import Path
from typing import List, Dict
from core.utils.document_processor import DocumentProcessor


class DocumentService:
    """Service for handling document operations."""
    
    def __init__(self):
        self.upload_dir = Path("data/uploads")
        self.chunks_dir = Path("data/chunks")
        self.processor = DocumentProcessor()
    
    def save_uploaded_file(self, file_content: bytes, filename: str) -> str:
        """
        Save uploaded file to disk.
        
        Args:
            file_content: File content as bytes
            filename: Original filename
            
        Returns:
            Path to saved file
        """
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        file_path = self.upload_dir / filename
        
        with open(file_path, "wb") as f:
            f.write(file_content)
        
        return str(file_path)
    
    def process_document(self, file_path: str) -> List[Dict]:
        """
        Process document into chunks.
        
        Args:
            file_path: Path to document file
            
        Returns:
            List of document chunks with metadata
        """
        return self.processor.process(file_path)
    
    def list_documents(self) -> List[str]:
        """List all uploaded documents."""
        if not self.upload_dir.exists():
            return []
        return [f.name for f in self.upload_dir.iterdir() if f.is_file()]

