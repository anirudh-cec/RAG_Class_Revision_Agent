"""
Chat Service - Orchestrates chat conversations with RAG
"""

from typing import List, Dict, Any, Optional, AsyncGenerator
import uuid
from datetime import datetime

from src.retrieval.services.retrieval_service import RetrievalService
from src.retrieval.services.llm_service import LLMService
from src.retrieval.models.responses import ChatMessage, SourceCitation


class ChatService:
    """
    Service for managing chat conversations with RAG
    """

    def __init__(
        self,
        retrieval_service: RetrievalService,
        llm_service: LLMService
    ):
        self.retrieval_service = retrieval_service
        self.llm_service = llm_service
        self._conversations: Dict[str, List[ChatMessage]] = {}

    async def chat(
        self,
        query: str,
        conversation_id: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
        top_k: int = 5
    ) -> Dict[str, Any]:
        """
        Process a chat query with RAG

        Args:
            query: User query
            conversation_id: Optional conversation ID
            filters: Metadata filters
            top_k: Number of results

        Returns:
            Dict with answer, sources, and conversation_id
        """
        # Generate or use conversation ID
        conv_id = conversation_id or str(uuid.uuid4())

        # 1. Retrieve relevant documents
        search_results = await self.retrieval_service.hybrid_search(
            query=query,
            top_k=top_k,
            filters=filters
        )

        # 2. Format context and sources
        context = []
        sources = []
        for result in search_results:
            context.append({
                "content": result.content,
                "source": result.document_id
            })
            sources.append({
                "chunk_id": result.chunk_id,
                "document_id": result.document_id,
                "score": result.score,
                "reranked_score": result.reranked_score
            })

        # 3. Generate response
        answer = await self.llm_service.generate_response(
            query=query,
            context=context
        )

        # 4. Store in conversation history
        if conv_id not in self._conversations:
            self._conversations[conv_id] = []

        self._conversations[conv_id].append(ChatMessage(
            role="user",
            content=query,
            timestamp=datetime.now().isoformat()
        ))

        self._conversations[conv_id].append(ChatMessage(
            role="assistant",
            content=answer,
            timestamp=datetime.now().isoformat(),
            sources=[SourceCitation(**s) for s in sources]
        ))

        return {
            "conversation_id": conv_id,
            "answer": answer,
            "sources": sources
        }

    async def stream_chat(
        self,
        query: str,
        conversation_id: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
        top_k: int = 5
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Stream a chat response with RAG

        Yields:
            Dict with type and data (sources, token, done)
        """
        conv_id = conversation_id or str(uuid.uuid4())

        # 1. Retrieve documents
        search_results = await self.retrieval_service.hybrid_search(
            query=query,
            top_k=top_k,
            filters=filters
        )

        # 2. Format context and sources
        context = []
        sources = []
        for result in search_results:
            context.append({
                "content": result.content,
                "source": result.document_id
            })
            sources.append({
                "chunk_id": result.chunk_id,
                "document_id": result.document_id,
                "score": result.score,
                "reranked_score": result.reranked_score
            })

        # Yield sources first
        yield {"type": "sources", "data": sources}

        # 3. Stream response
        full_response = []
        async for token in self.llm_service.stream_response(
            query=query,
            context=context
        ):
            yield {"type": "token", "data": token}
            full_response.append(token)

        # Store in conversation (simplified)
        if conv_id not in self._conversations:
            self._conversations[conv_id] = []

        self._conversations[conv_id].append(ChatMessage(
            role="user",
            content=query,
            timestamp=datetime.now().isoformat()
        ))

        self._conversations[conv_id].append(ChatMessage(
            role="assistant",
            content="".join(full_response),
            timestamp=datetime.now().isoformat(),
            sources=[SourceCitation(**s) for s in sources]
        ))

        # Yield completion
        yield {"type": "done", "conversation_id": conv_id}

    async def get_history(self, conversation_id: str) -> List[ChatMessage]:
        """Get conversation history"""
        return self._conversations.get(conversation_id, [])

    async def clear_history(self, conversation_id: str):
        """Clear conversation history"""
        if conversation_id in self._conversations:
            del self._conversations[conversation_id]
