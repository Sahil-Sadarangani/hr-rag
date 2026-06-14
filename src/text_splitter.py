from dataclasses import dataclass
from typing import List
import re

from src.document_loader import LoadedDocument


@dataclass
class TextChunk:
    id: str
    source: str
    chunk_index: int
    text: str


def clean_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def split_text(text: str, chunk_size: int = 900, chunk_overlap: int = 180) -> List[str]:
    """
    Character-based chunking. It is simple, fast, and works well for policy documents.
    chunk_overlap keeps context continuity between neighboring chunks.
    """
    text = clean_text(text)
    if not text:
        return []
    if len(text) <= chunk_size:
        return [text]

    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]

        # Try to avoid cutting a sentence in the middle.
        if end < len(text):
            last_period = max(chunk.rfind("."), chunk.rfind("\n"))
            if last_period > chunk_size * 0.55:
                end = start + last_period + 1
                chunk = text[start:end]

        chunks.append(chunk.strip())
        if end >= len(text):
            break
        start = max(0, end - chunk_overlap)

    return [chunk for chunk in chunks if chunk]


def make_chunks(documents: List[LoadedDocument]) -> List[TextChunk]:
    all_chunks: List[TextChunk] = []
    for doc in documents:
        pieces = split_text(doc.text)
        for index, piece in enumerate(pieces):
            safe_source = doc.source.replace(" ", "_").replace(".", "_")
            chunk_id = f"{safe_source}_chunk_{index}"
            all_chunks.append(
                TextChunk(
                    id=chunk_id,
                    source=doc.source,
                    chunk_index=index,
                    text=piece,
                )
            )
    return all_chunks
