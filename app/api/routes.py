"""API routes for the AI Document Agent."""

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile

from app.core.exceptions import OllamaServiceError
from app.models.schemas import (
    ChatMessage,
    ChatRequest,
    ChatResponse,
    DocumentResponse,
    DocumentsListResponse,
    HealthResponse,
    ModelsResponse,
    PromptCreate,
    PromptListResponse,
    PromptResponse,
    PromptUpdate,
    SessionHistoryResponse,
)
from app.services.document_service import DocumentService
from app.services.llm_service import LLMService
from app.services.memory_service import MemoryService
from app.services.prompt_service import PromptService

router = APIRouter()


# ============================================
# DEPENDENCY INJECTION
# ============================================


def get_llm_service(request: Request) -> LLMService:
    """Get LLM service from app state."""
    return request.app.state.llm_service


def get_memory_service(request: Request) -> MemoryService:
    """Get memory service from app state."""
    return request.app.state.memory_service


def get_document_service(request: Request) -> DocumentService:
    """Get document service from app state."""
    return request.app.state.document_service


def get_prompt_service(request: Request) -> PromptService:
    """Get prompt service from app state."""
    return request.app.state.prompt_service


# ============================================
# HEALTH & STATUS ENDPOINTS
# ============================================


@router.get("/health", response_model=HealthResponse)
def health(service: LLMService = Depends(get_llm_service)) -> HealthResponse:
    """Check service health and Ollama connectivity."""
    try:
        payload = service.health_check()
    except OllamaServiceError as exc:
        raise exc.to_http_exception() from exc
    return HealthResponse(**payload)


@router.get("/models", response_model=ModelsResponse)
def list_models(service: LLMService = Depends(get_llm_service)) -> ModelsResponse:
    """List available Ollama models."""
    try:
        model_names = service.list_models()
    except OllamaServiceError as exc:
        raise exc.to_http_exception() from exc
    return ModelsResponse(models=model_names)


# ============================================
# CHAT ENDPOINTS
# ============================================


@router.post("/chat", response_model=ChatResponse)
def chat(
    request: ChatRequest,
    llm_service: LLMService = Depends(get_llm_service),
    memory_service: MemoryService = Depends(get_memory_service),
    document_service: DocumentService = Depends(get_document_service),
    prompt_service: PromptService = Depends(get_prompt_service),
) -> ChatResponse:
    """
    Enhanced chat endpoint with:
    - Session-based conversation history
    - Document context retrieval
    - Prompt template integration
    """
    try:
        session_id = request.session_id
        user_prompt = request.prompt
        model = request.model

        # 1. Retrieve chat history
        history_text = memory_service.format_history_for_prompt(session_id)

        # 2. Retrieve relevant document context
        doc_context = document_service.get_relevant_context(user_prompt)

        # 3. Get system prompt (use default if not specified)
        default_prompt = prompt_service.get_prompt_by_name("default")
        system_prompt = default_prompt["content"] if default_prompt else "You are a helpful AI assistant."

        # 4. Build the full prompt
        full_prompt = _build_system_prompt(
            system_prompt=system_prompt,
            doc_context=doc_context,
            history=history_text,
            user_prompt=user_prompt,
        )

        # 5. Add user message to history
        memory_service.add_message(session_id, "user", user_prompt)

        # 6. Get response from LLM
        response_text = llm_service.chat(full_prompt, model)

        # 7. Add assistant response to history
        memory_service.add_message(session_id, "assistant", response_text)

        return ChatResponse(response=response_text, session_id=session_id)

    except OllamaServiceError as exc:
        raise exc.to_http_exception() from exc


@router.get("/sessions/{session_id}/history", response_model=SessionHistoryResponse)
def get_session_history(
    session_id: str,
    memory_service: MemoryService = Depends(get_memory_service),
) -> SessionHistoryResponse:
    """Get conversation history for a specific session."""
    history = memory_service.get_history(session_id)
    messages = [ChatMessage(**msg) for msg in history]
    return SessionHistoryResponse(
        session_id=session_id,
        messages=messages,
        message_count=len(messages),
    )


@router.delete("/sessions/{session_id}/history")
def clear_session_history(
    session_id: str,
    memory_service: MemoryService = Depends(get_memory_service),
) -> dict:
    """Clear conversation history for a specific session."""
    memory_service.clear_history(session_id)
    return {"message": f"History cleared for session {session_id}"}


# ============================================
# DOCUMENT ENDPOINTS
# ============================================


