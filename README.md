# Internal Document RAG Assistant

This project is an end-to-end Retrieval-Augmented Generation (RAG) system for answering questions over internal company documents. It ingests documents, chunks them, creates embeddings, stores them in a local ChromaDB vector database, retrieves relevant context for a user question, and generates a grounded answer with source attribution.

## Features

- Supports `.txt`, `.md`, `.pdf`, and `.docx` files
- Local semantic search using Sentence Transformers embeddings
- Persistent vector storage using ChromaDB
- Streamlit UI for natural language questions
- Source attribution for every answer
- Fallback extractive mode if no LLM API key is configured
- Clean project structure suitable for interview review

## Architecture

```text
Documents in data/
        ↓
Document loader
        ↓
Text chunking with overlap
        ↓
Sentence Transformer embeddings
        ↓
ChromaDB vector database
        ↓
User question
        ↓
Semantic retrieval of top-k chunks
        ↓
LLM answer generation
        ↓
Answer + source documents
```

## Why these choices?

### Python
Python has strong ecosystem support for NLP, embeddings, vector databases, and rapid UI development.

### Streamlit
Streamlit makes it easy to build a minimal but professional interface quickly. It is suitable for a take-home assignment because reviewers can run it locally with one command.

### Sentence Transformers
The project uses `sentence-transformers/all-MiniLM-L6-v2` for embeddings. It is lightweight, fast, and works locally without requiring a paid embedding API.

### ChromaDB
ChromaDB is a simple local vector database. It persists the vector index on disk and works well for small to medium document corpora.

### OpenAI-compatible LLM call
The app can use an OpenAI chat model when `OPENAI_API_KEY` is configured. If no key is configured, the app still runs in extractive retrieval mode so the pipeline can be demonstrated.

## Windows Setup

### 1. Open project in VS Code

Open VS Code and select:

```text
File → Open Folder → orbrick-rag-assistant
```

### 2. Create virtual environment

Open VS Code terminal and run:

```bash
python -m venv .venv
```

### 3. Activate virtual environment

```bash
.venv\Scripts\activate
```

You should see `(.venv)` in the terminal.

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Optional: configure LLM key

Copy `.env.example` to `.env`.

```bash
copy .env.example .env
```

Open `.env` and replace:

```text
OPENAI_API_KEY=your_openai_api_key_here
```

with your real API key.

If you skip this step, the app still runs but shows retrieved context instead of a polished LLM-generated answer.

### 6. Ingest documents

```bash
python ingest.py
```

This creates the local ChromaDB vector database.

### 7. Run app

```bash
streamlit run app.py
```

Open the browser URL shown by Streamlit.

## Example Questions

- How many annual leave days are employees eligible for?
- What should employees do if they receive an unexpected MFA prompt?
- What documents must a new employee submit before joining?
- Within how many days must expense claims be submitted?
- What is the first response time target for a P1 support ticket?

## Source Attribution

The app displays source documents under every answer. It also exposes the exact retrieved chunks inside the "View retrieved chunks" section. This makes the answer auditable and grounded in the document corpus.

## How to Add More Documents

Put additional `.txt`, `.md`, `.pdf`, or `.docx` files into the `data/` folder and run:

```bash
python ingest.py
```

Then restart the Streamlit app or click "Update index" from the sidebar.

## Running Tests

```bash
source .venv/bin/activate
python -m pytest tests/ -v
```

46 tests covering document loading, text splitting, vector store (with mocked dependencies), and answer generation.
