from src.document_processing.chunking.fixed_size import FixedSizeChunking


class TestFixedSizeChunking:
    def test_empty_text_returns_empty_list(self):
        # Arrange
        chunker = FixedSizeChunking(chunk_size=100)

        # Act
        result = chunker.chunk("", {"file_name": "test.txt"})

        # Assert
        assert result == []

    def test_text_shorter_than_chunk_size_returns_single_chunk(self, sample_short_text, sample_metadata):
        # Arrange
        chunker = FixedSizeChunking(chunk_size=1000)

        # Act
        result = chunker.chunk(sample_short_text, sample_metadata)

        # Assert
        assert len(result) == 1
        assert result[0]["text"] == sample_short_text

    def test_text_exact_multiple_of_chunk_size_splits_evenly(self):
        # Arrange
        chunk_size = 1000
        text = "A" * (chunk_size * 2)
        chunker = FixedSizeChunking(chunk_size=chunk_size)

        # Act
        result = chunker.chunk(text, {"file_name": "test.txt"})

        # Assert
        assert len(result) == 2
        assert all(len(c["text"]) == chunk_size for c in result)

    def test_text_with_remainder_produces_shorter_last_chunk(self, sample_long_text):
        # Arrange — sample_long_text is 2500 chars, chunk_size=1000 -> 3 chunks (1000, 1000, 500)
        chunk_size = 1000
        chunker = FixedSizeChunking(chunk_size=chunk_size)

        # Act
        result = chunker.chunk(sample_long_text, {"file_name": "test.txt"})

        # Assert
        assert len(result) == 3
        assert len(result[-1]["text"]) == 500

    def test_metadata_preserved_on_all_chunks(self, sample_metadata):
        # Arrange
        chunker = FixedSizeChunking(chunk_size=1000)

        # Act
        result = chunker.chunk("A" * 2500, sample_metadata)

        # Assert
        for chunk in result:
            assert chunk["metadata"] == sample_metadata

    def test_default_chunk_size_is_1000(self):
        # Act
        chunker = FixedSizeChunking()

        # Assert
        assert chunker.chunk_size == 1000

    def test_custom_chunk_size_is_stored(self):
        # Act
        chunker = FixedSizeChunking(chunk_size=500)

        # Assert
        assert chunker.chunk_size == 500

    def test_chunk_result_has_text_and_metadata_keys(self, sample_short_text, sample_metadata):
        # Arrange
        chunker = FixedSizeChunking(chunk_size=1000)

        # Act
        result = chunker.chunk(sample_short_text, sample_metadata)

        # Assert
        assert set(result[0].keys()) == {"text", "metadata"}

    def test_joined_chunks_equal_original_text(self, sample_long_text):
        # Arrange
        chunker = FixedSizeChunking(chunk_size=1000)

        # Act
        result = chunker.chunk(sample_long_text, {"file_name": "test.txt"})

        # Assert
        reconstructed = "".join(c["text"] for c in result)
        assert reconstructed == sample_long_text
