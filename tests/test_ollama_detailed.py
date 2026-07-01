#!/usr/bin/env python
"""Check Ollama models and try to use them."""

import requests
import json
from app.core.config import settings

base_url = settings.ollama_base_url.rstrip("/")

print(f"Ollama Base URL: {base_url}\n")

# Get available models
print("=" * 70)
print("STEP 1: List available models...")
response = requests.get(f"{base_url}/api/tags", timeout=5)
print(f"Status: {response.status_code}")
models_data = response.json()
print(json.dumps(models_data, indent=2))

# Try to get model info
if models_data.get("models"):
    model_name = models_data["models"][0]["name"]
    print(f"\n" + "=" * 70)
    print(f"STEP 2: Get details for model: {model_name}")
    response = requests.get(f"{base_url}/api/show", params={"name": model_name}, timeout=5)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:500]}")

# Try POST /api/tags
print(f"\n" + "=" * 70)
print("STEP 3: POST to /api/tags (try different method)...")
response = requests.post(f"{base_url}/api/tags", timeout=5)
print(f"Status: {response.status_code}")
print(f"Response: {response.text[:200]}")

# Check Ollama info/version
print(f"\n" + "=" * 70)
print("STEP 4: Check server endpoints...")
endpoints_to_check = [
    "GET /api/version",
    "GET /api/models",
    "POST /v1/chat/completions",
    "GET /v1/models",
]

for endpoint_str in endpoints_to_check:
    method, path = endpoint_str.split()
    try:
        if method == "GET":
            response = requests.get(f"{base_url}{path}", timeout=5)
        else:
            response = requests.post(f"{base_url}{path}", json={}, timeout=5)
        print(f"{method:6} {path:25} -> {response.status_code}")
        if response.status_code < 400:
            print(f"       {response.text[:80]}")
    except Exception as e:
        print(f"{method:6} {path:25} -> ERROR: {str(e)[:60]}")
