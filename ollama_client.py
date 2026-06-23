import requests

def ask_llm():
    response = requests.post(
        "https://localhost:11434", #this can also be an API if the LLM is hosted somewhere else
        json={
            "model": "pass",
            "prompt": "pass",
            "stream": False
        }
    )
    return response.json()['response']