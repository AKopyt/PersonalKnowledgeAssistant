import logging
from typing import List, Optional

import requests

from src.database.base import VectorStore

logger = logging.getLogger(__name__)


class WeaviateVectorStore(VectorStore):
    """Persists text and its pre-computed embedding vector to Weaviate."""

    def __init__(self, db_url: str, collection_name: str = "Documents",
                 session: requests.Session = None):
        self.db_url = db_url
        self.collection_name = collection_name
        self.session = session or requests.Session()

    def save(self, text: str, embedding: List[float]) -> Optional[str]:
        data_object = {
            "class": self.collection_name,
            "properties": {
                "text": text
            },
            "vector": embedding
        }

        try:
            response = self.session.post(
                f"{self.db_url}/v1/objects",
                json=data_object,
                headers={"Content-Type": "application/json"}
            )

            if response.status_code == 200:
                result = response.json()
                return result.get("id")
            else:
                logger.error(f"DB save failed: {response.text}")
                return None
        except Exception as e:
            logger.error(f"Database error: {e}")
            return None
