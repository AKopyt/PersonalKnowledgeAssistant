from unittest.mock import MagicMock

from src.database.base import VectorStore
from src.database.weaviate_client import WeaviateVectorStore

DB_URL = "http://weaviate:8080"


def _make_success_response(object_id="fake-uuid"):
    """Helper to build a mock 200 response with the given object ID."""
    response = MagicMock()
    response.status_code = 200
    response.json.return_value = {"id": object_id}
    return response


class TestWeaviateVectorStore:
    def test_save_returns_object_id_on_success(self, mock_session):
        # Arrange
        mock_session.post.return_value = _make_success_response("abc-123")
        store = WeaviateVectorStore(DB_URL, session=mock_session)

        # Act
        result = store.save("some text", [0.1, 0.2])

        # Assert
        assert result == "abc-123"

    def test_save_returns_none_on_http_error(self, mock_session):
        # Arrange
        response = MagicMock()
        response.status_code = 500
        response.text = "error"
        mock_session.post.return_value = response
        store = WeaviateVectorStore(DB_URL, session=mock_session)

        # Act
        result = store.save("text", [0.1])

        # Assert
        assert result is None

    def test_save_returns_none_on_connection_exception(self, mock_session):
        # Arrange
        mock_session.post.side_effect = ConnectionError("refused")
        store = WeaviateVectorStore(DB_URL, session=mock_session)

        # Act
        result = store.save("text", [0.1])

        # Assert
        assert result is None

    def test_save_sends_text_and_vector_in_payload(self, mock_session):
        # Arrange
        mock_session.post.return_value = _make_success_response()
        store = WeaviateVectorStore(DB_URL, session=mock_session)

        # Act
        store.save("my text", [0.1, 0.2, 0.3])

        # Assert
        payload = mock_session.post.call_args.kwargs["json"]
        assert payload["properties"]["text"] == "my text"
        assert payload["vector"] == [0.1, 0.2, 0.3]

    def test_save_posts_to_v1_objects_endpoint(self, mock_session):
        # Arrange
        mock_session.post.return_value = _make_success_response()
        store = WeaviateVectorStore(DB_URL, session=mock_session)

        # Act
        store.save("text", [0.1])

        # Assert
        actual_url = mock_session.post.call_args.args[0]
        assert actual_url == f"{DB_URL}/v1/objects"

    def test_save_uses_custom_collection_name_in_payload(self, mock_session):
        # Arrange
        mock_session.post.return_value = _make_success_response()
        store = WeaviateVectorStore(DB_URL, collection_name="Notes", session=mock_session)

        # Act
        store.save("text", [0.1])

        # Assert
        payload = mock_session.post.call_args.kwargs["json"]
        assert payload["class"] == "Notes"

    def test_default_collection_name_is_documents(self, mock_session):
        # Act
        store = WeaviateVectorStore(DB_URL, session=mock_session)

        # Assert
        assert store.collection_name == "Documents"

    def test_save_sends_json_content_type_header(self, mock_session):
        # Arrange
        mock_session.post.return_value = _make_success_response()
        store = WeaviateVectorStore(DB_URL, session=mock_session)

        # Act
        store.save("text", [0.1])

        # Assert
        headers = mock_session.post.call_args.kwargs["headers"]
        assert headers["Content-Type"] == "application/json"

    def test_is_subclass_of_vector_store(self):
        # Assert
        assert issubclass(WeaviateVectorStore, VectorStore)
