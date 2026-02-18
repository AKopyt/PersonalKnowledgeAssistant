from abc import ABC, abstractmethod
from typing import Any, Dict, List, TypedDict


class ChunkResult(TypedDict):
    text: str
    metadata: Dict[str, Any]


class ChunkingStrategy(ABC):

    @abstractmethod
    def chunk(self, text: str, metadata: Dict[str, Any]) -> List[ChunkResult]:
        pass