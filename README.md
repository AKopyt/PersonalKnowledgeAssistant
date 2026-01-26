
# Personal Knowledge Assistant

Personal Knowledge Assistant is a lightweight **Retrieval-Augmented Generation (RAG)** project for indexing and querying personal documents using semantic search and vector databases.

## Features
- Document ingestion and processing
- Multiple text chunking strategies (fixed, sentence-based, semantic)
- Text embedding generation
- Vector storage and retrieval with **Weaviate**
- Simple chat interface for document-based Q&A
- Modular and extensible architecture

## How It Works
1. Documents are loaded and split into chunks.
2. Chunks are embedded into vector representations.
3. Embeddings are stored in a vector database.
4. User queries retrieve relevant chunks via semantic search.
5. Results are used to answer questions in a chat interface.
