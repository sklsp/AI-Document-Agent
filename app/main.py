from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from app.api.routes import router
from app.services.document_service import DocumentService
from app.services.llm_service import LLMService
from app.services.memory_service import MemoryService
from app.services.prompt_service import PromptService
from app.services.rag.service import RAGService


def _iter_api_routes(routes):
    """Yield API routes, including those nested in included routers (FastAPI 0.138+)."""
    for route in routes:
        if type(route).__name__ == "_IncludedRouter":
            yield from _iter_api_routes(route.original_router.routes)
        elif hasattr(route, "routes"):
            yield from _iter_api_routes(route.routes)
        elif hasattr(route, "path") and hasattr(route, "methods"):
            yield route


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
    app.state.rag_service = RAGService()

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
        print("AI WORKSPACE API STARTED")
        print("=" * 70)
        print("\nREGISTERED ENDPOINTS:")
        print("-" * 70)
        
        # Collect all routes (including nested included routers)
        routes = {}
        for route in _iter_api_routes(app.routes):
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
        print("\nCRITICAL ROUTES:")
        print("  POST    /chat              <- Frontend calls this")
        print("  POST    /documents/upload  <- File uploads")
        print("  GET     /prompts           <- Load prompt templates")
        print("  GET     /documents         <- Load documents")
        print("  GET     /health            <- Health check")
        print("-" * 70)
        
        # Verify /chat endpoint exists
        chat_route_found = any(
            r.path == "/chat" and "POST" in r.methods
            for r in _iter_api_routes(app.routes)
        )
        
        if chat_route_found:
            print("\n[OK] /chat endpoint is REGISTERED")
        else:
            print("\n[WARN] /chat endpoint NOT FOUND!")
        
        print("\nFrontend API base:")
        print("   Same origin as this server (localhost, LAN, or Cloudflare tunnel)")
        print("   POST /chat with JSON: {\"prompt\": \"...\", \"session_id\": \"...\", \"model\": \"...\"}")
        print("\n" + "=" * 70 + "\n")

    return app


app = create_app()
