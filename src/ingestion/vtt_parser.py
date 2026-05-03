"""Phase 1: Parse VTT files into structured Cue objects."""

import os
import re

from src.ingestion.config import TOPIC_HINT_MAX_CHARS


def parse_vtt(file_path: str) -> list[dict]:
    """Parse a VTT file into a list of Cue dicts.

    Args:
        file_path: Path to a .vtt file.

    Returns:
        List of Cue dicts ordered by start_seconds ascending.

    Raises:
        FileNotFoundError: If file_path does not exist.
        ValueError: If the file is not a valid VTT (missing WEBVTT header).
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"VTT file not found: {file_path}")

    with open(file_path, encoding="utf-8") as f:
        raw = f.read()

    # Strip UTF-8 BOM if present
    if raw.startswith("﻿"):
        raw = raw[1:]

    # Normalize line endings
    raw = raw.replace("\r\n", "\n")

    # Validate WEBVTT header
    if not raw.lstrip().startswith("WEBVTT"):
        raise ValueError(f"Invalid VTT file: missing WEBVTT header in {file_path}")

    cues = _extract_cues(raw)
    return cues


def _extract_cues(raw: str) -> list[dict]:
    """Extract cue objects from normalized VTT text."""
    # Split into blocks by one or more blank lines
    blocks = re.split(r"\n\n+", raw.strip())

    cues = []
    cue_id = 0

    for block in blocks:
        lines = block.strip().split("\n")
        timestamp_line_idx = None
        start_ts = None
        end_ts = None
        text_lines = []

        for line in lines:
            # Skip WEBVTT header line
            if line.strip().startswith("WEBVTT"):
                continue

            # Skip standalone cue index numbers
            if re.match(r"^\d+$", line.strip()):
                continue

            # Check for timestamp line
            ts_match = re.match(
                r"^(\d{2}:\d{2}:\d{2}\.\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2}\.\d{3})",
                line.strip(),
            )
            if ts_match:
                start_ts = ts_match.group(1)
                end_ts = ts_match.group(2)
                timestamp_line_idx = True
                continue

            # Everything else is text content
            text_lines.append(line.strip())

        # Only create a cue if we have both timestamps and text
        if start_ts and end_ts and text_lines:
            text = _clean_text(" ".join(text_lines))
            if text:
                cues.append(
                    {
                        "cue_id": cue_id,
                        "start_seconds": _parse_timestamp(start_ts),
                        "end_seconds": _parse_timestamp(end_ts),
                        "start_timestamp": start_ts,
                        "end_timestamp": end_ts,
                        "text": text,
                    }
                )
                cue_id += 1

    return cues


def _clean_text(text: str) -> str:
    """Clean cue text: strip speaker labels, HTML tags, normalize whitespace."""
    # Strip HTML-like tags
    text = re.sub(r"</?([ibuc]|strong|em|mark|span)\b[^>]*>", "", text)

    # Strip speaker labels (e.g. "PAUL:" or "INSTRUCTOR 1:" at start)
    text = re.sub(r"^[A-Z][A-Z\s]*:\s*", "", text)

    # Collapse multiple spaces and strip
    text = re.sub(r"\s+", " ", text).strip()

    return text


def _parse_timestamp(ts: str) -> float:
    """Convert a VTT timestamp string to total seconds.

    Args:
        ts: Timestamp in "HH:MM:SS.mmm" format.

    Returns:
        Total seconds as float.

    Example:
        "01:23:45.678" -> 5025.678
    """
    parts = ts.split(":")
    hours = int(parts[0])
    minutes = int(parts[1])
    sec_parts = parts[2].split(".")
    seconds = int(sec_parts[0])
    milliseconds = int(sec_parts[1]) if len(sec_parts) > 1 else 0

    return hours * 3600 + minutes * 60 + seconds + milliseconds / 1000


def _format_timestamp(total_seconds: float) -> str:
    """Convert total seconds to "HH:MM:SS" format string.

    Args:
        total_seconds: Seconds as float.

    Returns:
        Timestamp string like "01:23:45" (no milliseconds).
    """
    total_seconds = max(0, total_seconds)
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    seconds = int(total_seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
