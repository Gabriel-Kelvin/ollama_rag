"""
RAG service combining retrieval and LLM generation.
"""
import logging
from typing import List, Dict, Any, Optional
from core.adapters import get_llm_adapter
from core.services.retrieval_service import RetrievalService
from core.utils.config import get_settings

logger = logging.getLogger(__name__)


class RAGService:
    """Service for RAG (Retrieval-Augmented Generation) operations."""
    
    def __init__(self):
        self.llm_adapter = get_llm_adapter()
        self.retrieval_service = RetrievalService()
        self.settings = get_settings()
        logger.info("🤖 RAG Service initialized")
    
    def query(
        self,
        question: str,
        kb_name: str,
        top_k: int = None
    ) -> Dict[str, Any]:
        """
        Perform RAG query: retrieve context and generate answer.
        
        Args:
            question: User question
            kb_name: Knowledge base name
            top_k: Number of context snippets to retrieve (uses config default if None)
            
        Returns:
            Dictionary with answer, sources, and metadata
        """
        top_k = top_k or self.settings.top_k
        
        logger.info(f"🤖 Starting RAG query for KB: {kb_name}")
        logger.info(f"   Question: {question[:100]}{'...' if len(question) > 100 else ''}")
        logger.info(f"   Top K: {top_k}")
        
        # Step 1: Retrieve relevant context
        logger.info("   Step 1/3: Retrieving relevant context...")
        retrieval_results = self.retrieval_service.retrieve(question, kb_name, top_k)
        logger.info(f"   ✓ Retrieved {len(retrieval_results)} context snippets")
        
        # Step 2: Build prompt with context
        logger.info("   Step 2/3: Building prompt with context...")
        context_parts = []
        valid_context_count = 0
        max_chars_per_chunk = self.settings.ctx_chars_per_chunk
        
        for i, result in enumerate(retrieval_results, 1):
            text = result.get("text", "").strip()
            source = result.get("metadata", {}).get("filename", "Unknown")
            
            # Skip mock text or empty text
            # Check for various mock text patterns
            is_mock = (
                text.startswith("Mock text from") or
                text.startswith("Mock text") or
                "Install" in text and "for real" in text.lower() or
                (len(text) < 50 and ("mock" in text.lower() or "install" in text.lower()))
            )
            
            if not text or is_mock or len(text) < 10:
                logger.warning(f"   Skipping result {i} from {source}: empty or mock text (preview: {text[:100]})")
                continue
            
            # Trim each chunk to reduce prompt size
            trimmed = text[:max_chars_per_chunk] + ("..." if len(text) > max_chars_per_chunk else "")
            context_parts.append(f"[Context {i} from {source}]\n{trimmed}")
            valid_context_count += 1
            logger.debug(f"   Context {i} from {source}: {len(text)} chars")
        
        context = "\n\n".join(context_parts)
        
        if not context or valid_context_count == 0:
            logger.warning(f"   ⚠️ No valid context found! All {len(retrieval_results)} results were empty or mock text.")
            logger.warning(f"   This usually means documents were uploaded with mock parsers. Please re-upload documents.")
        
        # Build messages for LLM
        # Detect if this is a summarization request
        question_lower = question.lower()
        is_summarize = any(word in question_lower for word in ["summarize", "summary", "summarise", "brief", "overview", "what is", "what are"])
        
        if not context or valid_context_count == 0:
            system_message = "You are a helpful assistant."
            user_prompt = f"""The user asked: "{question}"

However, I could not retrieve any valid content from the documents in the knowledge base. This usually happens when:
1. Documents were uploaded with mock parsers (only "Mock text from filename" was stored)
2. Documents need to be re-uploaded with real text extraction
3. The documents are empty or couldn't be parsed

Please inform the user that they need to re-upload their documents to get real content extracted and indexed."""
        elif is_summarize and context:
            system_message = "You are an expert at summarizing documents. Provide clear, concise summaries based on the provided context. Keep your response focused and well-organized."
            # Limit context length for summarization to avoid timeout
            max_context_length = 4000  # Limit context to prevent very long prompts
            if len(context) > max_context_length:
                context = context[:max_context_length] + "\n\n[... context truncated for efficiency ...]"
            user_prompt = f"""Based on the following context from the documents, provide a comprehensive summary.

Context:
{context}

Please provide a well-structured summary that covers the main points, key information, and important details. Keep it concise but comprehensive."""
        else:
            system_message = "You are a helpful assistant that answers questions based on the provided context. Provide accurate, detailed answers using only the information from the context. If the context doesn't contain enough information to fully answer the question, say so clearly."
            user_prompt = f"""Context from documents:
{context}

Question: {question}

Please provide a detailed answer based on the context above. Use specific information from the documents when available. If the context doesn't contain enough information to answer the question completely, acknowledge what information is missing."""
        
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_prompt}
        ]
        
        logger.info(f"   ✓ Prompt built ({len(context)} chars of context)")
        
        # Step 3: Generate answer using LLM
        logger.info("   Step 3/3: Generating answer with LLM...")
        answer = self.llm_adapter.chat(messages)
        logger.info(f"   ✓ Answer generated ({len(answer)} chars)")
        
        # Format sources
        sources = []
        for result in retrieval_results:
            sources.append({
                "doc_id": result.get("doc_id", ""),
                "filename": result.get("metadata", {}).get("filename", ""),
                "score": result.get("score", 0.0),
                "chunk_index": result.get("metadata", {}).get("chunk_index", -1)
            })
        
        # Summary
        logger.info(f"✅ RAG query complete for KB: {kb_name}")
        logger.info(f"   - Answer length: {len(answer)} chars")
        logger.info(f"   - Sources: {len(sources)}")
        logger.info(f"   - Backend mode: {type(self.retrieval_service.vector_store).__name__}")
        logger.info(f"   - LLM mode: {type(self.llm_adapter).__name__}")
        
        return {
            "answer": answer,
            "sources": sources,
            "question": question,
            "kb_name": kb_name,
            "context_snippets": len(retrieval_results),
            "backend_mode": type(self.retrieval_service.vector_store).__name__,
            "llm_mode": type(self.llm_adapter).__name__
        }
