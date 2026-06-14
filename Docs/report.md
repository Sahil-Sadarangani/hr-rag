# Repository Report: Internal Document RAG Assistant

## 1. Overview

A Retrieval-Augmented Generation (RAG) system that ingests internal company documents, indexes them via semantic embeddings, and answers natural language questions with grounded answers and source attribution. Built as a portfolio/interview project.

**Tech stack:** Python 3, Streamlit, ChromaDB, SentenceTransformers, OpenAI API

---

## 2. Directory Structure

```
hr-rag/
├── app.py                     # Streamlit UI — main entry point
├── ingest.py                  # CLI ingestion script (load → chunk → embed → store)
├── requirements.txt           # Python dependencies
├── README.md                  # Setup & usage documentation
├── report.md                  # Original project report (problem, approach, conclusion)
├── sample_questions.txt       # Example questions for testing
├── architecture.md            # [NEW] Detailed architecture & design analysis
├── repo_report.md             # [NEW] This file — full repository report
├── future_improvements.md     # [NEW] Improvement roadmap
├── .env.example               # Environment variable template
├── .env                       # Local env config (gitignored)
├── .gitignore                 # Git ignore rules
├── data/                      # Document corpus
│   ├── employee_onboarding.txt
│   ├── expense_policy.txt
│   ├── hr_leave_policy.txt
│   ├── it_security_policy.txt
│   └── product_support_manual.txt
├── .streamlit/
│   └── config.toml            # Streamlit server config (fileWatcherType=none)
├── src/                       # Core application modules
│   ├── __init__.py
│   ├── config.py              # Central config (paths, model names, API keys)
│   ├── document_loader.py     # Load .txt/.md/.pdf/.docx files
│   ├── text_splitter.py       # Character-based chunking with overlap
│   ├── vector_store.py        # Embedding + ChromaDB operations
│   ├── rag_chain.py           # LLM answer generation + fallback
├── chroma_db/                 # Persistent vector database (gitignored)
│   ├── chroma.sqlite3
│   └── 054dd7b2-.../
└── .venv/                     # Python virtual environment (gitignored)
```

**Total source files:** 7 Python modules, 2 entry-point scripts, 5 documents.

---

## 3. Component Breakdown

### 3.1 `app.py` (81 lines)
Streamlit single-page application. Provides sidebar index status + "Update index" and "Rebuild from scratch" buttons, question input, top-k slider, answer display, source attribution, and expandable raw chunk viewer.

### 3.2 `ingest.py` (23 lines)
CLI script that orchestrates the full ingestion pipeline. Can be run independently of the UI. Prints progress at each stage.

### 3.3 `src/config.py` (18 lines)
Reads `.env` via `python-dotenv`. Exposes 4 path constants and 3 environment variables (`OPENAI_API_KEY`, `OPENAI_MODEL`, `EMBEDDING_MODEL_NAME`) with sensible defaults.

### 3.4 `src/document_loader.py` (70 lines)
- `LoadedDocument` dataclass — source filename + raw text
- `load_single_document()` — dispatches to format-specific readers
- `load_documents()` — iterates directory, filters by supported extensions, returns non-empty documents

**Supported formats:** `.txt`, `.md` (raw read), `.pdf` (via `pypdf`, with page markers), `.docx` (via `python-docx`)

### 3.5 `src/text_splitter.py` (69 lines)
- `TextChunk` dataclass — id, source, chunk_index, text
- `clean_text()` — normalizes whitespace, collapses excessive newlines
- `split_text()` — character-based splitting at 900 chars with 180-char overlap, prefers sentence boundaries
- `make_chunks()` — applies splitting across all documents, generates unique chunk IDs

### 3.6 `src/vector_store.py` (115 lines)
- `get_embedding_model()` — lazy-loaded singleton for SentenceTransformer
- `embed_texts()` — batch encoding with L2 normalization
- `get_chroma_client()` / `get_collection()` — persistent ChromaDB access
- `reset_vector_database()` — full index deletion
- `build_vector_store(force_rebuild=False)` — incremental by default; `force_rebuild=True` does full reset + re-embed
- `query_vector_store()` — embed query → ChromaDB similarity search → return structured results

### 3.7 `src/rag_chain.py` (81 lines)
- `build_context()` — formats retrieved chunks into a prompt-ready string
- `fallback_extractive_answer()` — returns top chunk verbatim when no API key is present
- `generate_answer()` — dispatches to OpenAI or fallback based on key presence
- `unique_sources()` — deduplicates source filenames

**System prompt:** Strict instruction to answer only from provided context, cite sources, and refuse to invent information.

---

## 4. Dependencies (`requirements.txt`)

