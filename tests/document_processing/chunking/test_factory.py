from unittest.mock import MagicMock

import pytest

from src.document_processing.chunking.factory import (
    ChunkingStrategyFactory,
    create_default_chunking_factory,
)
from src.document_processing.chunking.fixed_size import FixedSizeChunking
from src.enums.chunking_types import ChunkingType


class TestChunkingStrategyFactory:
    def test_create_registered_type_returns_instance(self):
        # Arrange
        factory = ChunkingStrategyFactory()
        mock_creator = MagicMock(return_value="chunker_instance")
        factory.register("test_type", mock_creator)

        # Act
        result = factory.create("test_type")

        # Assert
        assert result == "chunker_instance"

    def test_create_unregistered_type_raises_value_error(self):
        # Arrange
        factory = ChunkingStrategyFactory()

        # Act & Assert
        with pytest.raises(ValueError, match="Unsupported chunking type: unknown"):
            factory.create("unknown")

    def test_kwargs_forwarded_to_creator(self):
        # Arrange
        factory = ChunkingStrategyFactory()
        mock_creator = MagicMock()
        factory.register("my_type", mock_creator)

        # Act
        factory.create("my_type", chunk_size=500, overlap=100)

        # Assert
        mock_creator.assert_called_once_with(chunk_size=500, overlap=100)

    def test_register_overwrites_previous_creator(self):
        # Arrange
        factory = ChunkingStrategyFactory()
        factory.register("dup", MagicMock(return_value="first"))
        factory.register("dup", MagicMock(return_value="second"))

        # Act
        result = factory.create("dup")

        # Assert
        assert result == "second"


class TestCreateDefaultChunkingFactory:
    def test_creates_fixed_size_chunker(self):
        # Arrange
        factory = create_default_chunking_factory()

        # Act
        chunker = factory.create(ChunkingType.FIXED_SIZE.value)

        # Assert
        assert isinstance(chunker, FixedSizeChunking)

    def test_passes_chunk_size_to_fixed_size(self):
        # Arrange
        factory = create_default_chunking_factory()

        # Act
        chunker = factory.create(ChunkingType.FIXED_SIZE.value, chunk_size=500)

        # Assert
        assert chunker.chunk_size == 500

    def test_unregistered_type_raises(self):
        # Arrange
        factory = create_default_chunking_factory()

        # Act & Assert
        with pytest.raises(ValueError, match="Unsupported chunking type"):
            factory.create("nonexistent")
