from typing import List, Dict, Any
import shutil

import chromadb
from sentence_transformers import SentenceTransformer

from src.config import DB_DIR, COLLECTION_NAME, EMBEDDING_MODEL_NAME
from src.text_splitter import TextChunk


_embedding_model = None


def get_embedding_model() -> SentenceTransformer:
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    return _embedding_model


def embed_texts(texts: List[str]) -> List[List[float]]:
    model = get_embedding_model()
    embeddings = model.encode(texts, normalize_embeddings=True, show_progress_bar=True)
    return embeddings.tolist()


def get_chroma_client() -> chromadb.PersistentClient:
    DB_DIR.mkdir(parents=True, exist_ok=True)
    return chromadb.PersistentClient(path=str(DB_DIR))


def reset_vector_database() -> None:
    if DB_DIR.exists():
        shutil.rmtree(DB_DIR)


def build_vector_store(chunks: List[TextChunk], force_rebuild: bool = False) -> int:
    if force_rebuild:
        reset_vector_database()

    client = get_chroma_client()
    collection = client.get_or_create_collection(name=COLLECTION_NAME)

    existing = collection.get(include=["metadatas"])
    indexed_sources: set[str] = set()
    if existing and existing.get("metadatas"):
        indexed_sources = {m["source"] for m in existing["metadatas"] if m.get("source")}

    current_sources = {c.source for c in chunks}

    stale_sources = indexed_sources - current_sources
    for source in stale_sources:
        collection.delete(where={"source": source})

    if force_rebuild:
        new_chunks = chunks
    else:
        new_chunks = [c for c in chunks if c.source not in indexed_sources]

    if not new_chunks:
        return len(chunks)

    texts = [chunk.text for chunk in new_chunks]
    embeddings = embed_texts(texts)
    ids = [chunk.id for chunk in new_chunks]
    metadatas = [
        {
            "source": chunk.source,
            "chunk_index": chunk.chunk_index,
        }
        for chunk in new_chunks
    ]

    collection.add(
        ids=ids,
        documents=texts,
        embeddings=embeddings,
        metadatas=metadatas,
    )
    return len(chunks)


def get_collection():
    client = get_chroma_client()
    return client.get_or_create_collection(name=COLLECTION_NAME)


def query_vector_store(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    collection = get_collection()
    if collection.count() == 0:
        return []

    query_embedding = embed_texts([query])[0]
    result = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    retrieved = []
    documents = result.get("documents", [[]])[0]
    metadatas = result.get("metadatas", [[]])[0]
    distances = result.get("distances", [[]])[0]

    for doc, metadata, distance in zip(documents, metadatas, distances):
        retrieved.append(
            {
                "text": doc,
                "source": metadata.get("source", "unknown"),
                "chunk_index": metadata.get("chunk_index", -1),
                "distance": distance,
            }
        )

    return retrieved
