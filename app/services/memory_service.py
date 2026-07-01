"""Memory service for managing chat history per session."""

from datetime import datetime
from typing import TypedDict


class Message(TypedDict):
    """Chat message structure."""

    role: str  # "user" or "assistant"
    content: str
    timestamp: str  # ISO format


class MemoryService:
    """In-memory chat history storage. Easily upgradeable to SQLite."""

    def __init__(self) -> None:
        # Structure: {session_id: [messages]}
        self._storage: dict[str, list[Message]] = {}

    def add_message(self, session_id: str, role: str, content: str) -> Message:
        """Add a message to session history.

        Args:
            session_id: Unique session identifier
            role: "user" or "assistant"
            content: Message content

        Returns:
            The created message
        """
        if session_id not in self._storage:
            self._storage[session_id] = []

        message: Message = {
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat(),
        }

        self._storage[session_id].append(message)
        return message

    def get_history(self, session_id: str) -> list[Message]:
        """Get all messages for a session.

        Args:
            session_id: Unique session identifier

        Returns:
            List of messages in chronological order
        """
        return self._storage.get(session_id, [])

    def clear_history(self, session_id: str) -> None:
        """Clear all messages for a session.

        Args:
            session_id: Unique session identifier
        """
        if session_id in self._storage:
            del self._storage[session_id]

    def get_session_ids(self) -> list[str]:
        """Get all session IDs.

        Returns:
            List of active session IDs
        """
        return list(self._storage.keys())

    def format_history_for_prompt(self, session_id: str) -> str:
        """Format chat history as a string for inclusion in prompts.

        Args:
            session_id: Unique session identifier

        Returns:
            Formatted history string
        """
        history = self.get_history(session_id)
        if not history:
            return ""

        lines = []
        for msg in history:
            role_label = "USER" if msg["role"] == "user" else "ASSISTANT"
            lines.append(f"{role_label}: {msg['content']}")

        return "\n".join(lines)
