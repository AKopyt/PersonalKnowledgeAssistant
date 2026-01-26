import requests
import json
import sys
import os
from dotenv import load_dotenv

load_dotenv()

def send_question_to_server(question: str, base_url: str = os.getenv("RETRIEVER_URL")) -> dict:
    """Send question to RetrieverServer and return response"""
    url = f"{base_url}/search"
    payload = {"question": question}

    try:
        response = requests.get(url, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        return {"error": "Could not connect to server. Make sure RetrieverServer is running on localhost:8000"}
    except requests.exceptions.RequestException as e:
        return {"error": f"Request failed: {str(e)}"}

def main():
    """Main console client loop"""
    print("=== Personal Knowledge Assistant Console Client ===")
    print("Type 'quit' or 'exit' to stop")
    print("Make sure RetrieverServer is running on localhost:8000")
    print("-" * 50)

    while True:
        try:
            question = input("\nEnter your question: ").strip()

            if question.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break

            if not question:
                print("Please enter a valid question.")
                continue

            print("Sending question to server...")
            response = send_question_to_server(question)

            if "error" in response:
                print(f"L Error: {response['error']}")
            else:
                print(f"=� Question: {response.get('question', 'N/A')}")
                print(f"=� Answer: {response.get('answer', 'No answer received')}")

        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            sys.exit(0)
        except Exception as e:
            print(f"L Unexpected error: {str(e)}")

if __name__ == "__main__":
    main()