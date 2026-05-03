"""Client for AstraDB vector store operations."""

import os
from typing import Any

from astrapy import DataAPIClient
from astrapy.database import Database
from astrapy.collection import Collection
from astrapy.info import CollectionDefinition, CollectionVectorOptions


class VectorStoreClient:
    """Client for AstraDB vector store operations."""

    DEFAULT_COLLECTION_NAME = "class_chunks"
    DEFAULT_DIMENSION = 1536

    def __init__(
        self,
        api_endpoint: str | None = None,
        token: str | None = None,
        collection_name: str = DEFAULT_COLLECTION_NAME,
    ):
        """Initialize AstraDB vector store client.

        Args:
            api_endpoint: AstraDB API endpoint. Defaults to ASTRA_API_ENDPOINT env var.
            token: AstraDB token. Defaults to ASTRA_TOKEN env var.
            collection_name: Name of the collection to use/create.

        Raises:
            ValueError: If credentials not provided or found in environment.
        """
        if api_endpoint is None:
            api_endpoint = os.environ.get("ASTRA_API_ENDPOINT")

        if token is None:
            token = os.environ.get("ASTRA_TOKEN")

        if not api_endpoint:
            raise ValueError(
                "AstraDB API endpoint not provided and ASTRA_API_ENDPOINT "
                "not found in environment"
            )

        if not token:
            raise ValueError(
                "AstraDB token not provided and ASTRA_TOKEN not found in "
                "environment"
            )

        self.api_endpoint = api_endpoint
        self.token = token
        self.collection_name = collection_name
        self._db: Database | None = None
        self._collection: Collection | None = None

    def _get_db(self) -> Database:
        """Get or create database connection."""
        if self._db is None:
            client = DataAPIClient()
            self._db = client.get_database(
                api_endpoint=self.api_endpoint,
                token=self.token,
            )
        return self._db

    def ensure_collection(
        self,
        dimension: int = DEFAULT_DIMENSION,
    ) -> Collection:
        """Ensure the collection exists with correct vector dimensions.

        Args:
            dimension: Vector dimension (1536 for text-embedding-3-small).

        Returns:
            AstraDB Collection object.

        Raises:
            RuntimeError: If collection creation fails.
        """
        if self._collection is not None:
            return self._collection

        try:
            db = self._get_db()
            collection_names = db.list_collection_names()

            if self.collection_name in collection_names:
                self._collection = db.get_collection(self.collection_name)
            else:
                definition = CollectionDefinition(
                    vector=CollectionVectorOptions(
                        dimension=dimension,
                        metric="cosine",
                    )
                )
                self._collection = db.create_collection(
                    name=self.collection_name,
                    definition=definition,
                )

            return self._collection

        except Exception as e:
            raise RuntimeError(
                f"Failed to ensure collection {self.collection_name}: {e}"
            ) from e

    def insert_chunks(
        self,
        chunks: list[dict],
    ) -> list[str]:
        """Insert embedded chunks into the vector store.

        Args:
            chunks: List of chunks with embeddings. Each chunk must have:
                - chunk_id: int
                - text: str
                - embedding: list[float]
                - metadata: dict

        Returns:
            List of inserted document IDs in same order.

        Raises:
            RuntimeError: If insertion fails.
        """
        if not chunks:
            return []

        collection = self.ensure_collection()

        documents: list[dict[str, Any]] = []
        for chunk in chunks:
            doc = {
                "_id": f"chunk_{chunk['chunk_id']}",
                "text": chunk["text"],
                "$vector": chunk["embedding"],
                "metadata": chunk["metadata"],
            }
            documents.append(doc)

        try:
            result = collection.insert_many(documents)
            return list(result.inserted_ids)
        except Exception as e:
            raise RuntimeError(f"Failed to insert chunks: {e}") from e

    def search_similar(
        self,
        query_embedding: list[float],
        top_k: int = 5,
        filter_dict: dict | None = None,
    ) -> list[dict]:
        """Search for similar chunks using vector similarity.

        Args:
            query_embedding: Query vector to search for.
            top_k: Number of results to return.
            filter_dict: Optional metadata filter (e.g., {"chunk_type": "code_walkthrough"}).

        Returns:
            List of matching documents with similarity scores.
        """
        collection = self.ensure_collection()

        try:
            cursor = collection.find(
                filter=filter_dict or {},
                sort={"$vector": query_embedding},
                limit=top_k,
                include_similarity=True,
            )

            return list(cursor)
        except Exception as e:
            raise RuntimeError(f"Failed to search similar chunks: {e}") from e

    def delete_all_chunks(self) -> int:
        """Delete all chunks from the collection.

        Returns:
            Number of documents deleted.

        Raises:
            RuntimeError: If deletion fails.
        """
        collection = self.ensure_collection()

        try:
            result = collection.delete_many({})
            return result.deleted_count
        except Exception as e:
            raise RuntimeError(f"Failed to delete chunks: {e}") from e
