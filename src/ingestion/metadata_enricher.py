"""Phase 5: Compute per-chunk metadata and auto-tag chunk_type."""

from src.ingestion.config import (
    CODE_WALKTHROUGH_KEYWORDS,
    QA_KEYWORDS,
    TOPIC_HINT_MAX_CHARS,
)
from src.ingestion.vtt_parser import _format_timestamp


def enrich(chunks: list[list[dict]], source_file: str) -> list[dict]:
    """Enrich chunks with metadata and chunk_type classification.

    Args:
        chunks: List of chunks (each a list of ChunkCue dicts) from Phase 4.
        source_file: Original .vtt filename for metadata.

    Returns:
        List of Chunk dicts with full metadata.
    """
    enriched = []

    for i, cues in enumerate(chunks):
        # Separate overlap and non-overlap cues for metadata calculations
        non_overlap_cues = [c for c in cues if not c["is_overlap"]]

        if not non_overlap_cues:
            # Edge case: chunk is entirely overlap cues (shouldn't happen)
            non_overlap_cues = cues

        text = " ".join(c["text"] for c in non_overlap_cues)
        start_seconds = non_overlap_cues[0]["start_seconds"]
        end_seconds = non_overlap_cues[-1]["end_seconds"]
        start_time = _format_timestamp(start_seconds)
        end_time = _format_timestamp(end_seconds)
        duration_seconds = end_seconds - start_seconds
        cue_count = len(non_overlap_cues)
        topic_hint = _extract_topic_hint(text)
        chunk_type = _classify_chunk_type(text)

        enriched.append(
            {
                "chunk_id": i,
                "text": text,
                "start_time": start_time,
                "end_time": end_time,
                "start_seconds": start_seconds,
                "end_seconds": end_seconds,
                "duration_seconds": duration_seconds,
                "cue_count": cue_count,
                "topic_hint": topic_hint,
                "chunk_type": chunk_type,
                "source_file": source_file,
                "cues": cues,
            }
        )

    return enriched


def _classify_chunk_type(text: str) -> str:
    """Classify a chunk's text as code_walkthrough, qa, or explanation.

    Priority: code_walkthrough > qa > explanation.
    """
    text_lower = text.lower()

    for keyword in CODE_WALKTHROUGH_KEYWORDS:
        if keyword in text_lower:
            return "code_walkthrough"

    for keyword in QA_KEYWORDS:
        if keyword in text_lower:
            return "qa"

    return "explanation"


def _extract_topic_hint(text: str) -> str:
    """Extract the first sentence of text as a topic hint.

    Returns the first sentence (up to first ., ?, or !), truncated to
    TOPIC_HINT_MAX_CHARS if needed.
    """
    # Find earliest sentence terminator
    earliest = len(text)
    for char in (".", "?", "!"):
        idx = text.find(char)
        if idx != -1 and idx < earliest:
            earliest = idx

    if earliest < len(text):
        hint = text[: earliest + 1]
    else:
        # No sentence terminator found
        hint = text[:TOPIC_HINT_MAX_CHARS]

    if len(hint) > TOPIC_HINT_MAX_CHARS:
        hint = hint[: TOPIC_HINT_MAX_CHARS - 3] + "..."

    return hint.strip()
