#!/usr/bin/env python
"""Debug script to test route registration - detailed version."""

from app.main import app

print("=" * 70)
print("ROUTE ANALYSIS")
print("=" * 70)
print(f"\nTotal routes in app: {len(app.routes)}\n")

print("Route Details:")
for i, route in enumerate(app.routes):
    route_type = type(route).__name__
    path = getattr(route, 'path', 'N/A')
    methods = getattr(route, 'methods', set()) or set()
    methods_str = ", ".join(sorted(methods)) if methods else "N/A"
    
    print(f"{i:2}. [{route_type:15}] {path:30} {methods_str}")

print("\n" + "=" * 70)
print("SEARCHING FOR /chat")
print("=" * 70 + "\n")

found_chat = False
for route in app.routes:
    if hasattr(route, 'path') and 'chat' in route.path.lower():
        methods = getattr(route, 'methods', set())
        print(f"✓ FOUND: {route.path} - Methods: {methods}")
        found_chat = True

if not found_chat:
    print("✗ /chat route NOT FOUND in app.routes")
    print("\nThis means the router.include_router() call is not working properly.")
    print("Possible causes:")
    print("  1. Syntax error in routes.py preventing route definitions")
    print("  2. Router not being included in the right order")
    print("  3. Issue with service dependencies")

print("\n" + "=" * 70)

