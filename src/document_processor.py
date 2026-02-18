import logging
import os
from typing import List

logger = logging.getLogger(__name__)

from src.document_processing.loader_registry import (
    DocumentLoaderRegistry,
    create_default_loader_registry,
)
from src.document_processing.chunking.factory import (
    ChunkingStrategyFactory,
    create_default_chunking_factory,
)
from src.document_processing.text_embedder import get_embedding
from src.document_processing.chunk_formatter import format_chunk
from src.database.base import VectorStore


class DocumentProcessor:
    """Thin orchestration facade for the document processing pipeline."""

    def __init__(
        self,
        data_directory: str,
        chunking_type: str,
        embedding_url: str,
        vector_store: VectorStore,
        chunk_size: int = 1000,
        embedding_model: str = "all-minilm",
        loader_registry: DocumentLoaderRegistry = None,
        chunking_factory: ChunkingStrategyFactory = None,
    ):
        self.data_directory = data_directory
        self.chunking_type = chunking_type
        self.chunk_size = chunk_size
        self.embedding_model = embedding_model
        self.embedding_url = embedding_url

        self.loader_registry = loader_registry or create_default_loader_registry()
        self.chunking_factory = chunking_factory or create_default_chunking_factory()
        self.vector_store = vector_store

    def process_file(self, filename: str, chunk_size: int = None,
                     model: str = None) -> List[str]:
        """Process a single file: load -> chunk -> embed -> store."""
        chunk_size = chunk_size or self.chunk_size
        model = model or self.embedding_model

        try:
            # 1. Load
            file_path = os.path.join(self.data_directory, filename)
            text = self.loader_registry.load(file_path)
            logger.info(f"Loaded file: {len(text)} characters")

            # 2. Chunk
            metadata = {"file_path": file_path, "file_name": filename}
            chunker = self.chunking_factory.create(
                self.chunking_type, chunk_size=chunk_size
            )
            chunks = chunker.chunk(text, metadata)
            logger.info(f"Created {len(chunks)} chunks")

            # 3. Embed and store
            saved_ids = self._embed_and_store(chunks, filename, model)

            logger.info(f"Processing complete! Saved {len(saved_ids)}/{len(chunks)} chunks")
            return saved_ids

        except Exception as e:
            logger.error(f"Error processing file: {e}")
            return []

    def _embed_and_store(self, chunks: List[dict], filename: str,
                         model: str) -> List[str]:
        """Embed each chunk and persist it to the vector store."""
        saved_ids = []
        total = len(chunks)

        for i, chunk_data in enumerate(chunks):
            try:
                chunk_text = chunk_data["text"]
                chunk_with_info = format_chunk(filename, i + 1, total, chunk_text)

                embedding = get_embedding(chunk_with_info, self.embedding_url, model)
                if not embedding:
                    logger.warning(f"Failed to embed chunk {i+1}")
                    continue

                object_id = self.vector_store.save(chunk_with_info, embedding)
                if object_id:
                    saved_ids.append(object_id)
                    logger.info(f"Saved chunk {i+1}/{total}")
                else:
                    logger.warning(f"Failed to save chunk {i+1}")

            except Exception as e:
                logger.error(f"Error processing chunk {i+1}: {e}")

        return saved_ids
