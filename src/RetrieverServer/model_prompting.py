import requests
import json


def send_prompt_to_model(prompt, model="llama3.2", url="http://localhost:11434/api/generate"):
    """
    Send a prompt to Llama 3.2 and get the response
    """
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

    except requests.exceptions.ConnectionError:
        raise Exception("Cannot connect to Ollama. Make sure it's running on port 11434")

