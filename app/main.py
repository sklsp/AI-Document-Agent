from fastapi import FastAPI

from app.api.routes import router
from app.services.llm_service import LLMService


def create_app(*, service=None) -> FastAPI:
    app = FastAPI(title="Local AI Agent API", version="1.0.0")
    app.state.service = service or LLMService()
    app.include_router(router)
    return app


app = create_app()
