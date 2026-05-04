#!/usr/bin/env python3
"""
Startup script for the Retrieval API

Usage:
    python start_retrieval_api.py

Or with options:
    python start_retrieval_api.py --host 0.0.0.0 --port 8080 --reload
"""

import argparse
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))


def main():
    parser = argparse.ArgumentParser(description="Start the RAG Retrieval API")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    parser.add_argument("--workers", type=int, default=1, help="Number of workers")

    args = parser.parse_args()

    print("=" * 60)
    print("🚀 RAG Retrieval API")
    print("=" * 60)
    print(f"Host: {args.host}")
    print(f"Port: {args.port}")
    print(f"Reload: {args.reload}")
    print(f"Workers: {args.workers}")
    print("=" * 60)
    print("\nStarting server...\n")

    # Import here to avoid circular imports
    import uvicorn

    uvicorn.run(
        "src.retrieval.api.main:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        workers=args.workers if not args.reload else 1
    )


if __name__ == "__main__":
    main()
