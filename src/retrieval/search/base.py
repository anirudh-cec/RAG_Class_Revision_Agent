"""
Base Search Interface

Abstract base class for all search implementations.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

from src.retrieval.models.responses import SearchResult


class BaseSearch(ABC):
    """Abstract base class for search implementations"""

    @abstractmethod
    async def search(
        self,
        query: str,
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> List[SearchResult]:
        """
        Execute search

        Args:
            query: Search query string
            top_k: Number of results to return
            filters: Optional metadata filters
            **kwargs: Additional search parameters

        Returns:
            List of SearchResult objects
        """
        pass

    @abstractmethod
    async def batch_search(
        self,
        queries: List[str],
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[List[SearchResult]]:
        """
        Execute multiple searches in parallel

        Args:
            queries: List of query strings
            top_k: Results per query
            filters: Optional metadata filters

        Returns:
            List of result lists (one per query)
        """
        pass
