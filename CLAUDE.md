# CLAUDE.md — Class Recording RAG App

## Project Overview

A Retrieval-Augmented Generation (RAG) application that ingests class recording subtitles (`.vtt` files), associated code files, and GitHub repositories to create a searchable knowledge base. Users can ask questions about class topics and receive detailed answers with relevant code snippets.

---

## High-Level Architecture

### 1. Input Pipeline (Ingestion)

**Step 1 — VTT Upload**

* User uploads one or more `.vtt` subtitle files from class recordings
* VTT files are parsed and cleaned (strip timestamps, speaker labels, formatting tags)
* Cleaned transcript text is chunked and indexed

**Step 2 — Code File Upload (Optional)**

* User is prompted: *"Do you have any code files discussed in the class?"*
* If yes: upload code files (`.py`, `.js`, `.ts`, `.java`, etc.)
* Code files are parsed, chunked by function/class/block, and indexed alongside transcript chunks

**Step 3 — GitHub Link (Optional)**

* User is prompted: *"Do you have any GitHub repository links?"*
* If yes: provide one or more GitHub URLs
* Repo contents are fetched (README, source files) and indexed

---

### 2. Processing & Indexing

* **VTT Parser** — strips VTT formatting, segments transcript into meaningful chunks (e.g., per topic/time window)
* **Code Parser** — language-aware chunking (functions, classes, top-level blocks)
* **GitHub Fetcher** — clones or fetches repo tree via GitHub API, extracts relevant source files
* **Embeddings** — all chunks (transcript + code + repo) are embedded using an embedding model
* **Vector Store** — embeddings stored in a vector database for similarity search

---

### 3. RAG Query Engine

* User asks a question via a chat interface
* Question is embedded and matched against the vector store
* Top-K relevant chunks (transcript context + code snippets) are retrieved
* Retrieved context is passed to an LLM to generate a detailed answer
* Response includes:
  * Explanation from the class transcript
  * Relevant code snippets (with language tags)
  * Source references (timestamp, file name, GitHub link)

---

### 4. Frontend (UI Flow)

```
[Upload VTT File]
       ↓
[Any code files? Yes/No]
       ↓ (if Yes)
[Upload Code Files]
       ↓
[Any GitHub links? Yes/No]
       ↓ (if Yes)
[Enter GitHub URLs]
       ↓
[Processing & Indexing]
       ↓
[Chat Interface — Ask Questions]
       ↓
[Answer with transcript context + code snippets]
```

---

## Tech Stack (TBD — to be confirmed as we go)

| Layer           | Options                                        |
| --------------- | ---------------------------------------------- |
| Frontend        | React / Next.js                                |
| VTT Parsing     | Custom parser /`webvtt-py`                   |
| Code Parsing    | Tree-sitter / language-specific AST            |
| GitHub Fetching | GitHub REST API /`PyGithub`                  |
| Embeddings      | OpenAI `text-embedding-ada-002`/ HuggingFace |
| Vector Store    | Pinecone / Chroma / FAISS                      |
| LLM             | Claude (Anthropic API) / OpenAI GPT            |
| Backend         | FastAPI / Node.js                              |

---

## Key Design Decisions (To Decide)

* [ ] Chunking strategy for VTT (by time window vs. by topic/pause)
* [ ] How to handle multi-session VTT files (multiple class recordings)
* [ ] Code chunking granularity (file-level vs. function-level)
* [ ] GitHub — full repo or specific folders/branches only?
* [ ] Auth & multi-user support (single user vs. multi-tenant)
* [ ] Persistence — should indexed data persist across sessions?

---

## File Structure (Proposed)

```
project-root/
├── CLAUDE.md               ← This file
├── frontend/               ← UI (React/Next.js)
│   └── src/
├── backend/                ← API server
│   ├── ingestion/
│   │   ├── vtt_parser.py
│   │   ├── code_parser.py
│   │   └── github_fetcher.py
│   ├── embeddings/
│   ├── vector_store/
│   └── rag/
│       └── query_engine.py
├── data/                   ← Raw uploads (gitignored)
└── README.md
```

---

## Notes

* This file will be updated iteratively as the project evolves
* Decisions marked TBD will be locked down in subsequent planning sessions
* All sensitive keys (API keys, tokens) go in `.env` — never committed to git
