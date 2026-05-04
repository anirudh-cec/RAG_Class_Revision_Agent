"""
Simple API - No torch dependencies

Basic dense search + LLM generation only.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import uuid
from datetime import datetime
import asyncio

from openai import AsyncOpenAI
from astrapy import DataAPIClient

from src.retrieval.config.settings import get_settings


router = APIRouter()

# Pydantic models
class SimpleChatRequest(BaseModel):
    query: str = Field(..., min_length=1)
    conversation_id: Optional[str] = None
    top_k: int = Field(default=5, ge=1, le=20)


class Source(BaseModel):
    chunk_id: str
    document_id: str
    content: str
    score: float


class SimpleChatResponse(BaseModel):
    conversation_id: str
    answer: str
    sources: List[Source]


# Simple retrieval service (no torch)
class SimpleRetrievalService:
    def __init__(self):
        self.settings = get_settings()
        self.openai_client = AsyncOpenAI(
            api_key=self.settings.MESH_API_KEY,
            base_url=self.settings.MESH_BASE_URL
        )
        self._astra_client = None
        self._collection = None

    async def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """Simple dense search with AstraDB."""
        # Get embedding
        response = await self.openai_client.embeddings.create(
            model="text-embedding-3-small",
            input=query
        )
        query_embedding = response.data[0].embedding

        # Init AstraDB if needed
        if self._astra_client is None:
            self._astra_client = DataAPIClient()
            db = self._astra_client.get_database(
                api_endpoint=self.settings.ASTRA_DB_API_ENDPOINT,
                token=self.settings.ASTRA_DB_TOKEN
            )
            self._collection = db.get_collection(self.settings.ASTRA_DB_COLLECTION)

        # Search
        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(
            None,
            lambda: list(self._collection.find(
                sort={"$vector": query_embedding},
                limit=top_k,
                projection={"$vector": 0}
            ))
        )

        # Format results
        formatted = []
        for doc in results:
            formatted.append({
                "chunk_id": str(doc.get("_id", "")),
                "document_id": doc.get("document_id", ""),
                "content": doc.get("content", ""),
                "score": doc.get("$similarity", 0.0)
            })

        return formatted


# Global service instance
_simple_service: Optional[SimpleRetrievalService] = None


def get_simple_service() -> SimpleRetrievalService:
    global _simple_service
    if _simple_service is None:
        _simple_service = SimpleRetrievalService()
    return _simple_service


@router.post("/chat", response_model=SimpleChatResponse)
async def simple_chat(request: SimpleChatRequest) -> SimpleChatResponse:
    """
    Simple chat endpoint - uses only dense search + LLM.
    No torch/dependencies required.
    """
    try:
        service = get_simple_service()
        settings = get_settings()

        # Generate conversation ID
        conversation_id = request.conversation_id or str(uuid.uuid4())

        # Search
        results = await service.search(
            query=request.query,
            top_k=request.top_k
        )

        # Format context for LLM
        context = []
        sources = []
        for r in results:
            context.append({
                "content": r["content"],
                "source": r["document_id"]
            })
            sources.append(Source(
                chunk_id=r["chunk_id"],
                document_id=r["document_id"],
                content=r["content"][:200] + "..." if len(r["content"]) > 200 else r["content"],
                score=r["score"]
            ))

        # Generate response with LLM
        openai_client = AsyncOpenAI(
            api_key=settings.MESH_API_KEY,
            base_url=settings.MESH_BASE_URL
        )

        system_prompt = "You are a helpful assistant. Answer based on the provided context. If context doesn't contain the answer, say so."

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Context:\n{context}\n\nQuestion: {request.query}"}
        ]

        response = await openai_client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=messages
        )

        answer = response.choices[0].message.content

        return SimpleChatResponse(
            conversation_id=conversation_id,
            answer=answer,
            sources=sources
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Chat failed: {str(e)}"
        )
