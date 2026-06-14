from pathlib import Path
from src.config import PROJECT_ROOT, DATA_DIR, DB_DIR, COLLECTION_NAME


class TestConfig:
    def test_project_root_is_absolute(self):
        assert isinstance(PROJECT_ROOT, Path)
        assert PROJECT_ROOT.is_absolute()

    def test_data_dir_is_absolute(self):
        assert isinstance(DATA_DIR, Path)
        assert DATA_DIR.is_absolute()

    def test_db_dir_is_absolute(self):
        assert isinstance(DB_DIR, Path)
        assert DB_DIR.is_absolute()

    def test_collection_name_is_string(self):
        assert isinstance(COLLECTION_NAME, str)
        assert len(COLLECTION_NAME) > 0

    def test_data_dir_points_to_data_folder(self):
        assert DATA_DIR.name == "data"

    def test_db_dir_points_to_chroma_db(self):
        assert DB_DIR.name == "chroma_db"
