"""Simple API - Just dense search + LLM"""

from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
import os
from openai import AsyncOpenAI
from astrapy import DataAPIClient
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Clients
openai = AsyncOpenAI(
    api_key=os.getenv("MESH_API_KEY"),
    base_url="https://api.meshapi.ai/v1"
)

astra = DataAPIClient()
db = astra.get_database(
    api_endpoint=os.getenv("ASTRA_DB_API_ENDPOINT"),
    token=os.getenv("ASTRA_DB_TOKEN")
)
collection = db.get_collection(os.getenv("ASTRA_DB_COLLECTION", "document_chunks"))


class ChatRequest(BaseModel):
    query: str
    top_k: int = 5


class Source(BaseModel):
    chunk_id: str
    document_id: str
    content: str
    score: float


class ChatResponse(BaseModel):
    answer: str
    sources: List[Source]


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    # 1. Get embedding
    emb = await openai.embeddings.create(
        model="text-embedding-3-small",
        input=req.query
    )
    vec = emb.data[0].embedding

    # 2. Search
    docs = list(collection.find(
        sort={"$vector": vec},
        limit=req.top_k,
        projection={"$vector": 0}
    ))

    # 3. Format
    context = []
    sources = []
    for d in docs:
        content = d.get("content", "")
        doc_id = d.get("document_id", "")
        score = d.get("$similarity", 0)

        context.append(f"Source: {doc_id}\n{content}")
        sources.append(Source(
            chunk_id=str(d.get("_id", "")),
            document_id=doc_id,
            content=content[:200] + "..." if len(content) > 200 else content,
            score=score
        ))

    # 4. Generate
    ctx = "\n\n---\n\n".join(context)
    chat = await openai.chat.completions.create(
        model="openai/gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Answer based on context. If not in context, say so."},
            {"role": "user", "content": f"Context:\n{ctx}\n\nQuestion: {req.query}"}
        ]
    )
    answer = chat.choices[0].message.content

    return ChatResponse(answer=answer, sources=sources)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
