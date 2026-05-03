"""Phase 2: Merge consecutive short cues into sentence-level MergedCue objects."""

from src.ingestion.config import MERGE_GAP_THRESHOLD_SECONDS, MERGE_MAX_CHARS


def merge_cues(cues: list[dict]) -> list[dict]:
    """Merge consecutive short cues into sentence-level merged cues.

    Args:
        cues: List of Cue objects from Phase 1.

    Returns:
        List of MergedCue dicts with potential_boundary set to False.
    """
    if not cues:
        return []

    if len(cues) == 1:
        return [_cue_to_merged(cues[0], 1)]

    result = []
    buf_text = cues[0]["text"]
    buf_start = cues[0]
    buf_end_seconds = cues[0]["end_seconds"]
    buf_end_timestamp = cues[0]["end_timestamp"]
    buf_count = 1

    for i in range(1, len(cues)):
        cue = cues[i]
        gap = cue["start_seconds"] - buf_end_seconds
        combined_len = len(buf_text) + 1 + len(cue["text"])

        # Check merge-blocking conditions
        gap_too_large = gap > MERGE_GAP_THRESHOLD_SECONDS
        chars_exceeded = combined_len > MERGE_MAX_CHARS
        sentence_boundary = (
            buf_text.rstrip().endswith((".", "?", "!"))
            and cue["text"].lstrip()
            and cue["text"].lstrip()[0].isupper()
        )

        if gap_too_large or chars_exceeded or sentence_boundary:
            # Flush buffer as a merged cue
            result.append(_build_merged(buf_start, buf_text, buf_end_seconds, buf_end_timestamp, buf_count))
            # Reset buffer with current cue
            buf_text = cue["text"]
            buf_start = cue
            buf_end_seconds = cue["end_seconds"]
            buf_end_timestamp = cue["end_timestamp"]
            buf_count = 1
        else:
            # Merge: extend buffer
            buf_text = buf_text + " " + cue["text"]
            buf_end_seconds = cue["end_seconds"]
            buf_end_timestamp = cue["end_timestamp"]
            buf_count += 1

    # Flush remaining buffer
    result.append(_build_merged(buf_start, buf_text, buf_end_seconds, buf_end_timestamp, buf_count))

    return result


def _build_merged(
    start_cue: dict,
    text: str,
    end_seconds: float,
    end_timestamp: str,
    merged_count: int,
) -> dict:
    """Build a MergedCue dict from buffer state."""
    return {
        "cue_id": start_cue["cue_id"],
        "start_seconds": start_cue["start_seconds"],
        "end_seconds": end_seconds,
        "start_timestamp": start_cue["start_timestamp"],
        "end_timestamp": end_timestamp,
        "text": text,
        "merged_count": merged_count,
        "potential_boundary": False,
    }


def _cue_to_merged(cue: dict, merged_count: int) -> dict:
    """Convert a single Cue to a MergedCue."""
    return {
        "cue_id": cue["cue_id"],
        "start_seconds": cue["start_seconds"],
        "end_seconds": cue["end_seconds"],
        "start_timestamp": cue["start_timestamp"],
        "end_timestamp": cue["end_timestamp"],
        "text": cue["text"],
        "merged_count": merged_count,
        "potential_boundary": False,
    }
