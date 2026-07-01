from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from app.api.routes import router
from app.services.document_service import DocumentService
from app.services.llm_service import LLMService
from app.services.memory_service import MemoryService
from app.services.prompt_service import PromptService


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    Initializes all services (LLM, Memory, Document, Prompt).
    """
    app = FastAPI(
        title="Local AI Agent API",
        version="1.0.0",
        description="Production-ready AI workspace with chat memory, document RAG, and prompt templates",
    )

    # ============ CORS MIDDLEWARE ============
    # Allow frontend to call backend from same origin and across network
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allow all origins (safe for local network)
        allow_credentials=True,
        allow_methods=["*"],  # Allow all HTTP methods
        allow_headers=["*"],  # Allow all headers
    )

    # ============ INITIALIZE SERVICES ============
    app.state.llm_service = LLMService()
    app.state.memory_service = MemoryService()
    app.state.document_service = DocumentService()
    app.state.prompt_service = PromptService()

    # ============ INCLUDE API ROUTES ============
    app.include_router(router)

    # ============ FRONTEND - SERVE AT ROOT ============
    frontend_path = Path(__file__).parent / "frontend" / "index.html"

    @app.get("/", include_in_schema=False)
    async def root():
        """Serve the frontend HTML."""
        return FileResponse(str(frontend_path))

    # ============ DEBUG: LOG ALL REGISTERED ROUTES ============
    @app.on_event("startup")
    async def log_routes():
        """Log all registered routes on startup for debugging."""
        print("\n" + "=" * 70)
        print("🚀 AI WORKSPACE API STARTED")
        print("=" * 70)
        print("\n📋 REGISTERED ENDPOINTS:")
        print("-" * 70)
        
        # Collect all routes
        routes = {}
        for route in app.routes:
            if hasattr(route, "path") and hasattr(route, "methods"):
                path = route.path
                methods = ", ".join(sorted(route.methods - {"HEAD", "OPTIONS"}))
                if path not in routes:
                    routes[path] = []
                routes[path].append(methods)
        
        # Print routes organized by path
        for path in sorted(routes.keys()):
            methods_list = routes[path]
            for methods in methods_list:
                print(f"  {methods:10} {path}")
        
        print("-" * 70)
        print("\n✅ CRITICAL ROUTES:")
        print(f"  POST    /chat              ← Frontend calls this")
        print(f"  POST    /documents/upload  ← File uploads")
        print(f"  GET     /prompts           ← Load prompt templates")
        print(f"  GET     /documents         ← Load documents")
        print(f"  GET     /health            ← Health check")
        print("-" * 70)
        
        # Verify /chat endpoint exists
        chat_route_found = any(
            hasattr(r, "path") and r.path == "/chat" and "POST" in getattr(r, "methods", set())
            for r in app.routes
        )
        
        if chat_route_found:
            print("\n✓ /chat endpoint is REGISTERED")
        else:
            print("\n✗ WARNING: /chat endpoint NOT FOUND!")
        
        print("\n🌐 Frontend should call:")
        print("   POST http://192.168.178.69:8000/chat")
        print("   with JSON: {\"prompt\": \"...\", \"session_id\": \"...\", \"model\": \"...\"}")
        print("\n" + "=" * 70 + "\n")

    return app


app = create_app()
