import argparse
import logging
import os

SUPPORTED_EXTENSIONS = {".pdf", ".txt", ".doc", ".docx"}
logger = logging.getLogger(__name__)


def main():
    from src.document_processor import DocumentProcessor
    from src.database.weaviate_client import WeaviateVectorStore

    parser = argparse.ArgumentParser(description="Process documents into vector store.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--file", help="Name of the file to process (inside data directory)")
    group.add_argument("--upload-directory", help="Path to directory with files to upload")
    parser.add_argument("--data-dir", default="./data/documents", help="Path to data directory (used with --file)")
    parser.add_argument("--chunk-size", type=int, default=800)
    parser.add_argument("--collection", default="TestDocs")
    parser.add_argument("--model", default="all-minilm")
    args = parser.parse_args()

    vector_store = WeaviateVectorStore(
        db_url=os.getenv("WEAVIATE_URL", "http://127.0.0.1:8080"),
        collection_name=args.collection,
    )

    if args.upload_directory:
        data_dir = args.upload_directory
        files = [
            f for f in os.listdir(data_dir)
            if os.path.isfile(os.path.join(data_dir, f))
            and os.path.splitext(f)[1].lower() in SUPPORTED_EXTENSIONS
        ]
        if not files:
            print(f"No supported files found in {data_dir}")
            return
        print(f"Found {len(files)} file(s) to process: {files}")
    else:
        data_dir = args.data_dir
        files = [args.file]

    processor = DocumentProcessor(
        data_directory=data_dir,
        chunking_type="fixed_size",
        embedding_url=os.getenv("EMBEDDING_MODEL_URL", "http://127.0.0.1:11434/api/embeddings"),
        vector_store=vector_store,
        chunk_size=args.chunk_size,
        embedding_model=args.model,
    )

    for filename in files:
        print(f"\nProcessing: {filename}")
        result = processor.process_file(filename=filename)
        print(f"Processed {len(result)} chunks from {filename}")

    print(f"\nDone! Processed {len(files)} file(s).")


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    main()
