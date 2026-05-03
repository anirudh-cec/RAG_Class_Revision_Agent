"""Phase 3: Detect topic boundaries via keyword signals and silence gaps."""

from src.ingestion.config import SILENCE_GAP_BOUNDARY_SECONDS, TOPIC_SIGNAL_PHRASES


def detect_boundaries(merged_cues: list[dict]) -> list[dict]:
    """Detect topic boundaries and set potential_boundary on merged cues.

    Args:
        merged_cues: List of MergedCue objects from Phase 2.

    Returns:
        Same list with potential_boundary field updated in-place.
    """
    for i, cue in enumerate(merged_cues):
        is_boundary = False

        # Keyword check
        if _contains_topic_signal(cue["text"]):
            is_boundary = True

        # Silence gap check (skip first cue — no previous to compare)
        if i > 0:
            gap = cue["start_seconds"] - merged_cues[i - 1]["end_seconds"]
            if gap > SILENCE_GAP_BOUNDARY_SECONDS:
                is_boundary = True

        cue["potential_boundary"] = is_boundary

    return merged_cues


def _contains_topic_signal(text: str) -> bool:
    """Check if text contains any topic-signal phrase (case-insensitive).

    Args:
        text: Cue text to check.

    Returns:
        True if any trigger phrase is found as a substring.
    """
    text_lower = text.lower()
    return any(phrase in text_lower for phrase in TOPIC_SIGNAL_PHRASES)
