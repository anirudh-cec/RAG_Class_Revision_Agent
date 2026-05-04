# RAG Class Assistant

A Retrieval-Augmented Generation (RAG) application for ingesting class recording subtitles (`.vtt` files), code files, and GitHub repositories to create a searchable knowledge base. Users can ask questions about class topics and receive detailed answers with relevant code snippets.

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Settings Panel](#settings-panel)
- [Troubleshooting](#troubleshooting)

## Features

### Core RAG Pipeline
- **Dense Search (Semantic)**: Uses OpenAI embeddings via MeshAPI
- **Sparse Search (SPLADE)**: Lexical matching with SPLADE model
- **Hybrid Search**: Combines dense + sparse with Reciprocal Rank Fusion (RRF)
- **Cross-Encoder Reranking**: Uses `ms-marco-MiniLM-L6-v2` for final ranking

### Ingestion Pipeline
- **VTT Upload**: Parse and index subtitle files
- **Code Files**: Support for `.py`, `.js`, `.ts`, `.java`, etc.
- **GitHub Repos**: Clone and index repository contents

### Chat Interface
- **Claude-like UI**: Modern chat interface with streaming
- **Source Citations**: Shows which documents were used
- **Settings Panel**: Toggle hybrid search and reranking on/off

### Settings Panel
Users can configure search behavior via the UI:

| Setting | ON | OFF |
|---------|----|-----|
| **Hybrid Search** | Dense + Sparse + RRF | Dense only |
| **Reranking** | Cross-encoder reranking | Raw results to LLM |

## Architecture

### High-Level Flow
```
User Query
    ↓
[Settings Check]
    ↓
┌─────────────────────────────────────────┐
│  Hybrid Search ON                       │
│  ├── Dense Search (AstraDB)             │
│  ├── Sparse Search (SPLADE)             │
│  └── RRF Fusion                         │
│                                         │
│  Hybrid Search OFF                      │
│  └── Dense Search Only (AstraDB)        │
└─────────────────────────────────────────┘
    ↓
[Settings Check]
    ↓
┌─────────────────────────────────────────┐
│  Reranking ON                           │
│  └── Cross-Encoder (ms-marco-MiniLM)    │
│                                         │
│  Reranking OFF                          │
│  └── Skip reranking                     │
└─────────────────────────────────────────┘
    ↓
[LLM Generation]
    ↓
User Response
```

### Technology Stack

| Component | Technology |
|-----------|------------|
| Frontend | Streamlit |
| Backend | FastAPI |
| Vector DB | AstraDB |
| Embeddings | OpenAI via MeshAPI |
| LLM | GPT-4o-mini via MeshAPI |
| Search | Dense: AstraDB, Sparse: SPLADE |
| Reranking | cross-encoder/ms-marco-MiniLM-L6-v2 |

## Installation

### Prerequisites
- Python 3.12+
- pip

### Step 1: Clone Repository
```bash
git clone <repository-url>
cd RAG_Class_Revision_Agent
```

### Step 2: Create Virtual Environment
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables
Create a `.env` file in the project root:

```env
# AstraDB Configuration
ASTRA_DB_API_ENDPOINT=https://your-endpoint.apps.astra.datastax.com
ASTRA_DB_TOKEN=AstraCS:your-token
ASTRA_DB_COLLECTION=document_chunks

# MeshAPI Configuration (for LLM and Embeddings)
MESH_API_KEY=your-mesh-api-key

# Optional: API Configuration
API_HOST=0.0.0.0
API_PORT=8000
```

## Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `ASTRA_DB_API_ENDPOINT` | Yes | AstraDB API endpoint URL |
| `ASTRA_DB_TOKEN` | Yes | AstraDB authentication token |
| `ASTRA_DB_COLLECTION` | No | Collection name (default: document_chunks) |
| `MESH_API_KEY` | Yes | MeshAPI key for LLM and embeddings |
| `API_HOST` | No | API host (default: 0.0.0.0) |
| `API_PORT` | No | API port (default: 8000) |

## Usage

### Start the Backend API

For normal retrieval (no hybrid search/reranking):
```bash
python simple_api.py
```

The API will be available at `http://localhost:8000`

### Start the Frontend

```bash
streamlit run frontend/app.py
```

The frontend will be available at `http://localhost:8501`

### Using the Application

1. **Open the frontend** at http://localhost:8501
2. **Ingest documents** (optional):
   - Upload VTT files
   - Upload code files
   - Add GitHub repository URLs
3. **Click "Go to Chat"** button
4. **Ask questions** about your documents
5. **Configure search settings** via the "⚙️ Show Settings" button:
   - Toggle Hybrid Search ON/OFF
   - Toggle Reranking ON/OFF
   - Adjust candidate counts

## API Endpoints

### Simple API (Normal Retrieval)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API info |
| `/health` | GET | Health check |
| `/chat` | POST | Chat with RAG |

### Chat Endpoint

**POST** `/chat`

Request:
```json
{
  "query": "What is Python?",
  "conversation_id": "optional-id",
  "top_k": 5
}
```

Response:
```json
{
  "conversation_id": "uuid",
  "answer": "Python is a programming language...",
  "sources": [
    {
      "chunk_id": "...",
      "document_id": "...",
      "content": "...",
      "score": 0.95
    }
  ]
}
```

## Settings Panel

The settings panel allows users to configure search behavior without code changes:

### Hybrid Search Toggle
- **ON**: Uses dense + sparse search with RRF fusion
- **OFF**: Uses dense search only (simpler, no torch needed)

### Reranking Toggle
- **ON**: Uses cross-encoder (ms-marco-MiniLM-L6-v2) for final ranking
- **OFF**: Returns raw search results directly to LLM

### Candidate Counts
- **Dense candidates**: Number of results from dense search (10-200)
- **Sparse candidates**: Number of results from sparse search (10-200)
- **Rerank candidates**: Number of top results to rerank (5-100)
- **Final results**: Number of results sent to LLM (1-20)

## License

[Your License Here]

## Contributors

[Your Name/Team Here]
