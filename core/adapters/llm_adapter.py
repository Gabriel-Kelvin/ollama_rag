"""
LLM adapter with stub and remote implementations.
"""
import logging
import time
from abc import ABC, abstractmethod
from typing import List, Dict
import httpx
from core.utils.config import get_settings

logger = logging.getLogger(__name__)


class LLMAdapter(ABC):
    """Abstract base class for LLM adapters."""
    
    @abstractmethod
    def chat(self, messages: List[Dict[str, str]]) -> str:
        """
        Generate a chat response from a list of messages.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content' keys.
                     Example: [{"role": "user", "content": "Hello"}]
        
        Returns:
            Response string from the LLM
        """
        pass


class StubLLMAdapter(LLMAdapter):
    """Stub LLM adapter that returns a simulated response."""
    
    def chat(self, messages: List[Dict[str, str]]) -> str:
        """
        Return a simulated AI response.
        
        Args:
            messages: List of message dictionaries
            
        Returns:
            Simulated response string
        """
        return "This is a simulated AI response."


class RemoteLLMAdapter(LLMAdapter):
    """Remote LLM adapter that calls Ollama API."""
    
    def __init__(self, max_retries: int = 3, retry_delay: float = 1.0, timeout: float = None):
        """
        Initialize remote adapter.
        
        Args:
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds
            timeout: Request timeout in seconds (default: 5 minutes for LLM generation)
        """
        self.settings = get_settings()
        self.ollama_url = self.settings.ollama_url
        self.model = self.settings.chat_model
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.timeout = timeout or self.settings.ollama_timeout
        self.client = httpx.Client(timeout=self.timeout)
    
    def chat(self, messages: List[Dict[str, str]]) -> str:
        """
        Generate chat response using Ollama API with retry logic.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content' keys
        
        Returns:
            Response string from the LLM
            
        Raises:
            Exception: If all retry attempts fail
        """
        return self._chat_with_retry(messages)
    
    def _chat_with_retry(self, messages: List[Dict[str, str]]) -> str:
        """
        Call Ollama chat API with retry logic.
        
        Args:
            messages: List of message dictionaries
            
        Returns:
            Response string
            
        Raises:
            Exception: If all retry attempts fail
        """
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                return self._call_ollama_chat_api(messages)
            except (httpx.TimeoutException, httpx.NetworkError) as e:
                last_error = e
                if attempt < self.max_retries - 1:
                    wait_time = self.retry_delay * (2 ** attempt)  # Exponential backoff
                    logger.warning(
                        f"Chat request failed (attempt {attempt + 1}/{self.max_retries}): {str(e)}. "
                        f"Retrying in {wait_time:.1f}s..."
                    )
                    time.sleep(wait_time)
                else:
                    logger.error(f"All chat retry attempts failed: {str(e)}")
            except httpx.HTTPStatusError as e:
                # Don't retry on HTTP errors (4xx, 5xx)
                logger.error(f"HTTP error from Ollama API: {e.response.status_code} - {e.response.text}")
                raise Exception(f"Ollama API error: {e.response.status_code} - {e.response.text}")
            except Exception as e:
                # Don't retry on other errors
                logger.error(f"Unexpected error in chat request: {str(e)}")
                raise
        
        # If we get here, all retries failed
        raise Exception(f"Failed to get chat response after {self.max_retries} attempts: {str(last_error)}")
    
    def _call_ollama_chat_api(self, messages: List[Dict[str, str]]) -> str:
        """
        Call Ollama chat API synchronously.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content' keys
            
        Returns:
            Response string from the LLM
        """
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "num_predict": self.settings.gen_max_tokens
            }
        }
        
        response = self.client.post(
            f"{self.ollama_url}/api/chat",
            json=payload
        )
        response.raise_for_status()
        result = response.json()
        
        # Extract message content from response
        # Ollama chat API returns: {"message": {"role": "assistant", "content": "..."}, ...}
        message = result.get("message", {})
        content = message.get("content", "")
        
        if not content:
            raise Exception(f"Invalid response format from Ollama API: {result}")
        
        return content
    
    def close(self):
        """Close the HTTP client."""
        self.client.close()


def get_llm_adapter() -> LLMAdapter:
    """
    Factory function to get the appropriate LLM adapter based on config.
    
    Returns:
        LLMAdapter instance (StubLLMAdapter or RemoteLLMAdapter)
    """
    settings = get_settings()
    
    if settings.use_ollama and not settings.demo_stub_mode:
        logger.info("Using remote Ollama LLM adapter")
        return RemoteLLMAdapter()
    else:
        logger.info("Using stub LLM adapter (demo mode)")
        return StubLLMAdapter()

