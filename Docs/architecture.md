# Architecture & Design Decisions

## System Overview

This project is a **Retrieval-Augmented Generation (RAG)** system that lets users ask natural language questions over a corpus of internal company documents and receive grounded, source-cited answers.

```
┌─────────────────────────────────────────────────────────┐
│                    INGESTION PIPELINE                     │
│                                                         │
│  data/*.{txt,md,pdf,docx}                               │
│         │                                                │
│         ▼                                                │
│  document_loader.py  ──► LoadedDocument (source, text)   │
│         │                                                │
│         ▼                                                │
│  text_splitter.py    ──► TextChunk (id, source, text)   │
│         │               chunk_size=900, overlap=180      │
│         ▼                                                │
│  vector_store.py     ──► ChromaDB collection             │
│         │               SentenceTransformer embeddings   │
│         │               all-MiniLM-L6-v2                 │
│         ▼                                                │
│  chroma_db/ (persistent on disk)                         │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                    QUERY PIPELINE                         │
│                                                         │
│  User question (Streamlit UI)                            │
│         │                                                │
│         ▼                                                │
│  vector_store.query_vector_store()                       │
│  ─► embed question ─► ChromaDB similarity search        │
│     ─► top-k chunks (with metadata + distances)         │
│         │                                                │
│         ▼                                                │
│  rag_chain.generate_answer()                             │
│     ├─ Has OPENAI_API_KEY? ─► OpenAI chat completion     │
│     │   (SYSTEM_PROMPT + context + question)             │
│     └─ No key? ─► fallback_extractive_answer()           │
│         │                                                │
│         ▼                                                │
│  Streamlit UI displays:                                  │
│     • Generated answer                                   │
│     • Source document names                              │
│     • Expandable retrieved chunks                        │
└─────────────────────────────────────────────────────────┘
```

## File-by-File Architecture

### `src/config.py` — Central Configuration
Reads environment variables via `python-dotenv` and exposes paths (`DATA_DIR`, `DB_DIR`), the embedding model name, and OpenAI settings. All magic strings are centralized here.

### `src/document_loader.py` — Document Ingestion
Defines a `LoadedDocument` dataclass (`source` filename + `text` content). Supports `.txt`, `.md`, `.pdf` (via `pypdf`), and `.docx` (via `python-docx`). PDFs include page-number markers. Only non-empty documents are returned.

**Design choice:** A simple dataclass over a class hierarchy keeps the code minimal while remaining extensible.

### `src/text_splitter.py` — Chunking Strategy
Splits cleaned text into chunks of **900 characters with 180-character overlap** (20% overlap). Chunk boundaries try to break at sentence ends (period or newline) when possible. Produces `TextChunk` objects with a unique ID, source filename, chunk index, and text.

**Design choice:** Character-based chunking with sentence-boundary awareness was chosen over token-based splitting because it is dependency-free, fast, and predictable for the policy-document genre. The 20% overlap prevents context loss at boundaries.

### `src/vector_store.py` — Embedding & Vector Database
- Uses **SentenceTransformer** (`all-MiniLM-L6-v2`) to create 384-dimensional normalized embeddings locally.
- Uses **ChromaDB** as a persistent vector store on disk.
- `build_vector_store(force_rebuild=False)` checks existing index and only embeds new documents (incremental). Pass `force_rebuild=True` for a full reset + re-embed.
- `query_vector_store()` embeds the question, retrieves top-k results with documents, metadata, and distances.

**Design choices:**
- **all-MiniLM-L6-v2:** Lightweight (~80 MB), fast inference, good semantic quality, runs entirely offline with no API cost.
- **ChromaDB:** Local, file-based, zero-infrastructure vector DB. Ideal for small-to-medium corpora and interview/demo contexts.
- **Incremental by default:** Skips re-embedding already-indexed documents. Removes chunks for deleted documents. Full rebuild available via `force_rebuild=True`.

### `src/rag_chain.py` — Answer Generation
Two modes:
1. **LLM mode** (with `OPENAI_API_KEY`): Builds a context string from retrieved chunks, sends it with a strict system prompt to OpenAI chat completion (`temperature=0.2` for deterministic answers). The prompt explicitly forbids inventing information.
2. **Fallback mode** (no key): Returns the top retrieved chunk verbatim with an explanatory message.

`unique_sources()` deduplicates source filenames for display.

**Design choice:** The fallback mode ensures the retrieval pipeline is demonstrable even without API credentials. The low temperature (0.2) prioritizes factual consistency over creativity.

### `app.py` — Streamlit UI
Single-page Streamlit app:
- Sidebar shows indexed chunk count, an "Update index" button (incremental), and a "Rebuild from scratch" button (full reset).
- Main area: question input, slider for top-k (2–8), "Generate answer" button.
- Results: answer text, source document list, expandable raw chunks with metadata.

**Design choice:** Streamlit was chosen over Flask/FastAPI because it is faster to prototype and requires zero front-end code. The slider lets users control retrieval breadth interactively.

### `ingest.py` — CLI Ingestion Script
Standalone script that runs the full ingestion pipeline (load → chunk → embed → store). Separated from `app.py` so indexing can happen before the UI starts.

## Data Flow (End-to-End)

1. **User runs `python ingest.py`** (or clicks "Update index" / "Rebuild from scratch" in the UI).
2. All documents in `data/` are loaded as `LoadedDocument` objects.
3. Each document is split into overlapping `TextChunk` objects.
4. Chunks are embedded and stored in the ChromaDB collection.
5. **User asks a question** in the Streamlit text input.
6. The question is embedded with the same SentenceTransformer model.
7. ChromaDB performs cosine similarity search and returns top-k chunks.
8. Retrieved chunks are injected into a prompt sent to OpenAI (or shown directly in fallback mode).
9. The answer and source documents are rendered in the UI.

## Why These Specific Choices?

| Decision | Choice | Rationale |
|---|---|---|
| **Language** | Python | Dominant ecosystem for NLP/ML. All major libraries (SentenceTransformers, ChromaDB, OpenAI SDK) are Python-native. |
| **UI Framework** | Streamlit | Zero front-end code, hot-reloading, single-command launch. Ideal for demos and interviews. |
| **Embedding Model** | `all-MiniLM-L6-v2` | 80 MB model, runs on CPU, 384-dim embeddings, no API dependency, good semantic retrieval quality. |
| **Vector Database** | ChromaDB | File-based persistence, simple API, no Docker/server required. Perfect for local/small-scale RAG. |
| **Chunk Size** | 900 chars | Fits comfortably within LLM context windows while carrying enough signal per chunk. |
| **Chunk Overlap** | 180 chars (20%) | Balances context continuity against storage/retrieval efficiency. |
| **LLM API** | OpenAI-compatible | Industry standard; the abstraction allows swapping to any OpenAI-compatible endpoint (e.g., Ollama, vLLM, Azure). |
| **Temperature** | 0.2 | Low randomness ensures answers stick closely to retrieved context. |
| **Fallback Mode** | Yes | Allows full pipeline demonstration without API keys. Shows the retrieval quality even without generation. |

## Security & Environment Management

- API keys and model names are managed via `.env` (gitignored). `.env.example` documents the required variables.
- `chroma_db/` is gitignored; the index is regenerated from source documents.
- The system prompt explicitly constrains the LLM to prevent hallucination.
