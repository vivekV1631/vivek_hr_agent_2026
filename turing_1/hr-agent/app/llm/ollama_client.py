import requests

# Ollama LLM configuration
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3"

# Send prompt to Ollama Llama3 model and get response
def chat(prompt: str):
    """Call Ollama LLM API with prompt and return generated response"""
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False
    }

    response = requests.post(OLLAMA_URL, json=payload)
    return response.json()["response"]
