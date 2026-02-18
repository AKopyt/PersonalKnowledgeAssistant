from src.document_processing.chunk_formatter import format_chunk


class TestFormatChunk:
    def test_format_chunk_normal(self):
        # Act
        result = format_chunk("report.pdf", 1, 5, "Some text content")

        # Assert
        assert result == "[File: report.pdf, Chunk: 1/5]\n\nSome text content"

    def test_format_chunk_empty_text(self):
        # Act
        result = format_chunk("report.pdf", 1, 1, "")

        # Assert
        assert result == "[File: report.pdf, Chunk: 1/1]\n\n"

    def test_format_chunk_special_characters_in_filename(self):
        # Act
        result = format_chunk("my file (1).pdf", 2, 3, "text")

        # Assert
        assert result == "[File: my file (1).pdf, Chunk: 2/3]\n\ntext"

    def test_format_chunk_special_characters_in_text(self):
        # Arrange
        text = 'He said "hello" & <goodbye>'

        # Act
        result = format_chunk("doc.txt", 1, 1, text)

        # Assert
        assert result == '[File: doc.txt, Chunk: 1/1]\n\nHe said "hello" & <goodbye>'

    def test_format_chunk_large_index(self):
        # Act
        result = format_chunk("big.pdf", 999, 1000, "last chunk")

        # Assert
        assert result == "[File: big.pdf, Chunk: 999/1000]\n\nlast chunk"

    def test_format_chunk_single_chunk(self):
        # Act
        result = format_chunk("single.txt", 1, 1, "only one")

        # Assert
        assert result == "[File: single.txt, Chunk: 1/1]\n\nonly one"
