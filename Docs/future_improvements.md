# Future Improvements


### 1. Semantic Chunking
Replace character-based splitting with recursive document-aware splitting (e.g., LangChain's `RecursiveCharacterTextSplitter`). Split on `\n\n` > `\n` > `.` > space to respect document structure (paragraphs, sections). This preserves semantic boundaries and improves retrieval quality.

### 2. Hybrid Search
Augment semantic search with keyword/BM25 retrieval using a hybrid retriever (e.g., ChromaDB's `multi` retrieval mode or a separate `rank_bm25` index). This captures exact term matches that dense embeddings may miss (e.g., policy IDs, specific numbers).

### 3. LLM-Agnostic Client
Replace the direct OpenAI SDK call with a generic HTTP client (e.g., `openai` SDK pointed at different base URLs, or `litellm`). This would allow swapping to Ollama (local LLMs), Anthropic, Azure OpenAI, vLLM, or any OpenAI-compatible endpoint via a config change.

### 4. Better `.env` Validation
Add startup validation in `config.py` that warns if key variables are missing or invalid, rather than silently falling back.

### 5. Streaming Output
Stream the LLM response token-by-token in the UI using `st.write_stream()` for a more responsive user experience.


### 6. Content-Aware Incremental Indexing
Basic incremental indexing (skip by source filename) is already implemented. Extend it to detect content changes: store a file hash or modification timestamp per source, and re-index only when content actually changes. This handles edits to existing documents that currently require a full "Rebuild from scratch".

### 7. Reranking
Add a cross-encoder reranker (e.g., `cross-encoder/ms-marco-MiniLM-L-6-v2`) as a second pass over retrieved chunks. This significantly improves the relevance of the top-k results before they reach the LLM.

### 8. Query Rewriting & Expansion
Before retrieval, rewrite the user query:
- Expand acronyms
- Add synonyms
- Decompose compound questions
- Use an LLM call to generate 3 related queries and retrieve for all of them (HyDE or query expansion)

### 9. Document-Level Metadata
Store richer metadata per document: page count, last modified date, author, document category (HR, IT, Finance). Allow filtering retrieval by category from the UI.

### 10. Conversation History
Add chat memory so users can ask follow-up questions. Store previous Q&A in `st.session_state` and optionally include recent conversation history in the LLM context.

### 11. Confidence Scores & Citation Highlighting
Display a confidence score for the answer (based on retrieval distances or LLM logprobs). Highlight which sentences in the answer came from which source document.


### 12. Multi-User Support & Authentication
Replace Streamlit's single-session model with a web framework (FastAPI + React) that supports authentication, user sessions, and per-user document access controls.

### 13. Document Management UI
Build a document management interface: upload files through the browser, view/edit/delete documents, preview chunks, and monitor index status without needing filesystem access.

### 14. Evaluation Pipeline
Add an evaluation harness:
- Curate a test set of question-answer pairs from the corpus
- Measure retrieval recall@k, MRR, NDCG
- Measure generation faithfulness using LLM-as-judge or BERTScore
- Track metrics over time as indexing strategies change

### 15. Monitoring & Logging
Add request logging (question, retrieved chunks, response, latency), integrate with tools like LangFuse or LangSmith for observability, and set up basic alerting for failures.

### 16. Support for More Document Types
Add readers for:
- HTML pages
- Markdown with frontmatter (for technical docs)
- Images with embedded text (via OCR — Tesseract or GPT-4o vision)
- Spreadsheets (CSV/XLSX — rows as mini-documents)

### 17. Self-Hosted LLM Integration
Add support for local LLMs via Ollama or llama.cpp. This eliminates the API key requirement entirely and keeps all data on-premises. The `rag_chain.py` abstraction would need to support multiple backends.

### 18. Asynchronous Ingestion Pipeline
For larger corpora, make ingestion async: process documents in parallel, batch embeddings, stream progress to the UI via WebSocket or server-sent events.

### 19. Advanced Retrieval Strategies
Implement:
- **MMR (Maximum Marginal Relevance):** Diversity-aware retrieval to avoid redundant chunks
- **Contextual retrieval:** Prepend chunk with a summary of its surrounding document section
- **Multi-vector retrieval:** Store both a summary embedding and the full chunk text for finer-grained search

### 20. Production Deployment
Containerize with Docker, add CI/CD (GitHub Actions for lint + test + build), deploy behind a reverse proxy with rate limiting, and add a persistent PostgreSQL/SQLite metadata store alongside ChromaDB.
