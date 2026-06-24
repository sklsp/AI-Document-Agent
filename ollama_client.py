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

    # If user left the default model, try to auto-detect an available model on the server.
    if model == "ggml-small":
        try:
            models_resp = list_models(host)
            # models_resp maps urls -> json/text; look for common shapes
            detected = None
            for val in models_resp.values():
                if isinstance(val, dict):
                    # OpenAI-like '/v1/models' response: {object: 'list', data: [{id: ...}, ...]}
                    data = val.get("data") if isinstance(val.get("data"), list) else None
                    if data:
                        first = data[0]
                        if isinstance(first, dict) and "id" in first:
                            detected = first["id"]
                            break
                    # Ollama-like: maybe a list of model names
                    if isinstance(val, list) and val:
                        candidate = val[0]
                        if isinstance(candidate, str):
                            detected = candidate
                            break
            if detected:
                model = detected
        except Exception:
            # ignore errors from model-listing and continue using provided model
            pass

    # Try several common Ollama endpoints in case the server exposes a different path.
    endpoints = [
        "/api/generate",
        "/generate",
        "/api/chat",
        "/chat",
        "/v1/completions",
        "/v1/chat/completions",
        "/completion",
    ]

    last_exc = None
    resp = None
    for ep in endpoints:
        url = host.rstrip("/") + ep
        # Choose payload shape depending on endpoint
        if "chat" in ep or "chat" in url or "v1/chat" in ep:
            ep_payload = {"model": model, "messages": [{"role": "user", "content": prompt}]}
        elif "v1/completions" in ep or "completions" in ep:
            ep_payload = {"model": model, "prompt": prompt}
        else:
            ep_payload = {"model": model, "prompt": prompt, "stream": stream}

        try:
            resp = requests.post(url, json=ep_payload, timeout=30)
            resp.raise_for_status()
            break
        except requests.RequestException as e:
            # save last exception and try next endpoint
            body = None
            try:
                body = e.response.text if getattr(e, 'response', None) is not None else None
            except Exception:
                body = None
            last_exc = (url, e, body)
            resp = None
            continue

    if resp is None:
        if last_exc is None:
            raise RuntimeError("Failed to contact Ollama server: no endpoints attempted")
        url, exc, body = last_exc
        msg = f"Failed to contact Ollama server. Last error at {url}: {exc}"
        if body:
            msg += f" -- response body: {body}"
        raise RuntimeError(msg)

    # Try to parse Ollama-style JSON responses, but fall back to raw text
    try:
        data = resp.json()
    except ValueError:
        return resp.text

    # If server streamed NDJSON or chunked JSON, try to assemble pieces.
    try:
        import json as _json
        assembled = []
        stream_seen = False
        # iterate over lines if available
        for line in resp.iter_lines(decode_unicode=True):
            if not line:
                continue
            try:
                obj = _json.loads(line)
            except Exception:
                # not JSON, skip
                continue

            # Ollama streaming shape: objects with 'message' or incremental 'choices' deltas
            if isinstance(obj, dict):
                # common shape: {"model":..., "message": {"role":"assistant","content": "..."}, "done": false}
                if "message" in obj and isinstance(obj["message"], dict):
                    cont = obj["message"].get("content")
                    if isinstance(cont, str):
                        assembled.append(cont)
                        stream_seen = True

                # OpenAI-style streaming: {"choices":[{"delta": {"content": "..."}}], ...}
                if "choices" in obj and isinstance(obj["choices"], list):
                    for ch in obj["choices"]:
                        if isinstance(ch, dict):
                            delta = ch.get("delta") or {}
                            if isinstance(delta, dict):
                                cont = delta.get("content")
                                if isinstance(cont, str):
                                    assembled.append(cont)
                                    stream_seen = True
                            # fallback: message.content in choices
                            msg = ch.get("message")
                            if isinstance(msg, dict):
                                cont = msg.get("content")
                                if isinstance(cont, str):
                                    assembled.append(cont)
                                    stream_seen = True

                if obj.get("done") is True:
                    break

        if stream_seen:
            return "".join(assembled)
    except Exception:
        # if streaming parse fails, fall back to JSON parsing above
        pass

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

        # OpenAI-compatible shape: {"choices": [ {"message": {"content": ...}} ] }
        if "choices" in data and isinstance(data["choices"], list) and data["choices"]:
            first = data["choices"][0]
            # Chat response
            if isinstance(first, dict):
                if "message" in first and isinstance(first["message"], dict):
                    content = first["message"].get("content")
                    if content:
                        return content
                # Completion-style
                if "text" in first and isinstance(first["text"], str):
                    return first["text"]

        # Some servers return an 'output' list
        if "output" in data:
            out = data["output"]
            if isinstance(out, list):
                return "\n".join([str(x) for x in out])
            return str(out)

    # Last resort: return the raw response body
    return resp.text


def list_models(host: str = "http://localhost:11434"):
    """Try to list available models from the Ollama server using common endpoints."""
    try:
        import requests
    except ImportError:
        raise RuntimeError("The 'requests' library is required. Install it with: pip install requests")

    endpoints = ["/models", "/api/models", "/models/list", "/v1/models"]
    results = {}
    for ep in endpoints:
        url = host.rstrip("/") + ep
        try:
            r = requests.get(url, timeout=5)
            try:
                results[url] = r.json()
            except Exception:
                results[url] = r.text
        except Exception as e:
            results[url] = str(e)

    return results