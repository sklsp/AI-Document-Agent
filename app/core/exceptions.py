from fastapi import HTTPException


class OllamaServiceError(Exception):
    """Raised when the Ollama service is unavailable or returns an error."""

    def __init__(self, message: str, *, status_code: int = 502, detail: str | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.detail = detail or message

    def to_http_exception(self) -> HTTPException:
        return HTTPException(status_code=self.status_code, detail=self.detail)
