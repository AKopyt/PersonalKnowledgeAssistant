import os
from unittest.mock import MagicMock, patch

import pytest

from src.document_processor import DocumentProcessor


def _make_processor(mock_vector_store, mock_loader_registry, mock_chunking_factory, **overrides):
    """Helper to build a DocumentProcessor with injected mocks and sensible defaults."""
    defaults = dict(
        data_directory="/data",
        chunking_type="fixed_size",
        embedding_url="http://embed/api",
        vector_store=mock_vector_store,
        loader_registry=mock_loader_registry,
        chunking_factory=mock_chunking_factory,
    )
    defaults.update(overrides)
    return DocumentProcessor(**defaults)


def _configure_pipeline(mock_loader_registry, mock_chunking_factory, chunks):
    """Helper to set up the load -> chunk part of the pipeline."""
    mock_loader_registry.load.return_value = "loaded text"
    mock_chunker = MagicMock()
    mock_chunker.chunk.return_value = chunks
    mock_chunking_factory.create.return_value = mock_chunker


TWO_CHUNKS = [
    {"text": "chunk one", "metadata": {"file_name": "test.txt"}},
    {"text": "chunk two", "metadata": {"file_name": "test.txt"}},
]

THREE_CHUNKS = [
    {"text": "chunk one", "metadata": {}},
    {"text": "chunk two", "metadata": {}},
    {"text": "chunk three", "metadata": {}},
]


class TestDocumentProcessorHappyPath:
    @patch("src.document_processor.get_embedding")
    def test_returns_saved_ids_for_all_chunks(
        self, mock_embed, mock_loader_registry, mock_chunking_factory, mock_vector_store
    ):
        # Arrange
        _configure_pipeline(mock_loader_registry, mock_chunking_factory, TWO_CHUNKS)
        mock_embed.return_value = [0.1, 0.2, 0.3]
        mock_vector_store.save.side_effect = ["id-1", "id-2"]
        processor = _make_processor(mock_vector_store, mock_loader_registry, mock_chunking_factory)

        # Act
        result = processor.process_file("test.txt")

        # Assert
        assert result == ["id-1", "id-2"]


class TestDocumentProcessorCallVerification:
    @patch("src.document_processor.get_embedding")
    def test_loads_file_from_data_directory(
        self, mock_embed, mock_loader_registry, mock_chunking_factory, mock_vector_store
    ):
        # Arrange
        _configure_pipeline(mock_loader_registry, mock_chunking_factory, TWO_CHUNKS)
        mock_embed.return_value = [0.1]
        mock_vector_store.save.return_value = "id"
        processor = _make_processor(mock_vector_store, mock_loader_registry, mock_chunking_factory)

        # Act
        processor.process_file("test.txt")

        # Assert
        expected_path = os.path.join("/data", "test.txt")
        mock_loader_registry.load.assert_called_once_with(expected_path)

    @patch("src.document_processor.get_embedding")
    def test_creates_chunker_with_configured_type_and_size(
        self, mock_embed, mock_loader_registry, mock_chunking_factory, mock_vector_store
    ):
        # Arrange
        _configure_pipeline(mock_loader_registry, mock_chunking_factory, TWO_CHUNKS)
        mock_embed.return_value = [0.1]
        mock_vector_store.save.return_value = "id"
        processor = _make_processor(
            mock_vector_store, mock_loader_registry, mock_chunking_factory, chunk_size=500
        )

        # Act
        processor.process_file("test.txt")

        # Assert
        mock_chunking_factory.create.assert_called_once_with("fixed_size", chunk_size=500)

    @patch("src.document_processor.format_chunk")
    @patch("src.document_processor.get_embedding")
    def test_formats_each_chunk_with_filename_and_position(
        self, mock_embed, mock_format, mock_loader_registry, mock_chunking_factory, mock_vector_store
    ):
        # Arrange
        _configure_pipeline(mock_loader_registry, mock_chunking_factory, TWO_CHUNKS)
        mock_embed.return_value = [0.1]
        mock_format.return_value = "formatted"
        mock_vector_store.save.return_value = "id"
        processor = _make_processor(mock_vector_store, mock_loader_registry, mock_chunking_factory)

        # Act
        processor.process_file("test.txt")

        # Assert
        mock_format.assert_any_call("test.txt", 1, 2, "chunk one")
        mock_format.assert_any_call("test.txt", 2, 2, "chunk two")

    @patch("src.document_processor.get_embedding")
    def test_passes_embedding_url_and_model_to_get_embedding(
        self, mock_embed, mock_loader_registry, mock_chunking_factory, mock_vector_store
    ):
        # Arrange
        _configure_pipeline(mock_loader_registry, mock_chunking_factory, TWO_CHUNKS)
        mock_embed.return_value = [0.1]
        mock_vector_store.save.return_value = "id"
        processor = _make_processor(
            mock_vector_store, mock_loader_registry, mock_chunking_factory,
            embedding_model="custom-model"
        )

        # Act
        processor.process_file("test.txt")

        # Assert
        for c in mock_embed.call_args_list:
            assert c.args[1] == "http://embed/api"
            assert c.args[2] == "custom-model"

    @patch("src.document_processor.get_embedding")
    def test_passes_embedding_vector_to_store(
        self, mock_embed, mock_loader_registry, mock_chunking_factory, mock_vector_store
    ):
        # Arrange
        _configure_pipeline(mock_loader_registry, mock_chunking_factory, TWO_CHUNKS)
        mock_embed.return_value = [0.1, 0.2]
        mock_vector_store.save.return_value = "id"
        processor = _make_processor(mock_vector_store, mock_loader_registry, mock_chunking_factory)

        # Act
        processor.process_file("test.txt")

        # Assert
        for c in mock_vector_store.save.call_args_list:
            assert c.args[1] == [0.1, 0.2]


