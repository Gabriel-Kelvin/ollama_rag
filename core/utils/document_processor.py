"""
Utilities for processing various document formats.
"""
from pathlib import Path
from typing import List, Dict
import PyPDF2
from docx import Document


class DocumentProcessor:
    """Process documents into chunks."""
    
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def process(self, file_path: str) -> List[Dict]:
        """
        Process a document file into chunks.
        
        Args:
            file_path: Path to the document file
            
        Returns:
            List of chunks with text and metadata
        """
        file_path_obj = Path(file_path)
        extension = file_path_obj.suffix.lower()
        
        if extension == ".pdf":
            text = self._extract_pdf(file_path)
        elif extension in [".docx", ".doc"]:
            text = self._extract_docx(file_path)
        elif extension == ".txt":
            text = self._extract_txt(file_path)
        else:
            raise ValueError(f"Unsupported file type: {extension}")
        
        chunks = self._chunk_text(text, file_path_obj.name)
        return chunks
    
    def _extract_pdf(self, file_path: str) -> str:
        """Extract text from PDF file."""
        text = ""
        with open(file_path, "rb") as f:
            pdf_reader = PyPDF2.PdfReader(f)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text
    
    def _extract_docx(self, file_path: str) -> str:
        """Extract text from DOCX file."""
        doc = Document(file_path)
        text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return text
    
    def _extract_txt(self, file_path: str) -> str:
        """Extract text from TXT file."""
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    
    def _chunk_text(self, text: str, source: str) -> List[Dict]:
        """Split text into overlapping chunks."""
        chunks = []
        words = text.split()
        
        for i in range(0, len(words), self.chunk_size - self.chunk_overlap):
            chunk_words = words[i:i + self.chunk_size]
            chunk_text = " ".join(chunk_words)
            
            chunks.append({
                "text": chunk_text,
                "metadata": {
                    "source": source,
                    "chunk_index": len(chunks),
                    "start_index": i
                }
            })
        
        return chunks

