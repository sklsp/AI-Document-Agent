#!/usr/bin/env python
"""Test which Ollama endpoints are available."""

import requests
from app.core.config import settings

base_url = settings.ollama_base_url.rstrip("/")

print(f"Testing Ollama endpoints at: {base_url}\n")

# Test different endpoints
endpoints = [
    ("GET", "/"),
    ("GET", "/api"),
    ("GET", "/api/tags"),
    ("POST", "/api/generate", {"model": "llama3.2", "prompt": "test"}),
    ("POST", "/api/chat", {"model": "llama3.2", "messages": [{"role": "user", "content": "test"}]}),
    ("GET", "/api/show", {"name": "llama3.2"}),
    ("POST", "/api/pull", {"name": "llama3.2"}),
]

for method, endpoint, *data in endpoints:
    url = f"{base_url}{endpoint}"
    json_data = data[0] if data else None
    
    try:
        response = requests.request(method=method, url=url, json=json_data, timeout=5)
        status = response.status_code
        print(f"{method:6} {endpoint:20} -> {status}")
        if status < 300:
            try:
                body = response.json()
                print(f"       {str(body)[:80]}")
            except:
                print(f"       {response.text[:80]}")
    except Exception as e:
        print(f"{method:6} {endpoint:20} -> ERROR: {str(e)[:60]}")

print("\n" + "=" * 70)
print("Checking server info...")
try:
    response = requests.get(f"{base_url}/", timeout=5)
    print(f"Root status: {response.status_code}")
    print(f"Root response: {response.text[:200]}")
except Exception as e:
    print(f"Root error: {e}")
