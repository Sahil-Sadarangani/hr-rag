from unittest.mock import patch, MagicMock
import pytest
from src.vector_store import embed_texts, build_vector_store, query_vector_store
from src.text_splitter import TextChunk


class FakeModel:
    def encode(self, texts, **kwargs):
        import numpy as np
        return np.array([[0.1] * 384 for _ in texts])


@pytest.fixture
def sample_chunks():
    return [
        TextChunk(id="doc1_chunk_0", source="doc1.txt", chunk_index=0, text="content A"),
        TextChunk(id="doc1_chunk_1", source="doc1.txt", chunk_index=1, text="content B"),
        TextChunk(id="doc2_chunk_0", source="doc2.txt", chunk_index=0, text="content C"),
    ]


class TestEmbedTexts:
    @patch("src.vector_store.get_embedding_model")
    def test_returns_list_of_lists(self, mock_get_model):
        mock_get_model.return_value = FakeModel()
        result = embed_texts(["hello", "world"])
        assert isinstance(result, list)
        assert len(result) == 2
        assert isinstance(result[0], list)
        assert len(result[0]) == 384


class TestBuildVectorStore:
    @patch("src.vector_store.reset_vector_database")
    @patch("src.vector_store.get_chroma_client")
    @patch("src.vector_store.embed_texts")
    def test_force_rebuild_resets_db(self, mock_embed, mock_client, mock_reset, sample_chunks):
        mock_embed.return_value = [[0.1] * 384 for _ in sample_chunks]
        fake_collection = MagicMock()
        fake_collection.get.return_value = {"metadatas": [], "ids": []}
        fake_client = MagicMock()
        fake_client.get_or_create_collection.return_value = fake_collection
        mock_client.return_value = fake_client

        build_vector_store(sample_chunks, force_rebuild=True)
        mock_reset.assert_called_once()

    @patch("src.vector_store.reset_vector_database")
    @patch("src.vector_store.get_chroma_client")
    @patch("src.vector_store.embed_texts")
    def test_incremental_skips_existing_sources(self, mock_embed, mock_client, mock_reset, sample_chunks):
        mock_embed.return_value = [[0.1] * 384]
        fake_collection = MagicMock()
        fake_collection.get.return_value = {
            "metadatas": [{"source": "doc1.txt", "chunk_index": 0}],
            "ids": ["doc1_chunk_0"],
        }
        fake_client = MagicMock()
        fake_client.get_or_create_collection.return_value = fake_collection
        mock_client.return_value = fake_client

        build_vector_store(sample_chunks, force_rebuild=False)

        added_ids = fake_collection.add.call_args[1]["ids"]
        assert all("doc2" in i for i in added_ids)
        assert not fake_collection.delete.called

    @patch("src.vector_store.reset_vector_database")
    @patch("src.vector_store.get_chroma_client")
    @patch("src.vector_store.embed_texts")
    def test_all_chunks_already_indexed(self, mock_embed, mock_client, mock_reset, sample_chunks):
        fake_collection = MagicMock()
        fake_collection.get.return_value = {
            "metadatas": [
                {"source": "doc1.txt", "chunk_index": 0},
                {"source": "doc1.txt", "chunk_index": 1},
                {"source": "doc2.txt", "chunk_index": 0},
            ],
            "ids": ["doc1_chunk_0", "doc1_chunk_1", "doc2_chunk_0"],
        }
        fake_client = MagicMock()
        fake_client.get_or_create_collection.return_value = fake_collection
        mock_client.return_value = fake_client

        result = build_vector_store(sample_chunks, force_rebuild=False)
        assert result == len(sample_chunks)
        fake_collection.add.assert_not_called()

    @patch("src.vector_store.get_chroma_client")
    @patch("src.vector_store.embed_texts")
    def test_stale_sources_removed(self, mock_embed, mock_client, sample_chunks):
        mock_embed.return_value = [[0.1] * 384]
        fake_collection = MagicMock()
        fake_collection.get.return_value = {
            "metadatas": [
                {"source": "doc1.txt", "chunk_index": 0},
                {"source": "stale.txt", "chunk_index": 0},
            ],
            "ids": ["doc1_chunk_0", "stale_chunk_0"],
        }
        fake_client = MagicMock()
        fake_client.get_or_create_collection.return_value = fake_collection
        mock_client.return_value = fake_client

        build_vector_store(sample_chunks, force_rebuild=False)
        fake_collection.delete.assert_called_with(where={"source": "stale.txt"})


class TestQueryVectorStore:
    @patch("src.vector_store.get_chroma_client")
    @patch("src.vector_store.embed_texts")
    def test_returns_empty_list_when_no_chunks(self, mock_embed, mock_client):
        fake_collection = MagicMock()
        fake_collection.count.return_value = 0
        fake_client = MagicMock()
        fake_client.get_or_create_collection.return_value = fake_collection
        mock_client.return_value = fake_client

        result = query_vector_store("test query")
        assert result == []

    @patch("src.vector_store.get_chroma_client")
    @patch("src.vector_store.embed_texts")
    def test_returns_structured_results(self, mock_embed, mock_client):
        mock_embed.return_value = [[0.1] * 384]
        fake_collection = MagicMock()
        fake_collection.count.return_value = 5
        fake_collection.query.return_value = {
            "documents": [["chunk text"]],
            "metadatas": [[{"source": "doc.txt", "chunk_index": 0}]],
            "distances": [[0.25]],
            "ids": [["id1"]],
        }
        fake_client = MagicMock()
        fake_client.get_or_create_collection.return_value = fake_collection
        mock_client.return_value = fake_client

        result = query_vector_store("test query")
        assert len(result) == 1
        assert result[0]["text"] == "chunk text"
        assert result[0]["source"] == "doc.txt"
        assert result[0]["chunk_index"] == 0
        assert result[0]["distance"] == 0.25
