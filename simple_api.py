"""
Simple FastAPI Backend - No torch dependencies

Uses only:
- AstraDB for vector search
- OpenAI/MeshAPI for embeddings and LLM
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import uuid
from datetime import datetime
import os

from openai import AsyncOpenAI
from astrapy import DataAPIClient


# Pydantic models
class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1)
    conversation_id: Optional[str] = None
    top_k: int = Field(default=5, ge=1, le=20)


class Source(BaseModel):
    chunk_id: str
    document_id: str
    content: str
    score: float


class ChatResponse(BaseModel):
    conversation_id: str
    answer: str
    sources: List[Source]


# Initialize FastAPI
app = FastAPI(
    title="Simple RAG API",
    description="Simple retrieval and generation - no torch required",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Initialize clients
settings = {
    "ASTRA_DB_API_ENDPOINT": os.environ.get("ASTRA_DB_API_ENDPOINT"),
    "ASTRA_DB_TOKEN": os.environ.get("ASTRA_DB_TOKEN"),
    "ASTRA_DB_COLLECTION": os.environ.get("ASTRA_DB_COLLECTION", "document_chunks"),
    "MESH_API_KEY": os.environ.get("MESH_API_KEY"),
    "MESH_BASE_URL": "https://api.meshapi.ai/v1",
    "LLM_MODEL": "openai/gpt-4o-mini",
}

openai_client = AsyncOpenAI(
    api_key=settings["MESH_API_KEY"],
    base_url=settings["MESH_BASE_URL"]
)

astra_client = None
collection = None


def init_astra():
    """Initialize AstraDB connection"""
    global astra_client, collection
    if astra_client is None:
        astra_client = DataAPIClient()
        db = astra_client.get_database(
            api_endpoint=settings["ASTRA_DB_API_ENDPOINT"],
            token=settings["ASTRA_DB_TOKEN"]
        )
        collection = db.get_collection(settings["ASTRA_DB_COLLECTION"])


@app.get("/")
async def root():
    return {"service": "Simple RAG API", "version": "1.0.0", "docs": "/docs"}


@app.get("/health")
async def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Simple chat with retrieval and generation.

    Uses only dense search (OpenAI embeddings + AstraDB).
    """
    try:
        # Generate conversation ID
        conversation_id = request.conversation_id or str(uuid.uuid4())

        # 1. Get embedding for query
        embed_response = await openai_client.embeddings.create(
            model="text-embedding-3-small",
            input=request.query
        )
        query_embedding = embed_response.data[0].embedding

        # 2. Search AstraDB
        import asyncio
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, init_astra)

        results = await loop.run_in_executor(
            None,
            lambda: list(collection.find(
                sort={"$vector": query_embedding},
                limit=request.top_k,
                projection={"$vector": 0}
            ))
        )

        # 3. Format context and sources
        context = []
        sources = []
        for doc in results:
            content = doc.get("content", "")
            doc_id = doc.get("document_id", "")
            score = doc.get("$similarity", 0.0)

            context.append(f"Source: {doc_id}\n{content}")
            sources.append(Source(
                chunk_id=str(doc.get("_id", "")),
                document_id=doc_id,
                content=content[:200] + "..." if len(content) > 200 else content,
                score=score
            ))

        # 4. Generate response with LLM
        context_str = "\n\n---\n\n".join(context)
        system_prompt = """You are a helpful assistant. Answer the user's question based ONLY on the provided context. If the context doesn't contain the answer, say "I don't have enough information to answer that question."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Context:\n{context_str}\n\nQuestion: {request.query}"}
        ]

        chat_response = await openai_client.chat.completions.create(
            model=settings["LLM_MODEL"],
            messages=messages
        )

        answer = chat_response.choices[0].message.content

        return ChatResponse(
            conversation_id=conversation_id,
            answer=answer,
            sources=sources
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Chat failed: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
