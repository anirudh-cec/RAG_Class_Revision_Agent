"""Main orchestration module for embedding and vector store pipeline."""

import json
import os
from datetime import datetime, timezone
from typing import TypedDict

from src.ingestion.chunk_reader import read_chunks, ChunkRecord
from src.ingestion.embedding_client import EmbeddingClient
from src.ingestion.vector_store_client import VectorStoreClient
from src.logger.custom_logger import get_logger

logger = get_logger("embedding_pipeline")


class EmbeddingStatus(TypedDict):
    """Status tracking for each chunk."""

    chunk_id: int
    embedded: bool
    stored: bool
    error: str | None
    timestamp: str


class PipelineResult(TypedDict):
    """Result from running the embedding pipeline."""

    total_chunks: int
    embedded: int
    stored: int
    failed: int
    errors: list[str]
    status_path: str


def _validate_env() -> dict:
    """Validate required environment variables are set.

    Returns:
        Dict with keys: openai_api_key, astra_endpoint, astra_token

    Raises:
        ValueError: If any required env var is missing.
    """
    openai_api_key = os.environ.get("OPENAI_API_KEY")
    astra_endpoint = os.environ.get("ASTRA_API_ENDPOINT")
    astra_token = os.environ.get("ASTRA_TOKEN")

    missing = []
    if not openai_api_key:
        missing.append("OPENAI_API_KEY")
    if not astra_endpoint:
        missing.append("ASTRA_API_ENDPOINT")
    if not astra_token:
        missing.append("ASTRA_TOKEN")

    if missing:
        raise ValueError(
            f"Missing required environment variables: {', '.join(missing)}"
        )

    return {
        "openai_api_key": openai_api_key,
        "astra_endpoint": astra_endpoint,
        "astra_token": astra_token,
    }


def _build_metadata(chunk: ChunkRecord) -> dict:
    """Build metadata dict from chunk record."""
    return {
        "chunk_id": chunk["chunk_id"],
        "start_time": chunk["start_time"],
        "end_time": chunk["end_time"],
        "start_seconds": chunk["start_seconds"],
        "end_seconds": chunk["end_seconds"],
        "duration_seconds": chunk["duration_seconds"],
        "topic_hint": chunk["topic_hint"],
        "chunk_type": chunk["chunk_type"],
        "source_file": chunk["source_file"],
        "cue_count": chunk["cue_count"],
    }


def run_embedding_pipeline(
    chunks_json_path: str,
    embedding_status_path: str = "data/embeddings/embedding_status.json",
    batch_size: int = 50,
) -> PipelineResult:
    """Run the full embedding and vector store pipeline.

    Reads chunks from chunking pipeline output, generates embeddings using
    MeshAPI, and inserts into AstraDB vector store.

    Args:
        chunks_json_path: Path to chunks.json from chunking pipeline.
        embedding_status_path: Path to write status tracking file.
        batch_size: Number of chunks to embed per batch.

    Returns:
        dict with keys:
            "total_chunks": int — total chunks processed
            "embedded": int — chunks successfully embedded
            "stored": int — chunks stored in vector DB
            "failed": int — chunks that failed
            "errors": list[str] — error messages
            "status_path": str — path to status file

    Raises:
        FileNotFoundError: If chunks_json_path does not exist.
        ValueError: If required environment variables are missing.
    """
    logger.info("Starting embedding pipeline", path=chunks_json_path)

    # 1. Validate environment
    env = _validate_env()
    logger.info("Environment validated")

    # 2. Read chunks
    chunks = read_chunks(chunks_json_path)
    total = len(chunks)
    logger.info("Chunks loaded", total=total)

    # 3. Initialize clients
    embedding_client = EmbeddingClient(api_key=env["openai_api_key"])
    vector_store = VectorStoreClient(
        api_endpoint=env["astra_endpoint"],
        token=env["astra_token"],
    )
    logger.info("Clients initialized")

    # 4. Process in batches
    status_list: list[EmbeddingStatus] = []
    errors: list[str] = []
    embedded_count = 0
    stored_count = 0
    failed_count = 0

    for i in range(0, total, batch_size):
        batch = chunks[i : i + batch_size]
        batch_end = min(i + batch_size, total)
        logger.info("Processing batch", start=i + 1, end=batch_end, total=total)

        # Extract texts
        texts = [c["text"] for c in batch]

        # Generate embeddings
        try:
            embeddings = embedding_client.embed_batch(texts)
            embedded_count += len(batch)
        except Exception as e:
            error_msg = f"Batch {i // batch_size} embedding failed: {e}"
            logger.error(error_msg)
            errors.append(error_msg)

            # Mark all in batch as failed
            now = datetime.now(timezone.utc).isoformat()
            for chunk in batch:
                failed_count += 1
                status_list.append(
                    {
                        "chunk_id": chunk["chunk_id"],
                        "embedded": False,
                        "stored": False,
                        "error": str(e),
                        "timestamp": now,
                    }
                )
            continue

        # Prepare embedded chunks
        embedded_chunks = []
        for j, chunk in enumerate(batch):
            embedded_chunks.append(
                {
                    "chunk_id": chunk["chunk_id"],
                    "text": chunk["text"],
                    "embedding": embeddings[j],
                    "metadata": _build_metadata(chunk),
                }
            )

        # Insert into vector store
        try:
            vector_store.insert_chunks(embedded_chunks)
            stored_count += len(batch)
            logger.info("Batch stored", count=len(batch))
        except Exception as e:
            error_msg = f"Batch {i // batch_size} storage failed: {e}"
            logger.error(error_msg)
            errors.append(error_msg)

            # Mark as embedded but not stored
            now = datetime.now(timezone.utc).isoformat()
            for chunk in batch:
                failed_count += 1
                status_list.append(
                    {
                        "chunk_id": chunk["chunk_id"],
                        "embedded": True,
                        "stored": False,
                        "error": str(e),
                        "timestamp": now,
                    }
                )
            continue

        # Mark all in batch as success
        now = datetime.now(timezone.utc).isoformat()
        for chunk in batch:
            status_list.append(
                {
                    "chunk_id": chunk["chunk_id"],
                    "embedded": True,
                    "stored": True,
                    "error": None,
                    "timestamp": now,
                }
            )

    # 5. Write status file
    os.makedirs(os.path.dirname(embedding_status_path) or ".", exist_ok=True)
    status_data = {
        "pipeline_run_id": datetime.now(timezone.utc).isoformat(),
        "total_chunks": total,
        "successful": stored_count,
        "embedded": embedded_count,
        "stored": stored_count,
        "failed": failed_count,
        "chunks": sorted(status_list, key=lambda x: x["chunk_id"]),
    }

    with open(embedding_status_path, "w", encoding="utf-8") as f:
        json.dump(status_data, f, indent=2)

    logger.info(
        "Pipeline complete",
        total=total,
        embedded=embedded_count,
        stored=stored_count,
        failed=failed_count,
    )

    return {
        "total_chunks": total,
        "embedded": embedded_count,
        "stored": stored_count,
        "failed": failed_count,
        "errors": errors,
        "status_path": embedding_status_path,
    }
