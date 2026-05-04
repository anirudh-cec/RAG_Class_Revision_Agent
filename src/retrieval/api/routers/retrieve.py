"""
Direct retrieval API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional

from src.retrieval.models.requests import SearchRequest, SimilarityRequest
from src.retrieval.models.responses import SearchResponse, SearchResult
from src.retrieval.services.retrieval_service import RetrievalService
from src.retrieval.api.dependencies import get_retrieval_service

import time

router = APIRouter()


@router.post("/search", response_model=SearchResponse)
async def hybrid_search(
    request: SearchRequest,
    retrieval_service: RetrievalService = Depends(get_retrieval_service)
) -> SearchResponse:
    """
    Perform hybrid search with dense + sparse + RRF + reranking.

    This is the main search endpoint that:
    1. Runs dense (semantic) search
    2. Runs sparse (SPLADE) search
    3. Fuses results with RRF
    4. Reranks with cross-encoder
    5. Returns top-N results
    """
    start_time = time.time()

    try:
        results = await retrieval_service.hybrid_search(
            query=request.query,
            top_k=request.top_k or 5,
            dense_k=request.dense_k or 50,
            sparse_k=request.sparse_k or 50,
            rerank_k=request.rerank_k or 20,
            filters=request.filters,
            alpha=request.alpha or 0.5
        )

        processing_time = (time.time() - start_time) * 1000

        return SearchResponse(
            query=request.query,
            results=results,
            total_results=len(results),
            search_metadata={
                "dense_k": request.dense_k or 50,
                "sparse_k": request.sparse_k or 50,
                "rerank_k": request.rerank_k or 20,
                "alpha": request.alpha or 0.5
            },
            processing_time_ms=processing_time
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Search failed: {str(e)}"
        )


@router.post("/similar", response_model=SearchResponse)
async def similarity_search(
    request: SimilarityRequest,
    retrieval_service: RetrievalService = Depends(get_retrieval_service)
) -> SearchResponse:
    """
    Pure semantic/dense similarity search without hybrid components.

    Useful for finding similar documents without reranking.
    """
    start_time = time.time()

    try:
        results = await retrieval_service.dense_search(
            query=request.query,
            top_k=request.top_k or 10,
            filters=request.filters
        )

        processing_time = (time.time() - start_time) * 1000

        return SearchResponse(
            query=request.query,
            results=results,
            total_results=len(results),
            search_metadata={"search_type": "dense_only"},
            processing_time_ms=processing_time
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Similarity search failed: {str(e)}"
        )


@router.get("/stats")
async def get_index_stats(
    retrieval_service: RetrievalService = Depends(get_retrieval_service)
):
    """Get vector store index statistics."""
    try:
        stats = await retrieval_service.get_index_stats()
        return {
            "status": "success",
            "stats": stats.dict()
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get stats: {str(e)}"
        )
