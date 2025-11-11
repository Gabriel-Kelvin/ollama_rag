"""
Embedding adapter with stub and remote implementations.
"""
import hashlib
import logging
import time
from abc import ABC, abstractmethod
from typing import List
import httpx
from core.utils.config import get_settings

logger = logging.getLogger(__name__)


class EmbeddingAdapter(ABC):
    """Abstract base class for embedding adapters."""
    
    @abstractmethod
    def embed(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List of embedding vectors (each vector is a list of floats)
        """
        pass


class StubEmbeddingAdapter(EmbeddingAdapter):
    """Stub embedding adapter that returns hash-based fixed-length vectors."""
    
    def __init__(self, vector_dim: int = 768):
        """
        Initialize stub adapter.
        
        Args:
            vector_dim: Dimension of the embedding vectors (default: 768)
        """
        self.vector_dim = vector_dim
    
    def embed(self, texts: List[str]) -> List[List[float]]:
        """
        Generate hash-based embeddings for texts.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List of embedding vectors
        """
        embeddings = []
        
        for text in texts:
            # Create hash-based embedding
            embedding = self._text_to_vector(text)
            embeddings.append(embedding)
        
        return embeddings
    
    def _text_to_vector(self, text: str) -> List[float]:
        """
        Convert text to a fixed-length vector using hash-based approach.
        
        Args:
            text: Text to convert
            
        Returns:
            Vector of floats
        """
        # Use SHA256 hash for deterministic but pseudo-random vectors
        hash_obj = hashlib.sha256(text.encode('utf-8'))
        hash_bytes = hash_obj.digest()
        
        # Convert hash bytes to vector
        vector = []
        for i in range(0, len(hash_bytes), 4):
            # Take 4 bytes at a time and convert to float in [-1, 1]
            if i + 4 <= len(hash_bytes):
                value = int.from_bytes(hash_bytes[i:i+4], byteorder='big')
                # Normalize to [-1, 1] range
                normalized = (value / (2**32 - 1)) * 2 - 1
                vector.append(normalized)
            
            if len(vector) >= self.vector_dim:
                break
        
        # Pad or truncate to exact dimension
        while len(vector) < self.vector_dim:
            # Use additional hash rounds for padding
            hash_obj.update(str(len(vector)).encode('utf-8'))
            hash_bytes = hash_obj.digest()
            value = int.from_bytes(hash_bytes[:4], byteorder='big')
            normalized = (value / (2**32 - 1)) * 2 - 1
            vector.append(normalized)
        
        return vector[:self.vector_dim]


class RemoteEmbeddingAdapter(EmbeddingAdapter):
    """Remote embedding adapter that calls Ollama API."""
    
    def __init__(self, max_retries: int = 3, retry_delay: float = 1.0, timeout: float = None):
        """
        Initialize remote adapter.
        
        Args:
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds
            timeout: Request timeout in seconds (per-embedding)
        """
        self.settings = get_settings()
        self.ollama_url = self.settings.ollama_url
        self.model = self.settings.embed_model
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.timeout = timeout or self.settings.ollama_timeout
        self.client = httpx.Client(timeout=self.timeout)
    
    def embed(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings using Ollama API with retry logic.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List of embedding vectors
            
        Raises:
            Exception: If all retry attempts fail
        """
        # Parallelize with limited workers to speed up large uploads
        from concurrent.futures import ThreadPoolExecutor, as_completed

        max_workers = min(8, max(2, len(texts)//8 or 2))
        results = [None] * len(texts)
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_idx = {executor.submit(self._embed_with_retry, t): i for i, t in enumerate(texts)}
            for future in as_completed(future_to_idx):
                i = future_to_idx[future]
                results[i] = future.result()
        return results
    
    def _embed_with_retry(self, text: str) -> List[float]:
        """
        Embed a single text with retry logic.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
            
        Raises:
            Exception: If all retry attempts fail
        """
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                return self._call_ollama_api(text)
            except (httpx.TimeoutException, httpx.NetworkError) as e:
                last_error = e
                if attempt < self.max_retries - 1:
                    wait_time = self.retry_delay * (2 ** attempt)  # Exponential backoff
                    logger.warning(
                        f"Embedding request failed (attempt {attempt + 1}/{self.max_retries}): {str(e)}. "
                        f"Retrying in {wait_time:.1f}s..."
                    )
                    time.sleep(wait_time)
                else:
                    logger.error(f"All embedding retry attempts failed: {str(e)}")
            except httpx.HTTPStatusError as e:
                # Don't retry on HTTP errors (4xx, 5xx)
                logger.error(f"HTTP error from Ollama API: {e.response.status_code} - {e.response.text}")
                raise Exception(f"Ollama API error: {e.response.status_code} - {e.response.text}")
            except Exception as e:
                # Don't retry on other errors
                logger.error(f"Unexpected error in embedding request: {str(e)}")
                raise
        
        # If we get here, all retries failed
        raise Exception(f"Failed to get embedding after {self.max_retries} attempts: {str(last_error)}")
    
    def _call_ollama_api(self, text: str) -> List[float]:
        """
        Call Ollama API synchronously.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        payload = {
            "model": self.model,
            "prompt": text
        }
        
        response = self.client.post(
            f"{self.ollama_url}/api/embeddings",
            json=payload
        )
        response.raise_for_status()
        result = response.json()
        
        # Extract embedding from response
        embedding = result.get("embedding", [])
        if not embedding and isinstance(result, list):
            embedding = result
        elif not embedding:
            raise Exception(f"Invalid response format from Ollama API: {result}")
        
        return embedding
    
    def close(self):
        """Close the HTTP client."""
        self.client.close()


def get_embedding_adapter() -> EmbeddingAdapter:
    """
    Factory function to get the appropriate embedding adapter based on config.
    
    Returns:
        EmbeddingAdapter instance (StubEmbeddingAdapter or RemoteEmbeddingAdapter)
    """
    settings = get_settings()
    
    if settings.use_nomic and not settings.demo_stub_mode:
        logger.info("Using remote Ollama embedding adapter")
        return RemoteEmbeddingAdapter()
    else:
        logger.info("Using stub embedding adapter (demo mode)")
        return StubEmbeddingAdapter()

