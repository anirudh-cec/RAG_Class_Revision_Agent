"""
FastAPI entry point for Retrieval Pipeline
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from src.retrieval.api.routers import chat, retrieve, health, simple_chat
from src.retrieval.api.middleware import logging, error_handling
from src.retrieval.config.settings import get_settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    settings = get_settings()
    print(f"Starting RAG Retrieval API on {settings.API_HOST}:{settings.API_PORT}")

    # Initialize services (lazy loading will handle models)

    yield

    # Shutdown
    print("Shutting down RAG Retrieval API")


app = FastAPI(
    title="RAG Retrieval API",
    description="Hybrid search with RRF and Cross-Encoder reranking",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom middleware
app.add_middleware(logging.LoggingMiddleware)
app.add_exception_handler(Exception, error_handling.global_exception_handler)

# Routers
app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(chat.router, prefix="/api/v1/chat", tags=["chat"])
app.include_router(simple_chat.router, prefix="/api/v1/simple", tags=["simple"])
app.include_router(retrieve.router, prefix="/api/v1/retrieve", tags=["retrieve"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "RAG Retrieval API",
        "version": "1.0.0",
        "docs": "/docs"
    }
