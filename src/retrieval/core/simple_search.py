"""
Simple Dense Search (No torch dependency)

When hybrid search is OFF, use this simplified version
that only does dense/semantic search without torch.
"""

import asyncio
from typing import List, Dict, Any, Optional

from astrapy import DataAPIClient

from src.retrieval.models.responses import SearchResult
from src.retrieval.config.settings import get_settings


class SimpleDenseSearch:
    """
    Simple dense semantic search using AstraDB only.

    This is used when:
    - Hybrid search is OFF
    - We want to avoid loading torch/transformers
    """

    def __init__(
        self,
        api_endpoint: Optional[str] = None,
        token: Optional[str] = None,
        collection_name: str = "document_chunks"
    ):
        self.settings = get_settings()
        self.api_endpoint = api_endpoint or self.settings.ASTRA_DB_API_ENDPOINT
        self.token = token or self.settings.ASTRA_DB_TOKEN
        self.collection_name = collection_name

        # Initialize client (lazy connection)
        self._client = None
        self._db = None
        self._collection = None

    def _init_connection(self):
        """Initialize database connection"""
        if self._client is None:
            self._client = DataAPIClient()
            self._db = self._client.get_database(
                api_endpoint=self.api_endpoint,
                token=self.token
            )
            self._collection = self._db.get_collection(self.collection_name)

    async def search(
        self,
        query: str,
        top_k: int = 10,
        filters: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> List[SearchResult]:
        """
        Perform simple dense semantic search
        """
        # Initialize connection in thread pool
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self._init_connection)

        # Generate embedding for query using OpenAI
        from openai import AsyncOpenAI
        import os

        client = AsyncOpenAI(
            api_key=os.environ.get("MESH_API_KEY"),
            base_url="https://api.meshapi.ai/v1"
        )

        response = await client.embeddings.create(
            model="text-embedding-3-small",
            input=query
        )
        query_embedding = response.data[0].embedding

        # Build filter clause
        filter_clause = self._build_filter(filters) if filters else None

        # Execute vector search
        results = await loop.run_in_executor(
            None,
            lambda: list(self._collection.find(
                filter=filter_clause,
                sort={"$vector": query_embedding},
                limit=top_k,
                projection={"$vector": 0}
            ))
        )

        # Convert to SearchResult objects
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

    def _build_filter(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Build AstraDB filter clause from filter dict"""
        if not filters:
            return {}

        filter_clause = {}
        for key, value in filters.items():
            if isinstance(value, dict):
                filter_clause[key] = value
            elif isinstance(value, list):
                filter_clause[key] = {"$in": value}
            else:
                filter_clause[key] = value

        return filter_clause
