"""Read and validate chunks.json output from chunking pipeline."""

import json
from typing import TypedDict


class ChunkRecord(TypedDict):
    """Input record from chunks.json."""

    chunk_id: int
    text: str
    start_time: str
    end_time: str
    start_seconds: float
    end_seconds: float
    duration_seconds: float
    cue_count: int
    topic_hint: str
    chunk_type: str
    source_file: str
    cues: list[dict]


def read_chunks(chunks_json_path: str) -> list[ChunkRecord]:
    """Read and validate chunks.json output from chunking pipeline.

    Args:
        chunks_json_path: Path to chunks.json file.

    Returns:
        List of ChunkRecord dicts, sorted by chunk_id.

    Raises:
        FileNotFoundError: If chunks_json_path does not exist.
        ValueError: If JSON is malformed or missing required fields.
    """
    import os

    if not os.path.exists(chunks_json_path):
        raise FileNotFoundError(f"Chunks file not found: {chunks_json_path}")

    with open(chunks_json_path, encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in chunks file: {e}") from e

    if not isinstance(data, list):
        raise ValueError(f"Expected JSON array, got {type(data).__name__}")

    required_fields = {"chunk_id", "text", "chunk_type", "source_file"}
    validated_chunks: list[ChunkRecord] = []

    for i, chunk in enumerate(data):
        if not isinstance(chunk, dict):
            raise ValueError(f"Chunk at index {i} is not a dict")

        missing = required_fields - set(chunk.keys())
        if missing:
            raise ValueError(
                f"Chunk at index {i} missing required fields: {missing}"
            )

        validated_chunks.append(chunk)  # type: ignore

    validated_chunks.sort(key=lambda c: c["chunk_id"])

    return validated_chunks
