import requests

def get_embedding(prompt, url, model="all-minilm"):
    headers = {"Content-Type": "application/json"}
    data = {
        "model": model,
        "prompt": prompt
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        result = response.json()
        return result['embedding']
    else:
        raise Exception(f"Error {response.status_code}: {response.text}")
