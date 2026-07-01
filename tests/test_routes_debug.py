#!/usr/bin/env python
"""Debug script to test route registration."""

import traceback
from fastapi import FastAPI
from app.api.routes import router

# Test 1: Router loading
print("=" * 70)
print("TEST 1: Router Loading")
print("=" * 70)
print(f"✓ Router imported: {router}")
print(f"  Router has {len(router.routes)} routes")
print(f"  First few routes:")
for route in router.routes[:5]:
    if hasattr(route, 'path'):
        print(f"    - {route.path}")

# Test 2: App creation and router inclusion
print("\n" + "=" * 70)
print("TEST 2: App Creation and Router Inclusion")
print("=" * 70)

try:
    app = FastAPI()
    print(f"✓ FastAPI app created")
    print(f"  Before include_router: {len(app.routes)} routes")
    
    app.include_router(router)
    print(f"✓ Router included")
    print(f"  After include_router: {len(app.routes)} routes")
    
    # List all routes
    print(f"\n  All routes in app:")
    for route in app.routes:
        if hasattr(route, 'path'):
            methods = getattr(route, 'methods', set())
            print(f"    - {route.path} {methods}")

except Exception as e:
    print(f"✗ Error: {e}")
    traceback.print_exc()

# Test 3: Check main.py app
print("\n" + "=" * 70)
print("TEST 3: Main App from main.py")
print("=" * 70)

try:
    from app.main import app as main_app
    print(f"✓ App from main.py loaded")
    print(f"  Total routes: {len(main_app.routes)}")
    
    api_routes = [r for r in main_app.routes if hasattr(r, 'path') and not r.path.startswith('/openapi') and not r.path.startswith('/docs')]
    print(f"  API routes (excluding docs): {len(api_routes)}")
    
    print(f"\n  API Routes:")
    for route in api_routes:
        path = route.path
        methods = getattr(route, 'methods', {'N/A'})
        print(f"    - {path} {methods}")
        
    # Check for /chat specifically
    chat_routes = [r for r in main_app.routes if hasattr(r, 'path') and '/chat' in r.path]
    print(f"\n  /chat routes found: {len(chat_routes)}")
    for route in chat_routes:
        print(f"    - {route.path} {getattr(route, 'methods', 'N/A')}")

except Exception as e:
    print(f"✗ Error: {e}")
    traceback.print_exc()

print("\n" + "=" * 70)
