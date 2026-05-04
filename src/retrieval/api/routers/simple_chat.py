"""
Simplified Chat API - No torch/dependencies

Uses only dense search with OpenAI embeddings and AstraDB.
"""

from fastapi import APIRouter, HTTPException
from typing import Optional
import uuid
from datetime import datetime

from src.retrieval.models.requests import ChatRequest
from src.retrieval.models.responses import ChatResponse, SourceCitation
from src.retrieval.services.simple_retrieval_service import SimpleRetrievalService
from src.retrieval.services.llm_service import LLMService


router = APIRouter()

# Singleton service
_retrieval_service: Optional[SimpleRetrievalService] = None
_llm_service: Optional[LLMService] = None


def get_retrieval_service() -> SimpleRetrievalService:
    global _retrieval_service
    if _retrieval_service is None:
        _retrieval_service = SimpleRetrievalService()
    return _retrieval_service


def get_llm_service() -> LLMService:
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service


@router.post("/simple-chat", response_model=ChatResponse)
async def simple_chat_query(request: ChatRequest) -> ChatResponse:
    """
    Simplified chat query using only dense search.

    No torch/dependencies required.
    """
    try:
        retrieval_service = get_retrieval_service()
        llm_service = get_llm_service()

        # Generate conversation ID
        conversation_id = request.conversation_id or str(uuid.uuid4())

        # Search
        search_results = await retrieval_service.search(
            query=request.query,
            top_k=request.top_k or 5,
            filters=request.filters
        )

        # Format context
        context = []
        sources = []
        for result in search_results:
            context.append({
                "content": result.content,
                "source": result.document_id
            })
            sources.append(SourceCitation(
                chunk_id=result.chunk_id,
                document_id=result.document_id,
                content=result.content[:200] + "..." if len(result.content) > 200 else result.content,
                score=result.score,
                metadata=result.metadata
            ))

        # Generate response
        answer = await llm_service.generate_response(
            query=request.query,
            context=context,
            system_prompt="You are a helpful assistant. Answer the user's question based on the provided context."
        )

        return ChatResponse(
            conversation_id=conversation_id,
            answer=answer,
            sources=sources
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Chat query failed: {str(e)}"
        )