@router.post("/documents/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    document_service: DocumentService = Depends(get_document_service),
) -> DocumentResponse:
    """Upload and store a document (.txt files)."""
    try:
        # Validate file type
        if not file.filename.endswith(".txt"):
            raise HTTPException(status_code=400, detail="Only .txt files are supported")

        # Read file content
        content = await file.read()
        text_content = content.decode("utf-8")

        # Store document
        doc_id = document_service.store_document(text_content, source=file.filename)

        return DocumentResponse(id=doc_id, source=file.filename)

    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="File must be valid UTF-8 text")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading document: {str(e)}")


@router.get("/documents", response_model=DocumentsListResponse)
def list_documents(
    document_service: DocumentService = Depends(get_document_service),
) -> DocumentsListResponse:
    """List all stored documents."""
    docs = document_service.get_all_documents()
    doc_list = [{"id": doc["id"], "source": doc["source"]} for doc in docs]
    return DocumentsListResponse(documents=doc_list, count=len(doc_list))


@router.delete("/documents/{doc_id}")
def delete_document(
    doc_id: str,
    document_service: DocumentService = Depends(get_document_service),
) -> dict:
    """Delete a stored document."""
    if document_service.delete_document(doc_id):
        return {"message": f"Document {doc_id} deleted"}
    raise HTTPException(status_code=404, detail=f"Document {doc_id} not found")


@router.delete("/documents")
def clear_all_documents(
    document_service: DocumentService = Depends(get_document_service),
) -> dict:
    """Clear all stored documents."""
    document_service.clear_all()
    return {"message": "All documents cleared"}


# ============================================
# PROMPT ENDPOINTS
# ============================================


@router.post("/prompts", response_model=PromptResponse)
def create_prompt(
    prompt_create: PromptCreate,
    prompt_service: PromptService = Depends(get_prompt_service),
) -> PromptResponse:
    """Create a new prompt template."""
    prompt_id = prompt_service.create_prompt(prompt_create.name, prompt_create.content)
    prompt = prompt_service.get_prompt(prompt_id)
    if prompt:
        return PromptResponse(**prompt)
    raise HTTPException(status_code=500, detail="Failed to create prompt")


@router.get("/prompts", response_model=PromptListResponse)
def list_prompts(
    prompt_service: PromptService = Depends(get_prompt_service),
) -> PromptListResponse:
    """List all prompt templates."""
    prompts = prompt_service.list_prompts()
    prompt_responses = [PromptResponse(**p) for p in prompts]
    return PromptListResponse(prompts=prompt_responses, count=len(prompt_responses))


@router.get("/prompts/{prompt_id}", response_model=PromptResponse)
def get_prompt(
    prompt_id: str,
    prompt_service: PromptService = Depends(get_prompt_service),
) -> PromptResponse:
    """Get a specific prompt template."""
    prompt = prompt_service.get_prompt(prompt_id)
    if prompt:
        return PromptResponse(**prompt)
    raise HTTPException(status_code=404, detail=f"Prompt {prompt_id} not found")


@router.put("/prompts/{prompt_id}", response_model=PromptResponse)
def update_prompt(
    prompt_id: str,
    prompt_update: PromptUpdate,
    prompt_service: PromptService = Depends(get_prompt_service),
) -> PromptResponse:
    """Update an existing prompt template."""
    if prompt_service.update_prompt(
        prompt_id,
        name=prompt_update.name,
        content=prompt_update.content,
    ):
        prompt = prompt_service.get_prompt(prompt_id)
        if prompt:
            return PromptResponse(**prompt)
    raise HTTPException(status_code=404, detail=f"Prompt {prompt_id} not found")


@router.delete("/prompts/{prompt_id}")
def delete_prompt(
    prompt_id: str,
    prompt_service: PromptService = Depends(get_prompt_service),
) -> dict:
    """Delete a prompt template."""
    if prompt_service.delete_prompt(prompt_id):
        return {"message": f"Prompt {prompt_id} deleted"}
    raise HTTPException(status_code=404, detail=f"Prompt {prompt_id} not found")


# ============================================
# HELPERS
# ============================================


def _build_system_prompt(
    system_prompt: str,
    doc_context: str,
    history: str,
    user_prompt: str,
) -> str:
    """Build the complete system prompt with context.

    Args:
        system_prompt: System-level instructions
        doc_context: Retrieved document context
        history: Chat history
        user_prompt: Current user prompt

    Returns:
        Complete prompt to send to LLM
    """
    parts = [f"SYSTEM:\n{system_prompt}"]

    if doc_context:
        parts.append(f"DOCUMENT CONTEXT:\n{doc_context}")

    if history:
        parts.append(f"CHAT HISTORY:\n{history}")

    parts.append(f"USER:\n{user_prompt}")

    return "\n\n".join(parts)
