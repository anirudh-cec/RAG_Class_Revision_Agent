"""
Dependency injection for FastAPI
"""

from functools import lru_cache
from typing import Optional

from src.retrieval.core.hybrid_search import HybridSearch
from src.retrieval.core.rrf_fusion import RRFFusion
from src.retrieval.core.reranker import CrossEncoderReranker
from src.retrieval.search.dense_search import DenseSearch
from src.retrieval.search.sparse_search import SparseSearch
from src.retrieval.services.retrieval_service import RetrievalService
from src.retrieval.services.llm_service import LLMService
from src.retrieval.config.settings import Settings, get_settings


# Singleton instances
_hybrid_search: Optional[HybridSearch] = None
_dense_search: Optional[DenseSearch] = None
_sparse_search: Optional[SparseSearch] = None
_retrieval_service: Optional[RetrievalService] = None
_llm_service: Optional[LLMService] = None


def get_hybrid_search() -> HybridSearch:
    """Get or create HybridSearch singleton"""
    global _hybrid_search
    if _hybrid_search is None:
        settings = get_settings()

        # Initialize components
        dense_search = DenseSearch()
        sparse_search = SparseSearch()
        rrf_fusion = RRFFusion()
        reranker = CrossEncoderReranker()

        _hybrid_search = HybridSearch(
            dense_search=dense_search,
            sparse_search=sparse_search,
            rrf_fusion=rrf_fusion,
            reranker=reranker
        )

    return _hybrid_search


def get_dense_search() -> DenseSearch:
    """Get or create DenseSearch singleton"""
    global _dense_search
    if _dense_search is None:
        _dense_search = DenseSearch()
    return _dense_search


def get_sparse_search() -> SparseSearch:
    """Get or create SparseSearch singleton"""
    global _sparse_search
    if _sparse_search is None:
        _sparse_search = SparseSearch()
    return _sparse_search


def get_retrieval_service() -> RetrievalService:
    """Get or create RetrievalService singleton"""
    global _retrieval_service
    if _retrieval_service is None:
        _retrieval_service = RetrievalService(
            hybrid_search=get_hybrid_search(),
            dense_search=get_dense_search()
        )
    return _retrieval_service


def get_llm_service() -> LLMService:
    """Get or create LLMService singleton"""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service
