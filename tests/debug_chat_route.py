#!/usr/bin/env python
"""Debug /chat route registration specifically."""

import traceback

print("=" * 70)
print("DEBUGGING /chat ROUTE")
print("=" * 70)

# Step 1: Import schemas
print("\n1. Testing schema imports...")
try:
    from app.models.schemas import ChatRequest, ChatResponse
    print("   [OK] Schemas imported successfully")
    print(f"   - ChatRequest fields: {ChatRequest.model_fields.keys()}")
    print(f"   - ChatResponse fields: {ChatResponse.model_fields.keys()}")
except Exception as e:
    print(f"   [ERROR] Error importing schemas: {e}")
    traceback.print_exc()

# Step 2: Import services
print("\n2. Testing service imports...")
try:
    from app.services.llm_service import LLMService
    from app.services.memory_service import MemoryService
    from app.services.document_service import DocumentService
    from app.services.prompt_service import PromptService
    print("   [OK] Services imported successfully")
except Exception as e:
    print(f"   [ERROR] Error importing services: {e}")
    traceback.print_exc()

# Step 3: Try to import the router
print("\n3. Testing router import...")
try:
    from app.api import routes
    router = routes.router
    print(f"   [OK] Router imported: {router}")
    print(f"   - Total routes in router: {len(router.routes)}")
    
    # Find /chat route
    chat_route = None
    for route in router.routes:
        if hasattr(route, 'path') and route.path == '/chat':
            chat_route = route
            break
    
    if chat_route:
        print(f"   [OK] /chat route FOUND in router")
        print(f"      Path: {chat_route.path}")
        print(f"      Methods: {getattr(chat_route, 'methods', 'N/A')}")
        print(f"      Endpoint: {getattr(chat_route, 'endpoint', 'N/A')}")
    else:
        print(f"   [ERROR] /chat route NOT found in router")
        print("\n   Routes in router:")
        for route in router.routes:
            if hasattr(route, 'path'):
                print(f"      - {route.path}")

except Exception as e:
    print(f"   [ERROR] Error: {e}")
    traceback.print_exc()

# Step 4: Try the full app
print("\n4. Testing full app...")
try:
    from app.main import app
    print(f"   [OK] App created: {app}")
    
    # Try to find /chat
    chat_found = False
    for route in app.routes:
        if hasattr(route, 'path') and route.path == '/chat':
            chat_found = True
            print(f"   [OK] /chat found in app.routes")
            break
    
    if not chat_found:
        print(f"   [ERROR] /chat NOT found in app.routes")
        print(f"   - Total routes: {len(app.routes)}")

except Exception as e:
    print(f"   [ERROR] Error: {e}")
    traceback.print_exc()

# Step 5: Try to manually test the endpoint
print("\n5. Testing endpoint with TestClient...")
try:
    from fastapi.testclient import TestClient
    from app.main import app
    
    client = TestClient(app)
    
    # First, try /health which we know works
    resp = client.get("/health")
    print(f"   [OK] /health returns: {resp.status_code}")
    
    # Now try /chat
    resp = client.post(
        "/chat",
        json={
            "prompt": "test",
            "session_id": "test",
            "model": "test"
        }
    )
    print(f"   - /chat returns: {resp.status_code}")
    if resp.status_code == 404:
        print(f"      Response: {resp.json()}")
    elif resp.status_code in [400, 422, 500]:
        print(f"      Response: {resp.text}")
    else:
        print(f"      Response: {resp.json()}")

except Exception as e:
    print(f"   [ERROR] Error: {e}")
    traceback.print_exc()

print("\n" + "=" * 70)
