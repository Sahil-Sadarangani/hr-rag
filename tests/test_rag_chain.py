from src.rag_chain import build_context, fallback_extractive_answer, unique_sources


def _make_chunk(text: str, source: str = "test.txt", chunk_index: int = 0, distance: float = 0.5):
    return {"text": text, "source": source, "chunk_index": chunk_index, "distance": distance}


class TestBuildContext:
    def test_returns_formatted_string(self):
        chunks = [
            _make_chunk("content A", "doc1.txt", 0),
            _make_chunk("content B", "doc2.txt", 1),
        ]
        result = build_context(chunks)
        assert "Source 1: doc1.txt, chunk 0" in result
        assert "content A" in result
        assert "Source 2: doc2.txt, chunk 1" in result
        assert "content B" in result

    def test_single_chunk(self):
        chunks = [_make_chunk("only content", "single.txt")]
        result = build_context(chunks)
        assert "Source 1: single.txt, chunk 0" in result
        assert "only content" in result


class TestFallbackExtractiveAnswer:
    def test_returns_top_chunk_snippet(self):
        chunks = [_make_chunk("relevant content here", "source.txt")]
        result = fallback_extractive_answer("some question", chunks)
        assert "relevant content here" in result
        assert "No LLM API key" in result
        assert "source.txt" in result

    def test_no_chunks_returns_not_found(self):
        result = fallback_extractive_answer("question", [])
        assert "could not find" in result.lower()

    def test_truncates_long_snippets(self):
        long_text = "word " * 2000
        chunks = [_make_chunk(long_text)]
        result = fallback_extractive_answer("q", chunks)
        assert len(result) < len(long_text) + 200


class TestUniqueSources:
    def test_deduplicates_sources(self):
        chunks = [
            _make_chunk("a", "doc1.txt"),
            _make_chunk("b", "doc2.txt"),
            _make_chunk("c", "doc1.txt"),
        ]
        assert unique_sources(chunks) == ["doc1.txt", "doc2.txt"]

    def test_single_source(self):
        chunks = [_make_chunk("a", "doc.txt"), _make_chunk("b", "doc.txt")]
        assert unique_sources(chunks) == ["doc.txt"]

    def test_empty_list(self):
        assert unique_sources([]) == []
