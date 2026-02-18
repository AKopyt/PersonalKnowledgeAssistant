from typing import Callable, Dict

from src.document_processing.chunking.base import ChunkingStrategy
from src.document_processing.chunking.fixed_size import FixedSizeChunking
from src.enums.chunking_types import ChunkingType


class ChunkingStrategyFactory:
    """Creates ChunkingStrategy instances by type name."""

    def __init__(self):
        self._creators: Dict[str, Callable[..., ChunkingStrategy]] = {}

    def register(self, chunking_type: str, creator: Callable[..., ChunkingStrategy]) -> None:
        self._creators[chunking_type] = creator

    def create(self, chunking_type: str, **kwargs) -> ChunkingStrategy:
        creator = self._creators.get(chunking_type)
        if creator is None:
            raise ValueError(f"Unsupported chunking type: {chunking_type}")
        return creator(**kwargs)


def create_default_chunking_factory() -> ChunkingStrategyFactory:
    factory = ChunkingStrategyFactory()
    factory.register(
        ChunkingType.FIXED_SIZE.value,
        lambda chunk_size=1000: FixedSizeChunking(chunk_size=chunk_size),
    )
    return factory
