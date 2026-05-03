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

## Tech Stack

| Layer           | Technology              |
| --------------- | ----------------------- |
| Frontend        | Streamlit               |
| VTT Parsing     | Custom parser           |
| Code Parsing    | Tree-sitter / AST (TBD) |
| GitHub Fetching | GitHub REST API (TBD)   |
| Embeddings      | TBD                     |
| Vector Store    | TBD                     |
| LLM             | TBD                     |
| Backend         | Python (src/)           |
| Python          | >=3.12                  |

---

## Key Design Decisions (To Decide)

* [ ] Chunking strategy for VTT (by time window vs. by topic/pause)
* [ ] How to handle multi-session VTT files (multiple class recordings)
* [ ] Code chunking granularity (file-level vs. function-level)
* [ ] GitHub — full repo or specific folders/branches only?
* [ ] Auth & multi-user support (single user vs. multi-tenant)
* [ ] Persistence — should indexed data persist across sessions?

---

## File Structure

```
project-root/
├── CLAUDE.md                ← This file
├── pyproject.toml           ← Project metadata, dependencies, tool configs
├── requirements.txt         ← Pinned dependencies (single file, project root)
├── .env                     ← API keys and secrets (gitignored)
├── app.py                   ← Entry point alias
├── frontend/                ← Streamlit UI
│   ├── app.py               ← Streamlit main entry point
│   ├── components/          ← Reusable UI components
│   │   ├── file_uploader.py
│   │   ├── github_input.py
│   │   ├── review_card.py
│   │   └── step_indicator.py
│   ├── pages/               ← Step-based page routing
│   │   ├── landing.py
│   │   ├── vtt_upload.py
│   │   ├── code_upload.py
│   │   ├── github_upload.py
│   │   ├── review.py
│   │   └── success.py
│   ├── styles/
│   │   └── custom_css.py
│   └── utils/
│       ├── file_handler.py
│       ├── session_state.py
│       └── validators.py
├── src/                     ← Core backend logic
│   ├── logger/
│   │   └── custom_logger.py
│   └── exception/
│       └── custom_exception.py
├── tests/                   ← Test suite
├── architecture/            ← Architecture docs
├── docs/                    ← Project documentation
├── logs/                    ← Runtime logs (gitignored)
└── data/                    ← Raw uploads (gitignored)
```

---

## Running the App

```bash
# Install dependencies
pip install -r requirements.txt

# Run the Streamlit frontend
streamlit run frontend/app.py
```

---

## Notes

* This file is updated iteratively as the project evolves
* Decisions marked TBD will be locked down in subsequent planning sessions
* All sensitive keys (API keys, tokens) go in `.env` — never committed to git
* Dependencies are managed in a single `requirements.txt` at the project root
* we will be using astra db as vectordb below are details how to access that
* 

Install an adequate version of the [astrapy package](https://github.com/datastax/astrapy) (note: Python 3.9+ and pip 23.0+ versions required).

```python
pip install --upgrade astrapy
```


from astrapy import DataAPIClient

# Initialize the client

client = DataAPIClient()
db = client.get_database(
  api_endpoint="YOUR_API_ENDPOINT",
  token="YOUR_TOKEN",
)

print(f"Connected to Astra DB: {db.list_collection_names()}")


* we will be using meshapi for accessing LLM, both for embedding and normal llm.
* How to use it  is shown below

# pip install openai

from openai import OpenAI
client = OpenAI(
api_key=os.environ["MESH_API_KEY"],
base_url="https://api.meshapi.ai/v1",
)
resp = client.chat.completions.create(
model="openai/gpt-4o-mini",
messages=[{"role": "user", "content": "Hello!"}],
)
print(resp.choices[0].message.content)
