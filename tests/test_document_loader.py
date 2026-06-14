import pytest
from pathlib import Path
from src.document_loader import (
    load_single_document,
    load_documents,
    LoadedDocument,
    SUPPORTED_EXTENSIONS,
)


class TestLoadSingleDocument:
    def test_loads_txt_file(self, sample_txt: Path):
        doc = load_single_document(sample_txt)
        assert isinstance(doc, LoadedDocument)
        assert doc.source == "sample.txt"
        assert "sample document" in doc.text

    def test_loads_md_file(self, sample_md: Path):
        doc = load_single_document(sample_md)
        assert isinstance(doc, LoadedDocument)
        assert doc.source == "sample.md"
        assert "Sample Markdown" in doc.text

    def test_unsupported_extension_raises(self, unsupported_file: Path):
        with pytest.raises(ValueError, match="Unsupported file type"):
            load_single_document(unsupported_file)


class TestLoadDocuments:
    def test_loads_all_supported_files(self, test_data_dir: Path):
        docs = load_documents(test_data_dir)
        sources = {d.source for d in docs}
        assert "sample.txt" in sources
        assert "sample.md" in sources
        assert "unsupported.xyz" not in sources

    def test_returns_loaded_document_instances(self, test_data_dir: Path):
        docs = load_documents(test_data_dir)
        for doc in docs:
            assert isinstance(doc, LoadedDocument)
            assert doc.source
            assert doc.text

    def test_raises_on_nonexistent_directory(self):
        with pytest.raises(FileNotFoundError, match="Data directory not found"):
            load_documents(Path("/nonexistent/path"))

    def test_raises_on_empty_directory(self, empty_dir: Path):
        with pytest.raises(FileNotFoundError, match="No supported documents found"):
            load_documents(empty_dir)


class TestSupportedExtensions:
    def test_includes_common_formats(self):
        assert ".txt" in SUPPORTED_EXTENSIONS
        assert ".md" in SUPPORTED_EXTENSIONS
        assert ".pdf" in SUPPORTED_EXTENSIONS
        assert ".docx" in SUPPORTED_EXTENSIONS
