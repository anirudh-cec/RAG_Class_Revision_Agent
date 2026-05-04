"""
Hybrid Search Orchestrator

Coordinates dense, sparse, and fusion components
for end-to-end hybrid retrieval.
"""

import asyncio
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import time

from src.retrieval.search.dense_search import DenseSearch
from src.retrieval.search.sparse_search import SparseSearch
from src.retrieval.core.rrf_fusion import RRFFusion
from src.retrieval.core.reranker import CrossEncoderReranker
from src.retrieval.models.responses import SearchResult


@dataclass
class HybridSearchConfig:
    """Configuration for hybrid search"""
    dense_k: int = 50
    sparse_k: int = 50
    rerank_k: int = 20
    final_k: int = 5
    rrf_k: int = 60
    alpha: float = 0.5
    use_reranking: bool = True


class HybridSearch:
    """
    Hybrid Search Orchestrator

    Pipeline:
    1. Run dense and sparse search in parallel
    2. Merge results with RRF
    3. Rerank top results with cross-encoder
    4. Return final top-K
    """

    def __init__(
        self,
        dense_search: DenseSearch,
        sparse_search: SparseSearch,
        rrf_fusion: RRFFusion,
        reranker: CrossEncoderReranker,
        config: Optional[HybridSearchConfig] = None
    ):
        self.dense_search = dense_search
        self.sparse_search = sparse_search
        self.rrf_fusion = rrf_fusion
        self.reranker = reranker
        self.config = config or HybridSearchConfig()

    async def search(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        config_override: Optional[HybridSearchConfig] = None
    ) -> List[SearchResult]:
        """
        Execute hybrid search pipeline

        Args:
            query: Search query string
            filters: Optional metadata filters
            config_override: Optional config overrides

        Returns:
            List of SearchResult objects (ranked)
        """
        config = config_override or self.config

        # Step 1: Run dense and sparse search in parallel
        dense_task = asyncio.create_task(
            self.dense_search.search(
                query=query,
                top_k=config.dense_k,
                filters=filters
            )
        )

        sparse_task = asyncio.create_task(
            self.sparse_search.search(
                query=query,
                top_k=config.sparse_k,
                filters=filters
            )
        )

        # Wait for both searches to complete
        dense_results, sparse_results = await asyncio.gather(
            dense_task, sparse_task
        )

        # Step 2: RRF Fusion
        fused_results = self.rrf_fusion.fuse(
            dense_results=dense_results,
            sparse_results=sparse_results,
            k=config.rrf_k,
            top_n=config.rerank_k
        )

        # Step 3: Cross-encoder reranking (if enabled)
        if config.use_reranking and fused_results:
            reranked_results = await self.reranker.rerank(
                query=query,
                results=fused_results,
                top_k=config.final_k
            )
            return reranked_results

        # Return top-K without reranking
        return fused_results[:config.final_k]

    async def batch_search(
        self,
        queries: List[str],
        filters: Optional[Dict[str, Any]] = None,
        config_override: Optional[HybridSearchConfig] = None
    ) -> List[List[SearchResult]]:
        """
        Execute hybrid search for multiple queries in parallel

        Args:
            queries: List of query strings
            filters: Optional metadata filters
            config_override: Optional config overrides

        Returns:
            List of SearchResult lists (one per query)
        """
        # Process all queries in parallel with semaphore for rate limiting
        semaphore = asyncio.Semaphore(10)

        async def search_with_limit(query: str) -> List[SearchResult]:
            async with semaphore:
                return await self.search(query, filters, config_override)

        tasks = [search_with_limit(q) for q in queries]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Handle any exceptions
        processed_results = []
        for result in results:
            if isinstance(result, Exception):
                processed_results.append([])
            else:
                processed_results.append(result)

        return processed_results

    async def search_with_timing(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        config_override: Optional[HybridSearchConfig] = None
    ) -> tuple[List[SearchResult], Dict[str, float]]:
        """
        Execute search with detailed timing information

        Returns:
            Tuple of (results, timing_dict)
        """
        config = config_override or self.config
        timing = {}

        start_total = time.time()

        # Dense search
        t0 = time.time()
        dense_task = asyncio.create_task(
            self.dense_search.search(
                query=query,
                top_k=config.dense_k,
                filters=filters
            )
        )

        # Sparse search
        t1 = time.time()
        sparse_task = asyncio.create_task(
            self.sparse_search.search(
                query=query,
                top_k=config.sparse_k,
                filters=filters
            )
        )

        # Wait for both
        dense_results, sparse_results = await asyncio.gather(
            dense_task, sparse_task
        )
        timing['dense_search_ms'] = (time.time() - t0) * 1000
        timing['sparse_search_ms'] = (time.time() - t1) * 1000

        # RRF Fusion
        t0 = time.time()
        fused_results = self.rrf_fusion.fuse(
            dense_results=dense_results,
            sparse_results=sparse_results,
            k=config.rrf_k,
            top_n=config.rerank_k
        )
        timing['rrf_fusion_ms'] = (time.time() - t0) * 1000

        # Reranking (if enabled)
        if config.use_reranking and fused_results:
            t0 = time.time()
            final_results = await self.reranker.rerank(
                query=query,
                results=fused_results,
                top_k=config.final_k
            )
            timing['reranking_ms'] = (time.time() - t0) * 1000
        else:
            final_results = fused_results[:config.final_k]
            timing['reranking_ms'] = 0

        timing['total_ms'] = (time.time() - start_total) * 1000

        return final_results, timing
