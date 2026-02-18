from unittest.mock import MagicMock, patch

import pytest
import requests

from src.document_processing.text_embedder import get_embedding, EmbeddingError


def _make_success_response(embedding):
    """Helper to build a mock 200 response with the given embedding."""
    response = MagicMock()
    response.status_code = 200
    response.json.return_value = {"embedding": embedding}
    return response


class TestGetEmbedding:
    def test_returns_embedding_on_success(self, mock_session):
        # Arrange
        mock_session.post.return_value = _make_success_response([0.1, 0.2, 0.3])

        # Act
        result = get_embedding("hello", "http://embed.local/api", session=mock_session)

        # Assert
        assert result == [0.1, 0.2, 0.3]

    def test_raises_embedding_error_on_api_failure(self, mock_session):
        # Arrange
        response = MagicMock()
        response.status_code = 500
        response.text = "Internal Server Error"
        mock_session.post.return_value = response

        # Act & Assert
        with pytest.raises(EmbeddingError, match="Embedding API error 500"):
            get_embedding("hello", "http://embed.local/api", session=mock_session)

    def test_raises_embedding_error_on_connection_failure(self, mock_session):
        # Arrange
        mock_session.post.side_effect = requests.exceptions.ConnectionError("refused")

        # Act & Assert
        with pytest.raises(EmbeddingError, match="Cannot connect to embedding service"):
            get_embedding("hello", "http://embed.local/api", session=mock_session)

    def test_sends_custom_model_in_payload(self, mock_session):
        # Arrange
        mock_session.post.return_value = _make_success_response([0.5])

        # Act
        get_embedding("text", "http://embed.local/api", model="custom-model", session=mock_session)

        # Assert
        payload = mock_session.post.call_args.kwargs["json"]
        assert payload["model"] == "custom-model"

    def test_sends_default_model_all_minilm(self, mock_session):
        # Arrange
        mock_session.post.return_value = _make_success_response([0.5])

        # Act
        get_embedding("text", "http://embed.local/api", session=mock_session)

        # Assert
        payload = mock_session.post.call_args.kwargs["json"]
        assert payload["model"] == "all-minilm"

    def test_posts_to_provided_url(self, mock_session):
        # Arrange
        mock_session.post.return_value = _make_success_response([0.5])
        url = "http://embed.local/api/embeddings"

        # Act
        get_embedding("text", url, session=mock_session)

        # Assert
        actual_url = mock_session.post.call_args.args[0]
        assert actual_url == url

    def test_sends_json_content_type_header(self, mock_session):
        # Arrange
        mock_session.post.return_value = _make_success_response([0.5])

        # Act
        get_embedding("text", "http://embed.local/api", session=mock_session)

        # Assert
        headers = mock_session.post.call_args.kwargs["headers"]
        assert headers["Content-Type"] == "application/json"

    @patch("src.document_processing.text_embedder.requests.Session")
    def test_creates_session_when_none_provided(self, mock_session_cls):
        # Arrange
        mock_session_instance = MagicMock()
        mock_session_instance.post.return_value = _make_success_response([0.5])
        mock_session_cls.return_value = mock_session_instance

        # Act
        result = get_embedding("text", "http://embed.local/api")

        # Assert
        mock_session_cls.assert_called_once()
        assert result == [0.5]
