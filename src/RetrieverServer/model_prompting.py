import requests
import json
import os


def send_prompt_to_model(prompt, model="llama3.2", url=None):
    """
    Send a prompt to Llama 3.2 and get the response
    """
    # Use environment variable or default to ollama service in Docker
    if url is None:
        url = os.getenv("OLLAMA_URL", "http://ollama:11434/api/generate")

    headers = {"Content-Type": "application/json"}
    data = {
        "model": model,
        "prompt": prompt,
        "stream": False  # Set to True if you want streaming responses
    }

    try:
        response = requests.post(url, headers=headers, json=data)

        if response.status_code == 200:
            result = response.json()
            return result['response']
        else:
            raise Exception(f"Error {response.status_code}: {response.text}")

    except requests.exceptions.ConnectionError as e:
        raise Exception(f"Cannot connect to Ollama at {url}. Error: {e}")

