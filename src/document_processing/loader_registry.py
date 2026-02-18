import os
from typing import Callable, Dict

from src.document_processing.loaders import load_pdf, load_txt, load_doc
from src.enums.file_types import FileType


class DocumentLoaderRegistry:
    """Maps file extensions to loader functions."""

    def __init__(self):
        self._loaders: Dict[str, Callable[[str], str]] = {}

    def register(self, extension: str, loader: Callable[[str], str]) -> None:
        self._loaders[extension.lower()] = loader

    def load(self, file_path: str) -> str:
        ext = os.path.splitext(file_path)[1].lower()
        loader = self._loaders.get(ext)
        if loader is None:
            raise ValueError(f"Unsupported file type: {ext}")
        return loader(file_path)


def create_default_loader_registry() -> DocumentLoaderRegistry:
    registry = DocumentLoaderRegistry()
    registry.register(FileType.PDF.value, load_pdf)
    registry.register(FileType.TXT.value, load_txt)
    registry.register(FileType.DOC.value, load_doc)
    registry.register(FileType.DOCX.value, load_doc)
    return registry
