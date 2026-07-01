#!/usr/bin/env python
"""Test /chat endpoint directly without running server."""

from fastapi.testclient import TestClient
from app.main import app

print("=" * 70)
print("TESTING /chat ENDPOINT")
print("=" * 70)

client = TestClient(app)

# Test 1: Check if /chat endpoint exists
print("\n1. Testing POST /chat")
print("-" * 70)

response = client.post(
    "/chat",
    json={
        "prompt": "Hello",
        "session_id": "test_session",
        "model": "llama3.2"
    }
)

print(f"Status Code: {response.status_code}")
print(f"Response Headers: {dict(response.headers)}")

if response.status_code == 200:
    print("✓ /chat endpoint is WORKING")
    print(f"Response: {response.json()}")
elif response.status_code == 404:
    print("✗ /chat endpoint returns 404 (NOT FOUND)")
else:
    print(f"✗ /chat endpoint error: {response.status_code}")
    print(f"Response: {response.text}")

# Test 2: Check other endpoints
print("\n2. Testing /documents")
print("-" * 70)

response = client.get("/documents")
print(f"Status Code: {response.status_code}")
if response.status_code == 200:
    print("✓ /documents endpoint is WORKING")
else:
    print(f"✗ /documents endpoint error: {response.status_code}")

# Test 3: Check /prompts
print("\n3. Testing /prompts")
print("-" * 70)

response = client.get("/prompts")
print(f"Status Code: {response.status_code}")
if response.status_code == 200:
    print("✓ /prompts endpoint is WORKING")
else:
    print(f"✗ /prompts endpoint error: {response.status_code}")

# Test 4: Check health
print("\n4. Testing /health")
print("-" * 70)

response = client.get("/health")
print(f"Status Code: {response.status_code}")
if response.status_code == 200:
    print("✓ /health endpoint is WORKING")
else:
    print(f"✗ /health endpoint error: {response.status_code}")

print("\n" + "=" * 70)
