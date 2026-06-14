from src.text_splitter import clean_text, split_text, make_chunks
from src.document_loader import LoadedDocument


class TestCleanText:
    def test_replaces_carriage_returns(self):
        assert clean_text("line1\r\nline2") == "line1\nline2"

    def test_collapses_excessive_newlines(self):
        assert clean_text("a\n\n\n\nb") == "a\n\nb"

    def test_collapses_multiple_spaces(self):
        assert clean_text("a   b    c") == "a b c"

    def test_strips_whitespace(self):
        assert clean_text("  hello  ") == "hello"

    def test_handles_empty_string(self):
        assert clean_text("") == ""

    def test_handles_whitespace_only(self):
        assert clean_text("   \n\n  ") == ""


class TestSplitText:
    def test_short_text_returns_single_chunk(self):
        chunks = split_text("Hello world.", chunk_size=900)
        assert len(chunks) == 1
        assert chunks[0] == "Hello world."

    def test_longer_text_splits_into_multiple_chunks(self):
        text = "word " * 500
        chunks = split_text(text, chunk_size=200, chunk_overlap=40)
        assert len(chunks) >= 2

    def test_chunks_respect_size_bound(self):
        text = "a" * 1000
        chunks = split_text(text, chunk_size=300, chunk_overlap=60)
        for chunk in chunks:
            assert len(chunk) <= 300

    def test_overlap_present_in_consecutive_chunks(self):
        text = "Sentence one. Sentence two. Sentence three. Sentence four. Sentence five. " * 10
        chunks = split_text(text, chunk_size=200, chunk_overlap=60)
        if len(chunks) >= 2:
            overlap_region = chunks[0][-60:]
            assert overlap_region in chunks[1]

    def test_empty_text_returns_no_chunks(self):
        chunks = split_text("")
        assert chunks == []

    def test_whitespace_text_returns_no_chunks(self):
        chunks = split_text("   \n\n  ")
        assert chunks == []


class TestMakeChunks:
    def test_creates_correct_number_of_chunks(self):
        long_text = "hello world. " * 200
        doc = LoadedDocument(source="test.txt", text=long_text)
        chunks = make_chunks([doc])
        assert len(chunks) >= 1
        for chunk in chunks:
            assert chunk.source == "test.txt"

    def test_chunk_ids_are_unique(self):
        doc1 = LoadedDocument(source="a.txt", text="hello " * 200)
        doc2 = LoadedDocument(source="b.txt", text="world " * 200)
        chunks = make_chunks([doc1, doc2])
        ids = [c.id for c in chunks]
        assert len(ids) == len(set(ids))

    def test_chunk_index_is_sequential(self):
        doc = LoadedDocument(source="test.txt", text="word " * 500)
        chunks = make_chunks([doc])
        for i, chunk in enumerate(chunks):
            assert chunk.chunk_index == i

    def test_empty_document_skipped(self):
        doc = LoadedDocument(source="empty.txt", text="")
        chunks = make_chunks([doc])
        assert len(chunks) == 0

    def test_whitespace_only_document_skipped(self):
        doc = LoadedDocument(source="whitespace.txt", text="   \n\n  ")
        chunks = make_chunks([doc])
        assert len(chunks) == 0
