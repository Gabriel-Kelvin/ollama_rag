"""
Adapters for external services and APIs.
"""
from core.adapters.embedding_adapter import (
    EmbeddingAdapter,
    StubEmbeddingAdapter,
    RemoteEmbeddingAdapter,
    get_embedding_adapter
)
from core.adapters.llm_adapter import (
    LLMAdapter,
    StubLLMAdapter,
    RemoteLLMAdapter,
    get_llm_adapter
)
from core.adapters.vector_store_adapter import (
    VectorStoreAdapter,
    InMemoryVectorStoreAdapter,
    QdrantVectorStoreAdapter,
    get_vector_store_adapter
)

__all__ = [
    "EmbeddingAdapter",
    "StubEmbeddingAdapter",
    "RemoteEmbeddingAdapter",
    "get_embedding_adapter",
    "LLMAdapter",
    "StubLLMAdapter",
    "RemoteLLMAdapter",
    "get_llm_adapter",
    "VectorStoreAdapter",
    "InMemoryVectorStoreAdapter",
    "QdrantVectorStoreAdapter",
    "get_vector_store_adapter",
]

