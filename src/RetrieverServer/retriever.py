import os
import sys
import requests
from typing import List, Dict
from dotenv import load_dotenv

# Add the project root to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from src.document_processing.text_embedder import get_embedding

def embedding_question(question: str, url: str):
    query_vector = get_embedding(question,url)
    if not query_vector:
        return []
    return query_vector

def similarity_search(db_url: str,query_vector: List[float], collection_name: str = "TestDocs", limit: int = 3) -> List[str]:
    if not query_vector:
        return []
    
    query = {
        "query": f"""{{
            Get {{
                {collection_name}(
                    nearVector: {{
                        vector: {query_vector}
                    }}
                    limit: {limit}
                ) {{
                    text
                }}
            }}
        }}"""
    }
    
    try:
        response = requests.post(
            f"{db_url}/v1/graphql",
            json=query,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            documents = result.get("data", {}).get("Get", {}).get(collection_name, [])
            return [doc.get("text", "") for doc in documents]
        else:
            print(f"Search failed: {response.text}")
            return []
            
    except Exception as e:
        print(f"Search error: {e}")
        return []


