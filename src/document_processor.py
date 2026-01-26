import os
from typing import Dict, List, Any
from src.document_processing.loaders import load_pdf, load_txt, load_doc
from src.document_processing.chunking.fixed_size import FixedSizeChunking
from src.database.weaviate_client import save_text_to_vector_db
from src.enums.file_types import FileType
from src.enums.chunking_types import ChunkingType


class DocumentProcessor:

    def __init__(self, data_directory, chunking_type, collection_name="Documents"):
        self.data_directory = data_directory
        self.chunking_type = chunking_type
        self.collection_name = collection_name

    def load_documents(self, filename: str) -> str:
        file_path = os.path.join(self.data_directory, filename)
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext == FileType.PDF.value:
            return load_pdf(file_path)
        elif ext == FileType.TXT.value:
            return load_txt(file_path)
        elif ext in [FileType.DOC.value, FileType.DOCX.value]:
            return load_doc(file_path)
        else:
            raise ValueError(f"Unsupported file type: {ext}")

    def chunk_text(self, text: str, metadata: Dict[str, Any], chunk_size: int = 1000) -> List[Dict]:
        if self.chunking_type == ChunkingType.FIXED_SIZE.value:
            chunker = FixedSizeChunking()
            return chunker.chunk(text, metadata, chunk_size)
        elif self.chunking_type == ChunkingType.SEMANTIC.value:
            raise NotImplementedError("Semantic chunking not implemented yet")
        elif self.chunking_type == ChunkingType.SENTENCE.value:
            raise NotImplementedError("Sentence chunking not implemented yet")
        else:
            raise ValueError(f"Unsupported chunking type: {self.chunking_type}")


    def process_file(self, filename: str, chunk_size: int = 1000, model: str = "all-minilm") -> List[str]:
        try:
            text = self.load_documents(filename)
            print(f"Loaded file: {len(text)} characters")

            file_path = os.path.join(self.data_directory, filename)
            metadata = {
                "file_path": file_path,
                "file_name": filename
            }

            chunks = self.chunk_text(text, metadata, chunk_size)
            print(f"Created {len(chunks)} chunks")

            saved_ids = []
            
            for i, chunk_data in enumerate(chunks):
                try:
                    chunk_text = chunk_data["text"]
                    chunk_with_info = f"[File: {filename}, Chunk: {i+1}/{len(chunks)}]\n\n{chunk_text}"

                    object_id = save_text_to_vector_db(
                        text=chunk_with_info,
                        collection_name=self.collection_name,
                        model=model
                    )
                    
                    if object_id:
                        saved_ids.append(object_id)
                        print(f"Saved chunk {i+1}/{len(chunks)}")
                    else:
                        print(f"Failed to save chunk {i+1}")
                        
                except Exception as e:
                    print(f"Error processing chunk {i+1}: {e}")
            
            print(f"Processing complete! Saved {len(saved_ids)}/{len(chunks)} chunks")
            return saved_ids
            
        except Exception as e:
            print(f"Error processing file: {e}")
            return []
