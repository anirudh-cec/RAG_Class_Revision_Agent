"""Configuration constants for the VTT chunking pipeline."""

# Phase 2 — Cue merging
MERGE_GAP_THRESHOLD_SECONDS: float = 3.0
MERGE_MAX_CHARS: int = 300

# Phase 3 — Topic boundary detection
SILENCE_GAP_BOUNDARY_SECONDS: float = 8.0
TOPIC_SIGNAL_PHRASES: list[str] = [
    "alright so",
    "alright,",
    "okay so",
    "so now",
    "now let",
    "next,",
    "next step",
    "the next",
    "let me show",
    "let me open",
    "let me explain",
    "let me just",
    "let me go",
    "moving on",
    "so what we",
    "so the idea",
    "so basically",
    "so here",
    "in summary",
    "to summarize",
    "so this is",
    "this particular",
    "notebook",
    "step ",
    "part ",
    "section",
]

# Phase 4 — Chunk building
TOPIC_SIGNAL_MIN_CUES: int = 5
CHUNK_HARD_CAP_CUES: int = 20
OVERLAP_CUES: int = 2

# Phase 5 — Chunk type classification
CODE_WALKTHROUGH_KEYWORDS: list[str] = [
    "notebook",
    "execute",
    "cell",
    "import",
    "function",
    "def ",
    "class ",
    "pip install",
]
QA_KEYWORDS: list[str] = [
    "question",
    "anyone",
    "let me know",
    "in the chat",
    "yes,",
    "no,",
]

# Phase 6 — Validation
MIN_CHUNK_TEXT_LENGTH: int = 100
MAX_CHUNK_TEXT_LENGTH: int = 3000
MIN_TOTAL_CHUNKS: int = 80
MAX_TOTAL_CHUNKS: int = 200

# Phase 5 — Topic hint
TOPIC_HINT_MAX_CHARS: int = 120
