from unittest.mock import MagicMock, patch

import pytest

from src.document_processing.loaders import load_pdf, load_txt, load_doc


class TestLoadTxt:
    def test_reads_file_content(self, tmp_path):
        # Arrange
        f = tmp_path / "test.txt"
        f.write_text("Hello world", encoding="utf-8")

        # Act
        result = load_txt(str(f))

        # Assert
        assert result == "Hello world"

    def test_empty_file_returns_empty_string(self, tmp_path):
        # Arrange
        f = tmp_path / "empty.txt"
        f.write_text("", encoding="utf-8")

        # Act
        result = load_txt(str(f))

        # Assert
        assert result == ""

    def test_reads_utf8_characters(self, tmp_path):
        # Arrange
        f = tmp_path / "unicode.txt"
        f.write_text("Zażółć gęślą jaźń", encoding="utf-8")

        # Act
        result = load_txt(str(f))

        # Assert
        assert result == "Zażółć gęślą jaźń"

    def test_missing_file_raises_file_not_found(self):
        # Act & Assert
        with pytest.raises(FileNotFoundError):
            load_txt("/nonexistent/path/file.txt")


class TestLoadPdf:
    @patch("src.document_processing.loaders.PdfReader")
    def test_extracts_text_from_single_page(self, mock_reader_cls):
        # Arrange
        page = MagicMock()
        page.extract_text.return_value = "Page one text"
        mock_reader_cls.return_value.pages = [page]

        # Act
        result = load_pdf("test.pdf")

        # Assert
        assert result == "Page one text"

    @patch("src.document_processing.loaders.PdfReader")
    def test_page_with_no_text_returns_empty_string(self, mock_reader_cls):
        # Arrange
        page = MagicMock()
        page.extract_text.return_value = None
        mock_reader_cls.return_value.pages = [page]

        # Act
        result = load_pdf("test.pdf")

        # Assert
        assert result == ""

    @patch("src.document_processing.loaders.PdfReader")
    def test_concatenates_text_from_multiple_pages(self, mock_reader_cls):
        # Arrange
        page1 = MagicMock()
        page1.extract_text.return_value = "First. "
        page2 = MagicMock()
        page2.extract_text.return_value = "Second."
        mock_reader_cls.return_value.pages = [page1, page2]

        # Act
        result = load_pdf("test.pdf")

        # Assert
        assert result == "First. Second."


class TestLoadDoc:
    @patch("src.document_processing.loaders.Document")
    def test_extracts_single_paragraph(self, mock_doc_cls):
        # Arrange
        para = MagicMock()
        para.text = "A paragraph"
        mock_doc_cls.return_value.paragraphs = [para]

        # Act
        result = load_doc("test.docx")

        # Assert
        assert result == "A paragraph\n"

    @patch("src.document_processing.loaders.Document")
    def test_empty_doc_returns_empty_string(self, mock_doc_cls):
        # Arrange
        mock_doc_cls.return_value.paragraphs = []

        # Act
        result = load_doc("test.docx")

        # Assert
        assert result == ""

    @patch("src.document_processing.loaders.Document")
    def test_joins_multiple_paragraphs_with_newlines(self, mock_doc_cls):
        # Arrange
        p1 = MagicMock()
        p1.text = "Para one"
        p2 = MagicMock()
        p2.text = "Para two"
        mock_doc_cls.return_value.paragraphs = [p1, p2]

        # Act
        result = load_doc("test.docx")

        # Assert
        assert result == "Para one\nPara two\n"
