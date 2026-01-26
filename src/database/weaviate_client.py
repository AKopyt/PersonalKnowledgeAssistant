import requests
import sys
import os
from dotenv import load_dotenv
load_dotenv()
from src.document_processing.text_embedder import get_embedding

def save_text_to_vector_db(text: str, collection_name: str = "Example", model: str = "all-minilm"):
    try:
        embedding = get_embedding(text, model)
        if not embedding:
            print(" Failed to get embedding")
            return None
        
        print(f"Got embedding with {len(embedding)} dimensions")
    except Exception as e:
        print(f"Embedding error: {e}")
        return None

    try:
        db_url = os.getenv("WEAVIATE_URL")
        data_object = {
            "class": collection_name,
            "properties": {
                "text": text
            },
            "vector": embedding
        }
        
        save_response = requests.post(
            f"{db_url}/v1/objects",
            json=data_object,
            headers={"Content-Type": "application/json"}
        )
        
        if save_response.status_code == 200:
            result = save_response.json()
            object_id = result.get("id")
            print(f"Saved to DB with ID: {object_id}")
            return object_id
        else:
            print(f"DB save failed: {save_response.text}")
            return None
            
    except Exception as e:
        print(f"Database error: {e}")
        return None


def main():
    text = "Example text"
    result = save_text_to_vector_db(text)
    
    if result:
        print("SUCCESS!")
    else:
        print("FAILED!")


if __name__ == "__main__":
    main()