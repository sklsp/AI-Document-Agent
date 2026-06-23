def ask_llm(prompt: str, model: str = "ggml-small", host: str = "http://localhost:11434", stream: bool = False) -> str:
    """Send a prompt to a local Ollama server and return the text response.

    Args:
        prompt: The text prompt to send to the model.
        model: The model name to use on the Ollama server.
        host: Base URL of the Ollama server (include scheme and port).
        stream: Whether to request streaming responses (not supported here).

    Returns:
        The model output as a string. If the response cannot be parsed as JSON,
        returns the raw response text.
    """
    try:
        import requests
    except ImportError:
        raise RuntimeError("The 'requests' library is required. Install it with: pip install requests")

    url = host.rstrip("/") + "/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": stream,
    }

    try:
        resp = requests.post(url, json=payload, timeout=30)
        resp.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"Failed to contact Ollama server at {url}: {e}")

    # Try to parse Ollama-style JSON responses, but fall back to raw text
    try:
        data = resp.json()
    except ValueError:
        return resp.text

    # Common Ollama response shapes: {'response': '...'} or {'result': [...]}
    if isinstance(data, dict):
        if "response" in data and isinstance(data["response"], str):
            return data["response"]

        if "result" in data and isinstance(data["result"], list):
            # Look for an output_text field in the result content
            for item in data["result"]:
                if isinstance(item, dict) and item.get("type") == "message":
                    for part in item.get("content", []):
                        if isinstance(part, dict) and part.get("type") == "output_text":
                            return part.get("text", "")
            # Fallback: return stringified result
            return str(data["result"])

    # Last resort: return the raw response body
    return resp.text