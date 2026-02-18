def format_chunk(filename: str, index: int, total: int, text: str) -> str:
    """Format a chunk with file and position metadata."""
    return f"[File: {filename}, Chunk: {index}/{total}]\n\n{text}"
