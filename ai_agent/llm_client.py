from __future__ import annotations

from typing import Any, Dict, Optional

from .config import OLLAMA_BASE_URL

DEFAULT_MODEL = "ggml-small"
ENDPOINTS = [
    "/api/generate",
    "/generate",
    "/api/chat",
    "/chat",
    "/v1/completions",
    "/v1/chat/completions",
    "/completion",
]


def _format_url(base_url: str, endpoint: str) -> str:
    return f"{base_url.rstrip('/')}{endpoint}"


def _build_payload(prompt: str, model: str, endpoint: str, stream: bool) -> Dict[str, Any]:
    if "chat" in endpoint or "v1/chat" in endpoint:
        return {"model": model, "messages": [{"role": "user", "content": prompt}]}
    if "v1/completions" in endpoint or "completions" in endpoint:
        return {"model": model, "prompt": prompt}
    return {"model": model, "prompt": prompt, "stream": stream}


def _parse_response(resp: Any, stream: bool) -> str:
    content_type = resp.headers.get("Content-Type", "").lower()
    transfer_enc = resp.headers.get("Transfer-Encoding", "").lower()
    should_stream = stream or "ndjson" in content_type or "event-stream" in content_type or "chunked" in transfer_enc

    if should_stream:
        try:
            import json

            assembled = []
            for line in resp.iter_lines(decode_unicode=True):
                if not line:
                    continue
                try:
                    obj = json.loads(line)
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


def ask_llm(prompt: str, model: str = DEFAULT_MODEL, base_url: str | None = None, stream: bool = False) -> str:
    try:
        import requests
    except ImportError:
        raise RuntimeError("The 'requests' library is required. Install it with: pip install requests")

    base_url = base_url or OLLAMA_BASE_URL
    last_error = None

    for endpoint in ENDPOINTS:
        url = _format_url(base_url, endpoint)
        payload = _build_payload(prompt, model, endpoint, stream)

        try:
            resp = requests.post(url, json=payload, timeout=30, stream=True)
            resp.raise_for_status()
            return _parse_response(resp, stream)
        except requests.exceptions.RequestException as exc:
            last_error = (url, exc)
            continue

    if last_error is None:
        raise RuntimeError("Failed to contact Ollama server: no endpoints attempted")

    url, exc = last_error
    error_message = f"Cannot connect to LLM server at {base_url}. Please check OLLAMA_BASE_URL or the Ollama server status."
    if isinstance(exc, (requests.exceptions.ConnectionError, requests.exceptions.Timeout)):
        raise RuntimeError(error_message) from exc
    raise RuntimeError(f"Failed to contact Ollama server at {url}: {exc}") from exc


def list_models(base_url: str | None = None) -> Dict[str, Any]:
    try:
        import requests
    except ImportError:
        raise RuntimeError("The 'requests' library is required. Install it with: pip install requests")

    base_url = base_url or OLLAMA_BASE_URL
    endpoints = ["/models", "/api/models", "/models/list", "/v1/models"]
    results: Dict[str, Any] = {}

    for endpoint in endpoints:
        url = _format_url(base_url, endpoint)
        try:
            r = requests.get(url, timeout=5)
            try:
                results[url] = r.json()
            except Exception:
                results[url] = r.text
        except requests.RequestException as exc:
            results[url] = str(exc)

    return results
