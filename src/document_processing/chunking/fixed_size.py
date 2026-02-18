from typing import Any, Dict, List

from src.document_processing.chunking.base import ChunkingStrategy, ChunkResult


class FixedSizeChunking(ChunkingStrategy):
    def __init__(self, chunk_size: int = 1000):
        self.chunk_size = chunk_size

    def chunk(self, text: str, metadata: Dict[str, Any]) -> List[ChunkResult]:
        chunks = []
        for i in range(0, len(text), self.chunk_size):
            chunk_text = text[i:i + self.chunk_size]
            chunks.append({
                "text": chunk_text,
                "metadata": metadata
            })
        return chunks

