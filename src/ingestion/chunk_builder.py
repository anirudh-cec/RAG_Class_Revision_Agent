"""Phase 4: Build chunks with topic-boundary splitting and overlap."""

from src.ingestion.config import CHUNK_HARD_CAP_CUES, OVERLAP_CUES, TOPIC_SIGNAL_MIN_CUES


def build_chunks(merged_cues: list[dict]) -> list[list[dict]]:
    """Build chunks from merged cues with topic-boundary splitting and overlap.

    Args:
        merged_cues: List of MergedCue objects with potential_boundary set.

    Returns:
        List of chunks, where each chunk is a list of ChunkCue dicts.
    """
    if not merged_cues:
        return []

    # Step 4.1: Create chunks based on boundaries and hard cap
    chunks = []
    buffer = []

    for cue in merged_cues:
        chunk_cue = _to_chunk_cue(cue)
        buffer.append(chunk_cue)

        # Flush at topic boundary if buffer is large enough
        if cue["potential_boundary"] and len(buffer) >= TOPIC_SIGNAL_MIN_CUES:
            chunks.append(buffer)
            buffer = []
        # Flush at hard cap regardless
        elif len(buffer) >= CHUNK_HARD_CAP_CUES:
            chunks.append(buffer)
            buffer = []

    # Flush remaining buffer
    if buffer:
        chunks.append(buffer)

    # Step 4.2: Add overlap between adjacent chunks
    chunks = _add_overlap(chunks)

    return chunks


def _to_chunk_cue(merged_cue: dict) -> dict:
    """Convert a MergedCue to a ChunkCue (adds is_overlap field)."""
    return {
        "cue_id": merged_cue["cue_id"],
        "start_seconds": merged_cue["start_seconds"],
        "end_seconds": merged_cue["end_seconds"],
        "start_timestamp": merged_cue["start_timestamp"],
        "end_timestamp": merged_cue["end_timestamp"],
        "text": merged_cue["text"],
        "merged_count": merged_cue["merged_count"],
        "potential_boundary": merged_cue["potential_boundary"],
        "is_overlap": False,
    }


def _add_overlap(chunks: list[list[dict]]) -> list[list[dict]]:
    """Prepend last OVERLAP_CUES cues from chunk N to start of chunk N+1."""
    if len(chunks) <= 1:
        return chunks

    for i in range(len(chunks) - 1):
        # Take last OVERLAP_CUES cues from current chunk
        overlap_count = min(OVERLAP_CUES, len(chunks[i]))
        overlap_cues = chunks[i][-overlap_count:]

        # Create copies with is_overlap=True
        overlap_copies = []
        for cue in overlap_cues:
            copy = dict(cue)
            copy["is_overlap"] = True
            overlap_copies.append(copy)

        # Prepend to next chunk
        chunks[i + 1] = overlap_copies + chunks[i + 1]

    return chunks
