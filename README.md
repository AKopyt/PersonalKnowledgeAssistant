# Personal Knowledge Assistant

Personal Knowledge Assistant is a lightweight Retrieval-Augmented Generation (RAG) project for indexing and querying personal documents using semantic search and vector databases.

## Features

- Document ingestion and processing (PDF, DOCX, TXT)
- Fixed-size text chunking with extensible strategy pattern
- Text embedding generation via Ollama (`all-minilm`)
- Vector storage and retrieval with Weaviate
- FastAPI server for document-based Q&A
- Console client for interactive querying
- Dockerized deployment with automatic document ingestion on startup

## Architecture

The system is composed of three services:

| Service | Description | Location |
|---------|-------------|----------|
| **RetrieverServer** | FastAPI app that embeds questions, searches Weaviate, and generates answers via Ollama | `src/RetrieverServer/` |
| **DocUploaderTool** | CLI tool that loads, chunks, embeds, and stores documents into Weaviate | `src/DocUploaderTool/` |
| **ConsoleClient** | Interactive command-line client that sends questions to the RetrieverServer | `src/ConsoleClient/` |

### Q&A Flow

1. User types a question in the ConsoleClient
2. ConsoleClient sends a POST request to `RetrieverServer /search`
3. RetrieverServer embeds the question using Ollama (`all-minilm`)
4. Embedded vector is used for similarity search against Weaviate
5. Top 3 matching document chunks are retrieved
6. Chunks + question are formatted into a RAG prompt and sent to Ollama (`llama3.2`)
7. Generated answer is returned to the client

## How to Run

### 1. Install and run Ollama locally

Install [Ollama](https://ollama.ai/) and pull the required models:

```bash
ollama pull all-minilm
ollama pull llama3.2
```

- `all-minilm` - embedding model for converting text into vectors
- `llama3.2` - language model for generating answers

> **Why is Ollama not running in Docker?**
> Ollama needs GPU access for reasonable inference speed. Docker containers don't have straightforward GPU access, especially on Windows/WSL2. Running Ollama directly on your machine lets it use your GPU without extra configuration.

### 2. Start the application

**PowerShell (Windows):**
```powershell
$env:DOCS_PATH="C:\path\to\your\documents"; docker compose up -d
```

**Bash (Linux/macOS):**
```bash
DOCS_PATH=/path/to/your/documents docker compose up -d
```

Replace the `DOCS_PATH` value with the path to a folder containing your documents (PDF, DOCX, or TXT files). Documents are automatically ingested on startup.

This starts two containers:
- **Weaviate** vector database on port `8080`
- **App** (document ingestion + RetrieverServer) on port `8000`

### 3. Query your documents

Run the console client:

```bash
uv run python -m src.ConsoleClient.main
```

## Environment Variables

These are configured automatically in `docker-compose.yml` for containerized deployment:

| Variable | Description | Default (Docker) |
|----------|-------------|------------------|
| `WEAVIATE_URL` | Weaviate database URL | `http://weaviate:8080` |
| `EMBEDDING_MODEL_URL` | Ollama embeddings endpoint | `http://host.docker.internal:11434/api/embeddings` |
| `OLLAMA_URL` | Ollama generation endpoint | `http://host.docker.internal:11434/api/generate` |
| `RETRIEVER_URL` | RetrieverServer URL (used by ConsoleClient) | — |

For local development without Docker, copy `.env_template` to `.env` and fill in the values.
