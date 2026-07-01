from pathlib import Path

from fastapi.responses import FileResponse
from fastapi import FastAPI

from app.api.routes import router
from app.services.llm_service import LLMService


def create_app(*, service=None) -> FastAPI:
    app = FastAPI(title="Local AI Agent API", version="1.0.0")

    app.state.service = service or LLMService()

    # API routes
    app.include_router(router)

    # Frontend - serve index.html at root
    frontend_path = Path(__file__).parent / "frontend" / "index.html"

    @app.get("/")
    async def root():
        return FileResponse(str(frontend_path))

    return app


app = create_app()