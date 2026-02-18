import logging
from typing import List

import requests

logger = logging.getLogger(__name__)


class EmbeddingError(Exception):
    """Raised when the embedding API returns an error."""


def get_embedding(prompt: str, url: str, model: str = "all-minilm",
                   session: requests.Session = None) -> List[float]:
    session = session or requests.Session()
    headers = {"Content-Type": "application/json"}
    data = {
        "model": model,
        "prompt": prompt
    }

    try:
        response = session.post(url, headers=headers, json=data)
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Cannot connect to embedding service at {url}: {e}")
        raise EmbeddingError(f"Cannot connect to embedding service at {url}") from e

    if response.status_code == 200:
        result = response.json()
        return result['embedding']
    else:
        logger.error(f"Embedding API error {response.status_code}: {response.text}")
        raise EmbeddingError(f"Embedding API error {response.status_code}: {response.text}")
