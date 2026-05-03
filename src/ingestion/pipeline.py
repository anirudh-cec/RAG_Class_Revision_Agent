"""Phase 6: Orchestrate all phases, write output, validate."""

import json
import os
from collections import Counter

from src.ingestion.chunk_builder import build_chunks
from src.ingestion.config import (
    MAX_CHUNK_TEXT_LENGTH,
    MAX_TOTAL_CHUNKS,
    MIN_CHUNK_TEXT_LENGTH,
    MIN_TOTAL_CHUNKS,
)
from src.ingestion.cue_merger import merge_cues
from src.ingestion.metadata_enricher import enrich
from src.ingestion.topic_detector import detect_boundaries
from src.ingestion.vtt_parser import parse_vtt


def run_vtt_chunking_pipeline(
    vtt_file_path: str,
    output_dir: str = "data/chunks",
) -> dict:
    """Run the full VTT chunking pipeline.

    Args:
        vtt_file_path: Path to the .vtt file.
        output_dir: Directory for output JSON files.

    Returns:
        dict with keys "chunks", "summary", and "validation".

    Raises:
        FileNotFoundError: If vtt_file_path does not exist.
        ValueError: If VTT parsing fails.
    """
    # Phase 1: Parse VTT
    cues = parse_vtt(vtt_file_path)

    # Phase 2: Merge cues
    merged = merge_cues(cues)

    # Phase 3: Detect boundaries
    merged = detect_boundaries(merged)

    # Phase 4: Build chunks
    raw_chunks = build_chunks(merged)

    # Phase 5: Enrich metadata
    source_file = os.path.basename(vtt_file_path)
    chunks = enrich(raw_chunks, source_file)

    # Phase 6: Output and validate
    os.makedirs(output_dir, exist_ok=True)

    summary = [_chunk_to_summary(c) for c in chunks]

    chunks_path = os.path.join(output_dir, "chunks.json")
    summary_path = os.path.join(output_dir, "chunks_summary.json")

    with open(chunks_path, "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=2, ensure_ascii=False)

    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    validation = _validate_chunks(chunks)
    _print_summary(chunks, validation)

    return {
        "chunks": chunks,
        "summary": summary,
        "validation": validation,
    }


def _chunk_to_summary(chunk: dict) -> dict:
    """Extract summary fields from a full chunk object."""
    return {
        "chunk_id": chunk["chunk_id"],
        "start_time": chunk["start_time"],
        "end_time": chunk["end_time"],
        "topic_hint": chunk["topic_hint"],
        "chunk_type": chunk["chunk_type"],
        "cue_count": chunk["cue_count"],
    }


def _validate_chunks(chunks: list[dict]) -> dict:
    """Validate chunk output against quality thresholds."""
    total_chunks = len(chunks)
    avg_duration = (
        sum(c["duration_seconds"] for c in chunks) / total_chunks if total_chunks else 0.0
    )
    type_distribution = dict(Counter(c["chunk_type"] for c in chunks))

    errors = []
    warnings = []

    # Total chunk count
    if total_chunks < MIN_TOTAL_CHUNKS or total_chunks > MAX_TOTAL_CHUNKS:
        errors.append(
            f"Total chunks {total_chunks} outside expected range "
            f"[{MIN_TOTAL_CHUNKS}-{MAX_TOTAL_CHUNKS}]"
        )

    # Per-chunk text length
    for chunk in chunks:
        text_len = len(chunk["text"])
        if text_len < MIN_CHUNK_TEXT_LENGTH:
            errors.append(
                f"Chunk {chunk['chunk_id']} has text under {MIN_CHUNK_TEXT_LENGTH} chars ({text_len})"
            )
        if text_len > MAX_CHUNK_TEXT_LENGTH:
            errors.append(
                f"Chunk {chunk['chunk_id']} has text over {MAX_CHUNK_TEXT_LENGTH} chars ({text_len})"
            )

    # Warnings
    for chunk in chunks:
        if chunk["cue_count"] < 3:
            warnings.append(
                f"Chunk {chunk['chunk_id']} has only {chunk['cue_count']} cues"
            )

    if "code_walkthrough" not in type_distribution:
        warnings.append("No code_walkthrough chunks detected")
    if "qa" not in type_distribution:
        warnings.append("No qa chunks detected")

    passed = len(errors) == 0

    return {
        "passed": passed,
        "total_chunks": total_chunks,
        "avg_duration_seconds": round(avg_duration, 1),
        "type_distribution": type_distribution,
        "warnings": warnings,
        "errors": errors,
    }


def _print_summary(chunks: list[dict], validation: dict) -> None:
    """Print a human-readable summary of the pipeline output."""
    print("=" * 50)
    print("VTT Chunking Pipeline Summary")
    print("=" * 50)
    print(f"Total chunks: {validation['total_chunks']}")
    print(f"Avg chunk duration: {validation['avg_duration_seconds']}s")
    print("Chunk type distribution:")
    for chunk_type, count in sorted(validation["type_distribution"].items()):
        print(f"  {chunk_type}: {count}")

    status = "PASSED" if validation["passed"] else "FAILED"
    print(f"Validation: {status}")
    print(f"Errors: {len(validation['errors'])} | Warnings: {len(validation['warnings'])}")

    for error in validation["errors"]:
        print(f"  ERROR: {error}")
    for warning in validation["warnings"]:
        print(f"  WARNING: {warning}")
    print("=" * 50)
