"""
Text chunking utilities for breaking text into smaller parts.
"""
from typing import List, Dict, Optional
from core.utils.config import get_settings


def chunk_text(
    text: str,
    chunk_size: Optional[int] = None,
    chunk_overlap: Optional[int] = None,
    metadata: Optional[Dict] = None
) -> List[Dict[str, any]]:
    """
    Break text into overlapping chunks.
    
    Args:
        text: Text to chunk
        chunk_size: Size of each chunk (in characters). Uses config default if None.
        chunk_overlap: Overlap between chunks (in characters). Uses config default if None.
        metadata: Optional metadata to attach to each chunk
        
    Returns:
        List of chunk dictionaries with 'text' and 'metadata' keys
    """
    # Get defaults from config if not provided
    settings = get_settings()
    chunk_size = chunk_size or settings.chunk_size
    chunk_overlap = chunk_overlap or settings.chunk_overlap
    
    if not text or len(text) <= chunk_size:
        # Text is smaller than chunk size, return as single chunk
        return [{
            "text": text,
            "metadata": {
                **(metadata or {}),
                "chunk_index": 0,
                "start_pos": 0,
                "end_pos": len(text)
            }
        }]
    
    chunks = []
    start = 0
    chunk_index = 0
    
    while start < len(text):
        # Calculate end position
        end = start + chunk_size
        
        # Extract chunk
        chunk_text = text[start:end]
        
        # Create chunk metadata
        chunk_metadata = {
            **(metadata or {}),
            "chunk_index": chunk_index,
            "start_pos": start,
            "end_pos": min(end, len(text))
        }
        
        chunks.append({
            "text": chunk_text,
            "metadata": chunk_metadata
        })
        
        # Move start position with overlap
        start = end - chunk_overlap
        chunk_index += 1
        
        # Prevent infinite loop if overlap >= chunk_size
        if chunk_overlap >= chunk_size:
            start += 1
    
    return chunks


def chunk_text_by_words(
    text: str,
    chunk_size: Optional[int] = None,
    chunk_overlap: Optional[int] = None,
    metadata: Optional[Dict] = None
) -> List[Dict[str, any]]:
    """
    Break text into overlapping chunks by words (preserves word boundaries).
    
    Args:
        text: Text to chunk
        chunk_size: Number of words per chunk. Uses config default if None.
        chunk_overlap: Number of overlapping words. Uses config default if None.
        metadata: Optional metadata to attach to each chunk
        
    Returns:
        List of chunk dictionaries with 'text' and 'metadata' keys
    """
    # Get defaults from config if not provided
    settings = get_settings()
    # Convert character-based config to approximate word count
    # Average word length is ~5 characters, so divide by 5
    chunk_size = chunk_size or (settings.chunk_size // 5)
    chunk_overlap = chunk_overlap or (settings.chunk_overlap // 5)
    
    words = text.split()
    
    if len(words) <= chunk_size:
        # Text is smaller than chunk size, return as single chunk
        return [{
            "text": text,
            "metadata": {
                **(metadata or {}),
                "chunk_index": 0,
                "word_start": 0,
                "word_end": len(words)
            }
        }]
    
    chunks = []
    start = 0
    chunk_index = 0
    
    while start < len(words):
        # Calculate end position
        end = start + chunk_size
        
        # Extract chunk words
        chunk_words = words[start:end]
        chunk_text = " ".join(chunk_words)
        
        # Create chunk metadata
        chunk_metadata = {
            **(metadata or {}),
            "chunk_index": chunk_index,
            "word_start": start,
            "word_end": min(end, len(words))
        }
        
        chunks.append({
            "text": chunk_text,
            "metadata": chunk_metadata
        })
        
        # Move start position with overlap
        start = end - chunk_overlap
        chunk_index += 1
        
        # Prevent infinite loop if overlap >= chunk_size
        if chunk_overlap >= chunk_size:
            start += 1
    
    return chunks


def chunk_text_by_sentences(
    text: str,
    sentences_per_chunk: int = 5,
    metadata: Optional[Dict] = None
) -> List[Dict[str, any]]:
    """
    Break text into chunks by sentences.
    
    Args:
        text: Text to chunk
        sentences_per_chunk: Number of sentences per chunk
        metadata: Optional metadata to attach to each chunk
        
    Returns:
        List of chunk dictionaries with 'text' and 'metadata' keys
    """
    # Simple sentence splitting by periods, exclamation, question marks
    import re
    sentences = re.split(r'[.!?]+\s+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    if len(sentences) <= sentences_per_chunk:
        return [{
            "text": text,
            "metadata": {
                **(metadata or {}),
                "chunk_index": 0,
                "sentence_start": 0,
                "sentence_end": len(sentences)
            }
        }]
    
    chunks = []
    for i in range(0, len(sentences), sentences_per_chunk):
        chunk_sentences = sentences[i:i + sentences_per_chunk]
        chunk_text = ". ".join(chunk_sentences) + "."
        
        chunks.append({
            "text": chunk_text,
            "metadata": {
                **(metadata or {}),
                "chunk_index": len(chunks),
                "sentence_start": i,
                "sentence_end": min(i + sentences_per_chunk, len(sentences))
            }
        })
    
    return chunks

