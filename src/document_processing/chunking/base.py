from abc import ABC, abstractmethod
from typing import Dict, Any, List

class ChunkingStrategy(ABC):

    @abstractmethod
    def chunk(self, text: str, metadata: Dict[str, Any]) -> List[Dict]:
        pass