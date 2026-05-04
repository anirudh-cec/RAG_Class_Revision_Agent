"""
Request models for API endpoints
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


# ==================== Search Requests ====================

class SearchRequest(BaseModel):
    """Request for hybrid search"""
    query: str = Field(..., description="Search query", min_length=1)
    top_k: Optional[int] = Field(default=5, ge=1, le=50, description="Number of results")
    dense_k: Optional[int] = Field(default=50, ge=10, le=200, description="Dense search candidates")
    sparse_k: Optional[int] = Field(default=50, ge=10, le=200, description="Sparse search candidates")
    rerank_k: Optional[int] = Field(default=20, ge=5, le=100, description="Reranker candidates")
    alpha: Optional[float] = Field(default=0.5, ge=0.0, le=1.0, description="Dense vs sparse weight")
    filters: Optional[Dict[str, Any]] = Field(default=None, description="Metadata filters")


class SimilarityRequest(BaseModel):
    """Request for pure similarity search"""
    query: str = Field(..., description="Search query", min_length=1)
    top_k: Optional[int] = Field(default=10, ge=1, le=100)
    filters: Optional[Dict[str, Any]] = Field(default=None)


# ==================== Chat Requests ====================

class ChatRequest(BaseModel):
    """Request for chat query"""
    query: str = Field(..., description="User query", min_length=1)
    conversation_id: Optional[str] = Field(default=None, description="Conversation ID")
    top_k: Optional[int] = Field(default=5, ge=1, le=20)
    filters: Optional[Dict[str, Any]] = Field(default=None)
    stream: Optional[bool] = Field(default=False, description="Whether to stream response")
    # Search settings
    hybrid_search: Optional[bool] = Field(default=True, description="Use hybrid search (dense + sparse)")
    reranking: Optional[bool] = Field(default=True, description="Use cross-encoder reranking")
    dense_k: Optional[int] = Field(default=50, ge=10, le=200, description="Dense search candidates")
    sparse_k: Optional[int] = Field(default=50, ge=10, le=200, description="Sparse search candidates")
    rerank_k: Optional[int] = Field(default=20, ge=5, le=100, description="Rerank candidates")


class StreamChatRequest(BaseModel):
    """Request for streaming chat"""
    query: str = Field(..., description="User query", min_length=1)
    conversation_id: Optional[str] = Field(default=None)
    top_k: Optional[int] = Field(default=5)
    filters: Optional[Dict[str, Any]] = Field(default=None)


class ChatMessageRequest(BaseModel):
    """Single message in a conversation"""
    role: str = Field(..., pattern="^(user|assistant|system)$")
    content: str = Field(..., min_length=1)
    timestamp: Optional[str] = Field(default=None)
    sources: Optional[List[Dict[str, Any]]] = Field(default=None)


# ==================== Filter Requests ====================

class FilterRequest(BaseModel):
    """Request for filtered search"""
    source_types: Optional[List[str]] = Field(default=None)
    document_names: Optional[List[str]] = Field(default=None)
    date_from: Optional[str] = Field(default=None)
    date_to: Optional[str] = Field(default=None)
    language: Optional[str] = Field(default=None)
    custom: Optional[Dict[str, Any]] = Field(default=None)
