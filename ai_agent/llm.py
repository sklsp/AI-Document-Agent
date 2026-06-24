"""LLM client utilities (Ollama)"""

def ask_llm(prompt: str, model: str = "ggml-small", host: str = "http://localhost:11434", stream: bool = False) -> str:
    """Send a prompt to a local Ollama server and return the text response.

    This function proxies the existing behavior from the top-level ollama_client module.
    """
    try:
        import requests
    except ImportError:
        raise RuntimeError("The 'requests' library is required. Install it with: pip install requests")

    # Local import to avoid circular import during packaging
    from . import llm as _self

    # If user left the default model, try to auto-detect an available model on the server.
    if model == "ggml-small":
        try:
            from .llm import list_models as _list_models
            models_resp = _list_models(host)
            detected = None
            for val in models_resp.values():
                if isinstance(val, dict):
                    data = val.get("data") if isinstance(val.get("data"), list) else None
                    if data:
                        first = data[0]
                        if isinstance(first, dict) and "id" in first:
                            detected = first["id"]
                            break
                    if isinstance(val, list) and val:
                        candidate = val[0]
                        if isinstance(candidate, str):
                            detected = candidate
                            break
            if detected:
                model = detected
        except Exception:
            pass

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
        if "chat" in ep or "chat" in url or "v1/chat" in ep:
            ep_payload = {"model": model, "messages": [{"role": "user", "content": prompt}]}
        elif "v1/completions" in ep or "completions" in ep:
            ep_payload = {"model": model, "prompt": prompt}
        else:
            ep_payload = {"model": model, "prompt": prompt, "stream": stream}

        try:
            resp = requests.post(url, json=ep_payload, timeout=30, stream=True)
            resp.raise_for_status()
            break
        except requests.RequestException as e:
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

    content_type = resp.headers.get('Content-Type', '').lower()
    transfer_enc = resp.headers.get('Transfer-Encoding', '').lower()
    should_stream = stream or 'ndjson' in content_type or 'event-stream' in content_type or 'chunked' in transfer_enc

    if should_stream:
        try:
            import json as _json
            assembled = []
            for line in resp.iter_lines(decode_unicode=True):
                if not line:
                    continue
                try:
                    obj = _json.loads(line)
                except Exception:
                    assembled.append(line)
                    continue

                if isinstance(obj, dict):
                    if "message" in obj and isinstance(obj["message"], dict):
                        cont = obj["message"].get("content")
                        if isinstance(cont, str):
                            assembled.append(cont)

                    if "choices" in obj and isinstance(obj["choices"], list):
                        for ch in obj["choices"]:
                            if isinstance(ch, dict):
                                delta = ch.get("delta") or {}
                                if isinstance(delta, dict):
                                    cont = delta.get("content")
                                    if isinstance(cont, str):
                                        assembled.append(cont)
                                msg = ch.get("message")
                                if isinstance(msg, dict):
                                    cont = msg.get("content")
                                    if isinstance(cont, str):
                                        assembled.append(cont)

                    if obj.get("done") is True:
                        break

            if assembled:
                return "".join(assembled)
        except Exception:
            pass

    try:
        data = resp.json()
    except Exception:
        return resp.text

    if isinstance(data, dict):
        if "response" in data and isinstance(data["response"], str):
            return data["response"]

        if "result" in data and isinstance(data["result"], list):
            for item in data["result"]:
                if isinstance(item, dict) and item.get("type") == "message":
                    for part in item.get("content", []):
                        if isinstance(part, dict) and part.get("type") == "output_text":
                            return part.get("text", "")
            return str(data["result"])

        if "choices" in data and isinstance(data["choices"], list) and data["choices"]:
            first = data["choices"][0]
            if isinstance(first, dict):
                if "message" in first and isinstance(first["message"], dict):
                    content = first["message"].get("content")
                    if content:
                        return content
                if "text" in first and isinstance(first["text"], str):
                    return first["text"]

        if "output" in data:
            out = data["output"]
            if isinstance(out, list):
                return "\n".join([str(x) for x in out])
            return str(out)

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
