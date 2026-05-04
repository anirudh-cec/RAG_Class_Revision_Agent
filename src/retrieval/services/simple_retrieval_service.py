"""
Simplified Retrieval Service - No torch dependency

Uses only dense search with AstraDB and OpenAI embeddings.
"""

from typing import List, Dict, Any, Optional
import asyncio
from datetime import datetime

from openai import AsyncOpenAI

from src.retrieval.models.responses import SearchResult
from src.retrieval.config.settings import get_settings


class SimpleRetrievalService:
    """
    Simplified retrieval service that only uses dense search.
    No torch, no transformers, no hybrid search.
    """

    def __init__(self):
        self.settings = get_settings()
        self.openai_client = AsyncOpenAI(
            api_key=self.settings.MESH_API_KEY,
            base_url=self.settings.MESH_BASE_URL
        )
        # Lazy init for AstraDB
        self._astra_client = None
        self._collection = None

    def _init_astra(self):
        """Initialize AstraDB connection"""
        if self._astra_client is None:
            from astrapy import DataAPIClient
            self._astra_client = DataAPIClient()
            db = self._astra_client.get_database(
                api_endpoint=self.settings.ASTRA_DB_API_ENDPOINT,
                token=self.settings.ASTRA_DB_TOKEN
            )
            self._collection = db.get_collection(self.settings.ASTRA_DB_COLLECTION)

    async def search(
        self,
        query: str,
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """
        Perform simple dense search.

        Args:
            query: Search query
            top_k: Number of results
            filters: Optional metadata filters

        Returns:
            List of SearchResult
        """
        # 1. Get embedding from OpenAI
        response = await self.openai_client.embeddings.create(
            model="text-embedding-3-small",
            input=query
        )
        query_embedding = response.data[0].embedding

        # 2. Search AstraDB
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._init_astra)

        # Build filter
        filter_clause = {}
        if filters:
            for key, value in filters.items():
                if isinstance(value, list):
                    filter_clause[key] = {"$in": value}
                else:
                    filter_clause[key] = value

        # Execute search
        results = await loop.run_in_executor(
            None,
            lambda: list(self._collection.find(
                filter=filter_clause if filter_clause else None,
                sort={"$vector": query_embedding},
                limit=top_k,
                projection={"$vector": 0}
            ))
        )

        # 3. Convert to SearchResult
        search_results = []
        for rank, doc in enumerate(results, start=1):
            score = doc.get("$similarity", 0.0)
            metadata = {k: v for k, v in doc.items()
                       if not k.startswith("$") and k != "content"}

            result = SearchResult(
                chunk_id=str(doc.get("_id", "")),
                document_id=doc.get("document_id", ""),
                content=doc.get("content", ""),
                metadata=metadata,
                score=score,
                rank=rank,
                source="dense"
            )
            search_results.append(result)

        return search_results
