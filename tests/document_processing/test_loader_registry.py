from unittest.mock import MagicMock, patch

import pytest

from src.document_processing.loader_registry import (
    DocumentLoaderRegistry,
    create_default_loader_registry,
)


class TestDocumentLoaderRegistry:
    def test_load_calls_registered_loader_and_returns_result(self):
        # Arrange
        registry = DocumentLoaderRegistry()
        loader = MagicMock(return_value="loaded text")
        registry.register(".txt", loader)

        # Act
        result = registry.load("document.txt")

        # Assert
        assert result == "loaded text"
        loader.assert_called_once_with("document.txt")

    def test_load_unregistered_extension_raises_value_error(self):
        # Arrange
        registry = DocumentLoaderRegistry()

        # Act & Assert
        with pytest.raises(ValueError, match="Unsupported file type: .xyz"):
            registry.load("file.xyz")

    def test_custom_loader_registration(self):
        # Arrange
        registry = DocumentLoaderRegistry()
        custom_loader = MagicMock(return_value="custom content")
        registry.register(".md", custom_loader)

        # Act
        result = registry.load("readme.md")

        # Assert
        assert result == "custom content"

    def test_extracts_extension_from_nested_path(self):
        # Arrange
        registry = DocumentLoaderRegistry()
        loader = MagicMock(return_value="text")
        registry.register(".txt", loader)

        # Act
        result = registry.load("/some/deep/path/to/file.txt")

        # Assert
        assert result == "text"
        loader.assert_called_once_with("/some/deep/path/to/file.txt")

    def test_extension_matching_is_case_insensitive(self):
        # Arrange
        registry = DocumentLoaderRegistry()
        loader = MagicMock(return_value="text")
        registry.register(".TXT", loader)

        # Act
        result = registry.load("FILE.txt")

        # Assert
        assert result == "text"


class TestCreateDefaultLoaderRegistry:
    @patch("src.document_processing.loader_registry.load_pdf")
    @patch("src.document_processing.loader_registry.load_txt")
    @patch("src.document_processing.loader_registry.load_doc")
    def test_registers_all_supported_file_types(self, mock_doc, mock_txt, mock_pdf):
        # Arrange
        mock_pdf.return_value = "pdf"
        mock_txt.return_value = "txt"
        mock_doc.return_value = "doc"
        registry = create_default_loader_registry()

        # Act & Assert
        assert registry.load("test.pdf") == "pdf"
        assert registry.load("test.txt") == "txt"
        assert registry.load("test.doc") == "doc"
        assert registry.load("test.docx") == "doc"
