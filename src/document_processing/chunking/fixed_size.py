from typing import Dict, Any, List

from src.document_processing.chunking.base import ChunkingStrategy

class FixedSizeChunking(ChunkingStrategy):
    def chunk(self, text: str, metadata: Dict[str, Any], chunk_size=100):
        chunks = []
        for i in range(0, len(text), chunk_size):
            chunk_text = text[i:i + chunk_size]
            chunks.append({
                "text": chunk_text,
                "metadata": metadata
            })

        return chunks

