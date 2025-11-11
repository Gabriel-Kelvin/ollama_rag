"""
Configuration management using dotenv and Pydantic settings.
"""
import logging
from pathlib import Path
from functools import lru_cache
from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

# Load .env file automatically
env_path = Path(__file__).parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Qdrant Configuration
    qdrant_url: str = Field(default="http://47.129.127.169:6333", description="Qdrant server URL")
    
    # Ollama Configuration
    ollama_url: str = Field(default="http://47.129.127.169:11434", description="Ollama server URL", env="OLLAMA_URL")
    ollama_base_url: str = Field(default="", description="Ollama base URL (alias for ollama_url)", env="OLLAMA_BASE_URL")
    
    # Model Configuration
    embed_model: str = Field(default="nomic-embed-text", description="Embedding model name")
    chat_model: str = Field(default="llama3.2", description="Chat model name")
    
    # Knowledge Base Configuration
    default_collection: str = Field(default="kb_default", description="Default collection name")
    
    # Chunking Configuration
    chunk_size: int = Field(default=800, description="Chunk size for document processing", env="CHUNK_SIZE")
    chunk_overlap: int = Field(default=120, description="Chunk overlap size", env="CHUNK_OVERLAP")
    ctx_chars_per_chunk: int = Field(default=600, description="Max characters from each retrieved chunk added to prompt", env="CTX_CHARS_PER_CHUNK")
    
    # Retrieval Configuration
    top_k: int = Field(default=5, description="Number of top results to retrieve", env="TOP_K")

    # Timeouts / Generation
    ollama_timeout: int = Field(default=300, description="Timeout (seconds) for Ollama requests", env="OLLAMA_TIMEOUT")
    gen_max_tokens: int = Field(default=192, description="Max tokens to generate from LLM", env="GEN_MAX_TOKENS")
    
    # Feature Flags
    use_qdrant: bool = Field(default=True, description="Use Qdrant vector database")
    use_ollama: bool = Field(default=True, description="Use Ollama for LLM")
    use_nomic: bool = Field(default=True, description="Use Nomic embeddings")
    demo_stub_mode: bool = Field(default=False, description="Use stub mode for demos")
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    def model_post_init(self, __context):
        """Post-initialization hook to validate URLs and log warnings."""
        # Use OLLAMA_BASE_URL if provided, otherwise use OLLAMA_URL
        if self.ollama_base_url:
            self.ollama_url = self.ollama_base_url
        
        # Check and warn if localhost is used
        if "localhost" in self.qdrant_url.lower() or "127.0.0.1" in self.qdrant_url:
            logger.warning(
                f"⚠️  Localhost detected in QDRANT_URL: {self.qdrant_url}\n"
                f"   Consider using the remote server at http://47.129.127.169:6333 instead."
            )
        if "localhost" in self.ollama_url.lower() or "127.0.0.1" in self.ollama_url:
            logger.warning(
                f"⚠️  Localhost detected in OLLAMA_URL: {self.ollama_url}\n"
                f"   Consider using the remote server at http://47.129.127.169:11434 instead."
            )


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    
    Returns:
        Settings: Cached settings instance
    """
    return Settings()

