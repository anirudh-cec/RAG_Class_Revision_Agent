"""
Retrieval Service - Business logic for search operations
"""

from typing import List, Dict, Any, Optional
import time

from src.retrieval.core.hybrid_search import HybridSearch, HybridSearchConfig
from src.retrieval.core.simple_search import SimpleDenseSearch
from src.retrieval.search.dense_search import DenseSearch
from src.retrieval.models.responses import SearchResult, SearchResponse, SearchStatsResponse
from src.retrieval.config.settings import get_settings


class RetrievalService:
    """
    Service layer for retrieval operations

    Provides high-level API for hybrid search and related operations.
    Supports dynamic search mode based on user settings.
    """

    def __init__(
        self,
        hybrid_search: Optional[HybridSearch] = None,
        dense_search: Optional[DenseSearch] = None,
        simple_search: Optional[SimpleDenseSearch] = None
    ):
        self.settings = get_settings()
        self.hybrid_search = hybrid_search
        self.dense_search = dense_search
        self.simple_search = simple_search or SimpleDenseSearch()

    async def hybrid_search(
        self,
        query: str,
        top_k: int = 5,
        dense_k: int = 50,
        sparse_k: int = 50,
        rerank_k: int = 20,
        filters: Optional[Dict[str, Any]] = None,
        alpha: float = 0.5
    ) -> List[SearchResult]:
        """
        Execute hybrid search with all stages

        Args:
            query: Search query
            top_k: Final number of results
            dense_k: Candidates from dense search
            sparse_k: Candidates from sparse search
            rerank_k: Candidates for reranking
            filters: Metadata filters
            alpha: Dense vs sparse weight

        Returns:
            List of ranked SearchResult
        """
        if not self.hybrid_search:
            raise ValueError("HybridSearch not initialized")

        config = HybridSearchConfig(
            dense_k=dense_k,
            sparse_k=sparse_k,
            rerank_k=rerank_k,
            final_k=top_k,
            rrf_k=self.settings.RRF_K,
            alpha=alpha,
            use_reranking=True
        )

        results = await self.hybrid_search.search(
            query=query,
            filters=filters,
            config_override=config
        )

        return results

    async def dense_search(
        self,
        query: str,
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """
        Execute pure dense (semantic) search

        Args:
            query: Search query
            top_k: Number of results
            filters: Metadata filters

        Returns:
            List of SearchResult
        """
        if not self.dense_search:
            raise ValueError("DenseSearch not initialized")

        results = await self.dense_search.search(
            query=query,
            top_k=top_k,
            filters=filters
        )

        return results

    async def get_index_stats(self) -> SearchStatsResponse:
        """
        Get statistics about the search index

        Returns:
            SearchStatsResponse with index information
        """
        # This would query the vector store for stats
        # For now, return placeholder
        return SearchStatsResponse(
            collection_name=self.settings.ASTRA_DB_COLLECTION,
            document_count=0,  # Would be fetched from DB
            vector_dimension=self.settings.EMBEDDING_DIMENSION,
            index_size_bytes=None,
            last_updated=None
        )

    async def search_with_timing(
        self,
        query: str,
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> tuple[List[SearchResult], Dict[str, float]]:
        """
        Execute search with detailed timing

        Returns:
            Tuple of (results, timing_dict)
        """
        if not self.hybrid_search:
            raise ValueError("HybridSearch not initialized")

        start_total = time.time()

        # Use the timing method from HybridSearch
        results, timing = await self.hybrid_search.search_with_timing(
            query=query,
            filters=filters
        )

        timing['total_with_overhead_ms'] = (time.time() - start_total) * 1000

        return results, timing

    async def search_with_settings(
        self,
        query: str,
        settings: Dict[str, Any],
        filters: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """
        Execute search based on user settings

        Args:
            query: Search query
            settings: Dictionary with search settings:
                - hybrid_search: bool - Whether to use hybrid search
                - reranking: bool - Whether to use reranking
                - dense_k: int - Number of dense candidates
                - sparse_k: int - Number of sparse candidates
                - rerank_k: int - Number of candidates to rerank
                - final_k: int - Final number of results
            filters: Optional metadata filters

        Returns:
            List of ranked SearchResult
        """
        hybrid_search = settings.get("hybrid_search", True)
        reranking = settings.get("reranking", True)
        final_k = settings.get("final_k", 5)

        if hybrid_search and self.hybrid_search:
            # Use full hybrid search with all components
            from src.retrieval.core.hybrid_search import HybridSearchConfig

            config = HybridSearchConfig(
                dense_k=settings.get("dense_k", 50),
                sparse_k=settings.get("sparse_k", 50),
                rerank_k=settings.get("rerank_k", 20),
                final_k=final_k,
                rrf_k=self.settings.RRF_K,
                alpha=0.5,
                use_reranking=reranking
            )

            results = await self.hybrid_search.search(
                query=query,
                filters=filters,
                config_override=config
            )
            return results

        elif not hybrid_search and self.simple_search:
            # Use simple dense search only (no torch needed)
            results = await self.simple_search.search(
                query=query,
                top_k=final_k,
                filters=filters
            )
            return results

        else:
            # Fallback: use whatever is available
            if self.dense_search:
                results = await self.dense_search.search(
                    query=query,
                    top_k=final_k,
                    filters=filters
                )
                return results
            else:
                raise ValueError("No search method available")
