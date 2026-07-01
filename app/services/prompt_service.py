"""Prompt service for managing prompt templates."""

from typing import TypedDict


class Prompt(TypedDict):
    """Prompt template structure."""

    id: str
    name: str
    content: str


class PromptService:
    """Manage prompt templates. Easily upgradeable to database storage."""

    def __init__(self) -> None:
        # Structure: {prompt_id: Prompt}
        self._storage: dict[str, Prompt] = {}
        self._prompt_counter = 0
        self._initialize_defaults()

    def _initialize_defaults(self) -> None:
        """Initialize with some default prompts."""
        self.create_prompt(
            "default",
            "You are a helpful AI assistant. Answer the user's question clearly and concisely.",
        )
        self.create_prompt(
            "code_helper",
            "You are an expert programmer. Help the user with code questions, provide clean examples, and explain concepts clearly.",
        )
        self.create_prompt(
            "document_analyzer",
            "You are a document analysis expert. Analyze the provided documents and answer questions based on their content.",
        )

    def create_prompt(self, name: str, content: str) -> str:
        """Create a new prompt template.

        Args:
            name: Prompt name/identifier
            content: Prompt content/template

        Returns:
            Prompt ID
        """
        prompt_id = f"prompt_{self._prompt_counter}"
        self._prompt_counter += 1

        self._storage[prompt_id] = {
            "id": prompt_id,
            "name": name,
            "content": content,
        }

        return prompt_id

    def get_prompt(self, prompt_id: str) -> Prompt | None:
        """Retrieve a prompt by ID.

        Args:
            prompt_id: Prompt identifier

        Returns:
            Prompt or None if not found
        """
        return self._storage.get(prompt_id)

    def get_prompt_by_name(self, name: str) -> Prompt | None:
        """Retrieve a prompt by name.

        Args:
            name: Prompt name

        Returns:
            Prompt or None if not found
        """
        for prompt in self._storage.values():
            if prompt["name"] == name:
                return prompt
        return None

    def list_prompts(self) -> list[Prompt]:
        """List all prompts.

        Returns:
            List of all prompts
        """
        return list(self._storage.values())

    def update_prompt(self, prompt_id: str, name: str | None = None, content: str | None = None) -> bool:
        """Update an existing prompt.

        Args:
            prompt_id: Prompt identifier
            name: New name (optional)
            content: New content (optional)

        Returns:
            True if updated, False if not found
        """
        if prompt_id not in self._storage:
            return False

        if name is not None:
            self._storage[prompt_id]["name"] = name
        if content is not None:
            self._storage[prompt_id]["content"] = content

        return True

    def delete_prompt(self, prompt_id: str) -> bool:
        """Delete a prompt.

        Args:
            prompt_id: Prompt identifier

        Returns:
            True if deleted, False if not found
        """
        if prompt_id in self._storage:
            del self._storage[prompt_id]
            return True
        return False
