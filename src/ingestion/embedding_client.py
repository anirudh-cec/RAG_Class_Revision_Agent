"""Client for generating text embeddings via MeshAPI (OpenAI-compatible)."""

import os
import time
from typing import TypedDict

from openai import OpenAI
from openai.types.embedding import Embedding


class EmbeddingConfig(TypedDict):
    """Configuration for embedding client."""

    api_key: str
    base_url: str
    model: str
    dimensions: int


class EmbeddingClient:
    """Client for generating text embeddings via OpenAI."""

    DEFAULT_BASE_URL = "https://api.openai.com/v1"
    DEFAULT_MODEL = "text-embedding-3-small"
    DEFAULT_DIMENSIONS = 1536

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str = DEFAULT_BASE_URL,
        model: str = DEFAULT_MODEL,
        dimensions: int = DEFAULT_DIMENSIONS,
    ):
        """Initialize the embedding client.

        Args:
            api_key: OpenAI API key. Defaults to OPENAI_API_KEY env var.
            base_url: OpenAI base URL.
            model: Embedding model to use.
            dimensions: Expected embedding dimensions.

        Raises:
            ValueError: If no API key provided or found in environment.
        """
        if api_key is None:
            api_key = os.environ.get("OPENAI_API_KEY")

        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY not provided and not found in environment"
            )

        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.dimensions = dimensions

        self.client = OpenAI(api_key=api_key, base_url=base_url)

    def embed_text(
        self,
        text: str,
        max_retries: int = 3,
        base_delay: float = 2.0,
    ) -> list[float]:
        """Generate embedding for a single text.

        Args:
            text: Input text to embed.
            max_retries: Maximum retry attempts for transient failures.
            base_delay: Base delay for exponential backoff in seconds.

        Returns:
            1536-dimensional embedding vector.

        Raises:
            ValueError: If text is empty.
            RuntimeError: If API call fails after all retries.
        """
        if not text or not text.strip():
            raise ValueError("Cannot embed empty text")

        last_error: Exception | None = None

        for attempt in range(max_retries):
            try:
                response = self.client.embeddings.create(
                    model=self.model,
                    input=text,
                    dimensions=self.dimensions,
                )

                embedding: Embedding = response.data[0]
                return list(embedding.embedding)

            except Exception as e:
                last_error = e
                is_retryable = isinstance(
                    e, (TimeoutError, ConnectionError)
                ) or (
                    hasattr(e, "status_code")
                    and getattr(e, "status_code", 0) in (429, 502, 503, 504)
                )

                if not is_retryable or attempt == max_retries - 1:
                    break

                delay = base_delay * (2**attempt)
                time.sleep(delay)

        raise RuntimeError(
            f"Failed to generate embedding after {max_retries} attempts: {last_error}"
        ) from last_error

    def embed_batch(
        self,
        texts: list[str],
        batch_size: int = 100,
        max_retries: int = 3,
    ) -> list[list[float]]:
        """Generate embeddings for multiple texts in batches.

        Args:
            texts: List of input texts to embed.
            batch_size: Number of texts per API call.
            max_retries: Maximum retry attempts per batch.

        Returns:
            List of embedding vectors in same order as input.

        Raises:
            RuntimeError: If any batch fails after all retries.
        """
        if not texts:
            return []

        results: list[list[float]] = []

        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]

            for attempt in range(max_retries):
                try:
                    response = self.client.embeddings.create(
                        model=self.model,
                        input=batch,
                        dimensions=self.dimensions,
                    )

                    batch_embeddings: list[list[float]] = [
                        list(item.embedding) for item in response.data
                    ]
                    results.extend(batch_embeddings)
                    break

                except Exception as e:
                    if attempt == max_retries - 1:
                        raise RuntimeError(
                            f"Failed to embed batch {i // batch_size} after "
                            f"{max_retries} attempts: {e}"
                        ) from e
                    time.sleep(2**attempt)

        return results
