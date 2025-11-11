"""
File utility functions for managing uploaded files.
"""
import os
import shutil
from pathlib import Path
from typing import List, Optional


def save_uploaded_file(file_content: bytes, filename: str, kb_name: str = "default") -> str:
    """
    Save an uploaded file to the knowledge base directory.
    
    Args:
        file_content: File content as bytes
        filename: Original filename
        kb_name: Knowledge base name (creates subdirectory)
        
    Returns:
        Path to saved file
    """
    # Create KB-specific directory
    kb_dir = Path("data/uploads") / kb_name
    kb_dir.mkdir(parents=True, exist_ok=True)
    
    # Save file
    file_path = kb_dir / filename
    
    with open(file_path, "wb") as f:
        f.write(file_content)
    
    return str(file_path)


def list_kb_files(kb_name: str = "default") -> List[str]:
    """
    List all files in a knowledge base directory.
    
    Args:
        kb_name: Knowledge base name
        
    Returns:
        List of filenames
    """
    kb_dir = Path("data/uploads") / kb_name
    
    if not kb_dir.exists():
        return []
    
    files = []
    for file_path in kb_dir.iterdir():
        if file_path.is_file():
            files.append(file_path.name)
    
    return sorted(files)


def delete_kb_file(filename: str, kb_name: str = "default") -> bool:
    """
    Delete a file from a knowledge base directory.
    
    Args:
        filename: Name of file to delete
        kb_name: Knowledge base name
        
    Returns:
        True if file was deleted, False if not found
    """
    kb_dir = Path("data/uploads") / kb_name
    file_path = kb_dir / filename
    
    if file_path.exists() and file_path.is_file():
        file_path.unlink()
        return True
    
    return False


def get_file_path(filename: str, kb_name: str = "default") -> Optional[str]:
    """
    Get the full path to a file in a knowledge base.
    
    Args:
        filename: Name of the file
        kb_name: Knowledge base name
        
    Returns:
        Full path to file, or None if not found
    """
    kb_dir = Path("data/uploads") / kb_name
    file_path = kb_dir / filename
    
    if file_path.exists() and file_path.is_file():
        return str(file_path)
    
    return None


def get_file_size(filepath: str) -> int:
    """
    Get file size in bytes.
    
    Args:
        filepath: Path to file
        
    Returns:
        File size in bytes
    """
    file_path = Path(filepath)
    if file_path.exists():
        return file_path.stat().st_size
    return 0

