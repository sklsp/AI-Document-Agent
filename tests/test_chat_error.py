#!/usr/bin/env python
"""Test /chat with full error details."""

from fastapi.testclient import TestClient
from app.main import app

print("Testing /chat endpoint with detailed output...\n")

client = TestClient(app)

response = client.post(
    "/chat",
    json={
        "prompt": "test",
        "session_id": "test",
        "model": "llama3.2"
    }
)

print(f"Status Code: {response.status_code}")
print(f"Headers: {dict(response.headers)}")
print(f"Full Response:")
print(f"  Text: {response.text}")
try:
    print(f"  JSON: {response.json()}")
except:
    print(f"  (Not valid JSON)")

# Also test /health to compare
print("\n\nComparing with /health endpoint...\n")

response = client.get("/health")
print(f"Status Code: {response.status_code}")
print(f"Response: {response.json()}")
