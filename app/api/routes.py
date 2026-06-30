from fastapi import APIRouter, Depends, Request

from app.core.exceptions import OllamaServiceError
from app.models.schemas import ChatRequest, ChatResponse, HealthResponse, ModelsResponse
from app.services.llm_service import LLMService

router = APIRouter()


def get_service(request: Request) -> LLMService:
    return request.app.state.service


@router.get("/health", response_model=HealthResponse)
def health(service: LLMService = Depends(get_service)) -> HealthResponse:
    try:
        payload = service.health_check()
    except OllamaServiceError as exc:
        raise exc.to_http_exception() from exc
    return HealthResponse(**payload)


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest, service: LLMService = Depends(get_service)) -> ChatResponse:
    try:
        response_text = service.chat(request.prompt, request.model)
    except OllamaServiceError as exc:
        raise exc.to_http_exception() from exc
    return ChatResponse(response=response_text, model=request.model or "llama3.2")


@router.get("/models", response_model=ModelsResponse)
def models(service: LLMService = Depends(get_service)) -> ModelsResponse:
    try:
        model_names = service.list_models()
    except OllamaServiceError as exc:
        raise exc.to_http_exception() from exc
    return ModelsResponse(models=model_names)
