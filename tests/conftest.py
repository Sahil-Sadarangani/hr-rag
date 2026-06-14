from pathlib import Path
import pytest

TEST_DATA_DIR = Path(__file__).resolve().parent / "test_data"


@pytest.fixture
def sample_txt() -> Path:
    return TEST_DATA_DIR / "sample.txt"


@pytest.fixture
def sample_md() -> Path:
    return TEST_DATA_DIR / "sample.md"


@pytest.fixture
def unsupported_file() -> Path:
    return TEST_DATA_DIR / "unsupported.xyz"


@pytest.fixture
def test_data_dir() -> Path:
    return TEST_DATA_DIR


@pytest.fixture
def empty_dir(tmp_path: Path) -> Path:
    d = tmp_path / "empty"
    d.mkdir()
    return d
