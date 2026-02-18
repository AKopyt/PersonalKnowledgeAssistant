from unittest.mock import MagicMock

import pytest
import requests

from src.database.base import VectorStore


@pytest.fixture
def sample_short_text():
    return "Hello, this is a short sample text for testing."


@pytest.fixture
def sample_long_text():
    return "A" * 2500


@pytest.fixture
def sample_metadata():
    return {"file_path": "/data/test.txt", "file_name": "test.txt"}


@pytest.fixture
def sample_embedding():
    return [0.1, 0.2, 0.3, 0.4, 0.5]


@pytest.fixture
def mock_session():
    return MagicMock(spec=requests.Session)


@pytest.fixture
def mock_vector_store():
    return MagicMock(spec=VectorStore)


@pytest.fixture
def mock_loader_registry():
    return MagicMock()


@pytest.fixture
def mock_chunking_factory():
    return MagicMock()
