#!/bin/bash
set -e

DOCS_DIR="/app/data/documents"
WEAVIATE_URL="${WEAVIATE_URL:-http://weaviate:8080}"

# Wait for Weaviate to be ready
echo "Waiting for Weaviate at $WEAVIATE_URL ..."
until curl -sf "$WEAVIATE_URL/v1/.well-known/ready" > /dev/null 2>&1; do
  sleep 2
done
echo "Weaviate is ready."

# Ingest all documents from the mounted folder
if [ -d "$DOCS_DIR" ] && [ "$(ls -A "$DOCS_DIR" 2>/dev/null)" ]; then
  echo "Found documents in $DOCS_DIR, starting ingestion..."
  uv run python -m src.DocUploaderTool.main --upload-directory "$DOCS_DIR" || echo "Ingestion failed."
else
  echo "No documents found in $DOCS_DIR, skipping ingestion."
fi

# Start the server
echo "Starting RetrieverServer..."
exec uv run uvicorn src.RetrieverServer.main:app --host 0.0.0.0 --port 8000
