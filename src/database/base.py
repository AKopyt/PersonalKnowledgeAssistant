from abc import ABC, abstractmethod
from typing import List, Optional


class VectorStore(ABC):

    @abstractmethod
    def save(self, text: str, embedding: List[float]) -> Optional[str]:
        """Persist a text chunk and its embedding. Returns the stored object ID, or None on failure."""