class TestDocumentProcessorFailureModes:
    @patch("src.document_processor.get_embedding")
    def test_load_failure_returns_empty_list(
        self, mock_embed, mock_loader_registry, mock_chunking_factory, mock_vector_store
    ):
        # Arrange
        mock_loader_registry.load.side_effect = ValueError("Unsupported file type")
        processor = _make_processor(mock_vector_store, mock_loader_registry, mock_chunking_factory)

        # Act
        result = processor.process_file("bad.xyz")

        # Assert
        assert result == []

    @patch("src.document_processor.get_embedding")
    def test_chunking_failure_returns_empty_list(
        self, mock_embed, mock_loader_registry, mock_chunking_factory, mock_vector_store
    ):
        # Arrange
        mock_loader_registry.load.return_value = "text"
        mock_chunking_factory.create.side_effect = ValueError("Unsupported chunking type")
        processor = _make_processor(
            mock_vector_store, mock_loader_registry, mock_chunking_factory,
            chunking_type="bad_type"
        )

        # Act
        result = processor.process_file("test.txt")

        # Assert
        assert result == []

    @patch("src.document_processor.get_embedding")
    def test_embedding_failure_skips_chunk_and_does_not_store(
        self, mock_embed, mock_loader_registry, mock_chunking_factory, mock_vector_store
    ):
        # Arrange
        _configure_pipeline(mock_loader_registry, mock_chunking_factory, TWO_CHUNKS)
        mock_embed.side_effect = Exception("embedding error")
        processor = _make_processor(mock_vector_store, mock_loader_registry, mock_chunking_factory)

        # Act
        result = processor.process_file("test.txt")

        # Assert
        assert result == []
        mock_vector_store.save.assert_not_called()

    @patch("src.document_processor.get_embedding")
    def test_store_returning_none_excludes_chunk_from_results(
        self, mock_embed, mock_loader_registry, mock_chunking_factory, mock_vector_store
    ):
        # Arrange
        _configure_pipeline(mock_loader_registry, mock_chunking_factory, TWO_CHUNKS)
        mock_embed.return_value = [0.1]
        mock_vector_store.save.return_value = None
        processor = _make_processor(mock_vector_store, mock_loader_registry, mock_chunking_factory)

        # Act
        result = processor.process_file("test.txt")

        # Assert
        assert result == []


class TestDocumentProcessorOverrides:
    @patch("src.document_processor.get_embedding")
    def test_per_call_chunk_size_overrides_default(
        self, mock_embed, mock_loader_registry, mock_chunking_factory, mock_vector_store
    ):
        # Arrange
        _configure_pipeline(mock_loader_registry, mock_chunking_factory, TWO_CHUNKS)
        mock_embed.return_value = [0.1]
        mock_vector_store.save.return_value = "id"
        processor = _make_processor(
            mock_vector_store, mock_loader_registry, mock_chunking_factory, chunk_size=1000
        )

        # Act
        processor.process_file("test.txt", chunk_size=250)

        # Assert
        mock_chunking_factory.create.assert_called_once_with("fixed_size", chunk_size=250)

    @patch("src.document_processor.get_embedding")
    def test_per_call_model_overrides_default(
        self, mock_embed, mock_loader_registry, mock_chunking_factory, mock_vector_store
    ):
        # Arrange
        _configure_pipeline(mock_loader_registry, mock_chunking_factory, TWO_CHUNKS)
        mock_embed.return_value = [0.1]
        mock_vector_store.save.return_value = "id"
        processor = _make_processor(
            mock_vector_store, mock_loader_registry, mock_chunking_factory,
            embedding_model="all-minilm"
        )

        # Act
        processor.process_file("test.txt", model="nomic-embed")

        # Assert
        for c in mock_embed.call_args_list:
            assert c.args[2] == "nomic-embed"


class TestDocumentProcessorPartialFailure:
    @patch("src.document_processor.get_embedding")
    def test_skips_failed_embed_and_returns_remaining_ids(
        self, mock_embed, mock_loader_registry, mock_chunking_factory, mock_vector_store
    ):
        # Arrange — chunk 2 fails to embed, chunks 1 and 3 succeed
        _configure_pipeline(mock_loader_registry, mock_chunking_factory, THREE_CHUNKS)
        mock_embed.side_effect = [[0.1], Exception("fail"), [0.3]]
        mock_vector_store.save.side_effect = ["id-1", "id-3"]
        processor = _make_processor(mock_vector_store, mock_loader_registry, mock_chunking_factory)

        # Act
        result = processor.process_file("test.txt")

        # Assert
        assert result == ["id-1", "id-3"]


class TestDocumentProcessorDefaults:
    @patch("src.document_processor.create_default_chunking_factory")
    @patch("src.document_processor.create_default_loader_registry")
    def test_creates_default_registry_and_factory_when_not_injected(
        self, mock_create_registry, mock_create_factory, mock_vector_store
    ):
        # Arrange
        mock_create_registry.return_value = MagicMock()
        mock_create_factory.return_value = MagicMock()

        # Act
        processor = DocumentProcessor(
            data_directory="/data",
            chunking_type="fixed_size",
            embedding_url="http://embed/api",
            vector_store=mock_vector_store,
        )

        # Assert
        mock_create_registry.assert_called_once()
        mock_create_factory.assert_called_once()
        assert processor.loader_registry is mock_create_registry.return_value
        assert processor.chunking_factory is mock_create_factory.return_value
