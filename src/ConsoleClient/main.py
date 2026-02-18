import argparse
import sys
import requests


DEFAULT_URL = "http://127.0.0.1:8000"


def send_question_to_server(question: str, base_url: str) -> dict:
    """Send question to RetrieverServer and return response"""
    url = f"{base_url}/search"
    payload = {"question": question}

    try:
        response = requests.post(url, json=payload, timeout=120)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        return {"error": f"Could not connect to server. Make sure RetrieverServer is running on {base_url}"}
    except requests.exceptions.Timeout:
        return {"error": "Request timed out. Ollama might be loading the model (this can take 30-60 seconds on first request)"}
    except requests.exceptions.RequestException as e:
        return {"error": f"Request failed: {str(e)}"}


def main():
    parser = argparse.ArgumentParser(description="Personal Knowledge Assistant Console Client")
    parser.add_argument("--url", default=DEFAULT_URL, help=f"RetrieverServer URL (default: {DEFAULT_URL})")
    args = parser.parse_args()

    print("=== Personal Knowledge Assistant Console Client ===")
    print(f"Server: {args.url}")
    print("Type 'quit' or 'exit' to stop")
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
            response = send_question_to_server(question, args.url)

            if "error" in response:
                print(f"Error: {response['error']}")
            else:
                print(f"Question: {response.get('question', 'N/A')}")
                print(f"Answer: {response.get('answer', 'No answer received')}")

        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            sys.exit(0)
        except Exception as e:
            print(f"Unexpected error: {str(e)}")


if __name__ == "__main__":
    main()
