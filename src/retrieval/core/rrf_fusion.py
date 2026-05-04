"""
Reciprocal Rank Fusion (RRF) Implementation

RRF is a method for combining ranked lists from multiple sources.
It doesn't require score normalization and is robust to different score scales.

Formula: score = Σ 1/(k + rank)
Where k is a constant (typically 60) and rank is the position in the list.
"""

from typing import List, Dict, Set
from dataclasses import dataclass
from collections import defaultdict

from src.retrieval.models.responses import SearchResult


@dataclass
class RRFConfig:
    """Configuration for RRF"""
    k: int = 60


class RRFFusion:
    """
    Reciprocal Rank Fusion implementation

    Combines multiple ranked result lists into a single ranked list
    using the RRF formula.
    """

    def __init__(self, config: RRFConfig = None):
        self.config = config or RRFConfig()

    def fuse(
        self,
        dense_results: List[SearchResult],
        sparse_results: List[SearchResult],
        k: int = None,
        top_n: int = None
    ) -> List[SearchResult]:
        """
        Fuse dense and sparse search results using RRF

        Args:
            dense_results: Results from dense (semantic) search
            sparse_results: Results from sparse (SPLADE) search
            k: RRF constant (uses config default if not specified)
            top_n: Return top N results (None = return all)

        Returns:
            Fused and ranked list of SearchResult
        """
        k = k or self.config.k

        # Dictionary to accumulate RRF scores: {doc_id: rrf_score}
        rrf_scores: Dict[str, float] = defaultdict(float)

        # Dictionary to store the best SearchResult for each doc_id
        doc_results: Dict[str, SearchResult] = {}

        # Process dense results
        for rank, result in enumerate(dense_results, start=1):
            doc_id = result.chunk_id or result.document_id
            rrf_scores[doc_id] += 1.0 / (k + rank)

            # Store the result with highest individual score
            if doc_id not in doc_results or result.score > doc_results[doc_id].score:
                doc_results[doc_id] = result

        # Process sparse results
        for rank, result in enumerate(sparse_results, start=1):
            doc_id = result.chunk_id or result.document_id
            rrf_scores[doc_id] += 1.0 / (k + rank)

            # Store the result with highest individual score
            if doc_id not in doc_results or result.score > doc_results[doc_id].score:
                doc_results[doc_id] = result

        # Sort by RRF score (descending)
        sorted_doc_ids = sorted(
            rrf_scores.keys(),
            key=lambda doc_id: rrf_scores[doc_id],
            reverse=True
        )

        # Build final result list
        fused_results = []
        for rank, doc_id in enumerate(sorted_doc_ids, start=1):
            result = doc_results[doc_id]
            # Create new result with RRF score and rank
            fused_result = SearchResult(
                chunk_id=result.chunk_id,
                document_id=result.document_id,
                content=result.content,
                metadata=result.metadata,
                score=rrf_scores[doc_id],  # RRF score
                rank=rank,
                source=result.source,
                reranked_score=None,
                reranked_rank=None
            )
            fused_results.append(fused_result)

        # Return top N if specified
        if top_n:
            return fused_results[:top_n]

        return fused_results

    def fuse_multi(
        self,
        result_lists: List[List[SearchResult]],
        k: int = None,
        top_n: int = None
    ) -> List[SearchResult]:
        """
        Fuse multiple result lists (more than 2) using RRF

        Args:
            result_lists: List of result lists from different sources
            k: RRF constant
            top_n: Return top N results

        Returns:
            Fused and ranked list of SearchResult
        """
        k = k or self.config.k

        rrf_scores: Dict[str, float] = defaultdict(float)
        doc_results: Dict[str, SearchResult] = {}

        # Process each result list
        for results in result_lists:
            for rank, result in enumerate(results, start=1):
                doc_id = result.chunk_id or result.document_id
                rrf_scores[doc_id] += 1.0 / (k + rank)

                if doc_id not in doc_results or result.score > doc_results[doc_id].score:
                    doc_results[doc_id] = result

        # Sort and build results
        sorted_doc_ids = sorted(
            rrf_scores.keys(),
            key=lambda doc_id: rrf_scores[doc_id],
            reverse=True
        )

        fused_results = []
        for rank, doc_id in enumerate(sorted_doc_ids, start=1):
            result = doc_results[doc_id]
            fused_result = SearchResult(
                chunk_id=result.chunk_id,
                document_id=result.document_id,
                content=result.content,
                metadata=result.metadata,
                score=rrf_scores[doc_id],
                rank=rank,
                source=result.source
            )
            fused_results.append(fused_result)

        if top_n:
            return fused_results[:top_n]

        return fused_results
