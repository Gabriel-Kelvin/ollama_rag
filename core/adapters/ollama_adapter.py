"""
Adapter for interacting with the remote Ollama server.
"""
import httpx
from typing import Optional, Dict, Any
from core.utils.config import get_settings


class OllamaAdapter:
    """Adapter for Ollama API interactions."""
    
    def __init__(self):
        self.base_url = get_settings().ollama_base_url
        self.model = get_settings().ollama_model
        self.client = httpx.AsyncClient(timeout=60.0)
    
    async def generate(self, prompt: str, context: Optional[str] = None) -> str:
        """
        Generate text using Ollama.
        
        Args:
            prompt: The user prompt
            context: Optional context to include in the prompt
            
        Returns:
            Generated text response
        """
        full_prompt = f"{context}\n\n{prompt}" if context else prompt
        
        payload = {
            "model": self.model,
            "prompt": full_prompt,
            "stream": False
        }
        
        try:
            response = await self.client.post(
                f"{self.base_url}/api/generate",
                json=payload
            )
            response.raise_for_status()
            result = response.json()
            return result.get("response", "")
        except httpx.HTTPError as e:
            raise Exception(f"Error calling Ollama API: {str(e)}")
    
    async def embed(self, text: str) -> list[float]:
        """
        Generate embeddings for text using Ollama.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        payload = {
            "model": self.model,
            "prompt": text
        }
        
        try:
            response = await self.client.post(
                f"{self.base_url}/api/embeddings",
                json=payload
            )
            response.raise_for_status()
            result = response.json()
            # Ollama returns embedding in 'embedding' field
            embedding = result.get("embedding", [])
            if not embedding:
                # Fallback: try to get from response directly
                embedding = result if isinstance(result, list) else []
            return embedding
        except httpx.HTTPError as e:
            raise Exception(f"Error calling Ollama embeddings API: {str(e)}")
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

