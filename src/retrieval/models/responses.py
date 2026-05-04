"""
Response models for API endpoints
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from datetime import datetime


# ==================== Search Results ====================

class SearchResult(BaseModel):
    """Single search result"""
    chunk_id: str = Field(..., description="Unique chunk identifier")
    document_id: str = Field(..., description="Parent document identifier")
    content: str = Field(..., description="Chunk content/text")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Chunk metadata")

    # Original scores from search
    score: float = Field(..., description="Original similarity/score")
    rank: int = Field(..., description="Original rank")
    source: str = Field(..., description="Source search type (dense/sparse)")

    # Reranking results (optional)
    reranked_score: Optional[float] = Field(default=None, description="Score after reranking")
    reranked_rank: Optional[int] = Field(default=None, description="Rank after reranking")

    class Config:
        json_schema_extra = {
            "example": {
                "chunk_id": "chunk_001",
                "document_id": "doc_001",
                "content": "This is the content of the chunk...",
                "metadata": {"source": "vtt", "timestamp": "00:05:30"},
                "score": 0.89,
                "rank": 1,
                "source": "dense",
                "reranked_score": 0.92,
                "reranked_rank": 1
            }
        }


class SearchResponse(BaseModel):
    """Response from search endpoints"""
    query: str = Field(..., description="Original query")
    results: List[SearchResult] = Field(default=[], description="Search results")
    total_results: int = Field(..., description="Total number of results")
    search_metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Metadata about the search"
    )
    processing_time_ms: Optional[float] = Field(
        default=None,
        description="Total processing time in milliseconds"
    )


class SearchStatsResponse(BaseModel):
    """Index statistics response"""
    collection_name: str
    document_count: int
    vector_dimension: int
    index_size_bytes: Optional[int] = None
    last_updated: Optional[str] = None


# ==================== Chat Responses ====================

class SourceCitation(BaseModel):
    """Source citation for chat response"""
    chunk_id: str
    document_id: str
    content: str
    score: float
    reranked_score: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None


class ChatMessage(BaseModel):
    """Single message in conversation"""
    role: str = Field(..., pattern="^(user|assistant|system)$")
    content: str
    timestamp: Optional[str] = None
    sources: Optional[List[SourceCitation]] = None


class ChatResponse(BaseModel):
    """Response from chat query"""
    conversation_id: str
    answer: str
    sources: List[SourceCitation] = []
    processing_time_ms: Optional[float] = None
    search_metadata: Optional[Dict[str, Any]] = None


class ChatStreamChunk(BaseModel):
    """Single chunk from streaming response"""
    type: str = Field(..., pattern="^(token|sources|done|error)$")
    data: Any


class ChatHistoryResponse(BaseModel):
    """Chat history response"""
    conversation_id: str
    messages: List[ChatMessage]


# ==================== Error Responses ====================

class ErrorDetail(BaseModel):
    """Error detail"""
    field: Optional[str] = None
    message: str
    code: Optional[str] = None


class ErrorResponse(BaseModel):
    """Standard error response"""
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None
    request_id: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