| Library | Version | Purpose |
|---|---|---|
| `streamlit` | >=1.37.0 | Web UI framework |
| `chromadb` | >=0.5.0 | Vector database (persistent local storage) |
| `sentence-transformers` | >=3.0.0 | Local embedding model |
| `pypdf` | >=4.0.0 | PDF parsing |
| `python-docx` | >=1.1.0 | DOCX parsing |
| `python-dotenv` | >=1.0.1 | Environment variable loading |
| `openai` | >=1.40.0 | OpenAI-compatible LLM API client |
| `numpy` | >=1.26.0 | Numerical operations (transitive dependency) |

---

## 5. Document Corpus

5 documents covering an internal company scenario:

| File | Topics | Lines |
|---|---|---|
| `employee_onboarding.txt` | Joining process, day one, first week, probation, buddy program | 16 |
| `expense_policy.txt` | Eligibility, deadlines, required docs, travel/meal limits, payment timeline | 19 |
| `hr_leave_policy.txt` | Annual leave, sick leave, casual leave, carry-forward, probation leave, holidays | 19 |
| `it_security_policy.txt` | Passwords, MFA, device security, data classification, incident reporting, remote work | 19 |
| `product_support_manual.txt` | Support channels, ticket priorities, response targets, escalation, knowledge base | 16 |

---

## 6. Configuration & Environment

- `.env.example` documents 3 variables: `OPENAI_API_KEY`, `OPENAI_MODEL` (default `gpt-4o-mini`), `EMBEDDING_MODEL_NAME` (default `sentence-transformers/all-MiniLM-L6-v2`)
- `.env` is gitignored
- `chroma_db/` is gitignored (regenerated by `ingest.py`)
- `.streamlit/config.toml` at project root disables file watching (`fileWatcherType = "none"`) to avoid issues with ChromaDB

---

## 7. Usage Flow

```bash
# 1. Setup
python -m venv .venv
source .venv/bin/activate      # macOS/Linux
# .venv\Scripts\activate       # Windows
pip install -r requirements.txt
cp .env.example .env           # (optional) add OPENAI_API_KEY

# 2. Ingest documents
python ingest.py

# 3. Launch app
streamlit run app.py
```

Alternatively, clicking "Update index" (incremental) or "Rebuild from scratch" (full reset) from the app sidebar performs ingestion without leaving the UI.

---

## 8. Key Metrics

- **Embedding dimension:** 384
- **Chunk size:** 900 characters
- **Chunk overlap:** 180 characters (20%)
- **Default top-k:** 5 (user-configurable 2–8)
- **LLM temperature:** 0.2
- **Number of indexed chunks (approx):** 10–15 (depends on document lengths)

---

## 9. Strengths

- **Clean separation of concerns:** Each pipeline stage is a dedicated module with a single responsibility.
- **Graceful degradation:** Full LLM mode when key is present; informative fallback when absent.
- **Auditability:** Raw chunks are exposed in the UI with distance scores and source filenames.
- **Extensible format support:** Adding a new document format requires adding one reader function.
- **Minimal dependencies:** No Docker, no cloud services required for the retrieval pipeline.

---

## 11. Testing

46 pytest tests across 5 modules, all passing:

```
tests/test_config.py ..............  6 passed
tests/test_document_loader.py .....  8 passed
tests/test_rag_chain.py ...........  8 passed
tests/test_text_splitter.py ....... 16 passed
tests/test_vector_store.py ........ 10 passed
──────────────────────────────────────
Total: 46 passed in 3.71s
```

Run tests with:
```bash
source .venv/bin/activate
python -m pytest tests/ -v
```

### Test Coverage by Module

| Test file | Tests | What it covers |
|---|---|---|
| `tests/test_config.py` | 6 | Path correctness, constants |
| `tests/test_document_loader.py` | 8 | Loading txt/md, unsupported types, empty dir, error handling |
| `tests/test_rag_chain.py` | 8 | Context building, fallback mode, source dedup, truncation |
| `tests/test_text_splitter.py` | 16 | `clean_text`, chunk size/overlap, sentence boundaries, empty docs, chunk IDs |
| `tests/test_vector_store.py` | 10 | Embedding, incremental indexing, stale cleanup, force rebuild, query results |

External dependencies (ChromaDB, SentenceTransformer) are mocked in `test_vector_store.py` to keep tests fast and isolated.

---

## 12. Limitations

- **Simple source-based incremental indexing:** Only skips documents by source filename; does not detect content changes within a file.
- **Character-based chunking:** No awareness of document structure (headings, sections, lists).
- **Single-user Streamlit:** No session management, authentication, or persistence.
- **No query rewriting:** Questions are used as-is without expansion or decomposition.
- **No reranking:** Retrieved chunks are used in order of similarity without a secondary ranking pass.
- **OpenAI-only LLM:** The generation backend is tied to the OpenAI SDK; switching requires code changes.
