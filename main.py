from src.document_processor import DocumentProcessor

def main():
    processor = DocumentProcessor(
        data_directory="./data/documents",
        chunking_type="fixed_size",
        collection_name="TestDocs"
    )

    filename = "test_txt.txt"
    result = processor.process_file(
        filename=filename,
        chunk_size=800,
        model="all-minilm"
    )
    
    print(f"Processed {len(result)} chunks successfully!")

if __name__ == "__main__":
    main()