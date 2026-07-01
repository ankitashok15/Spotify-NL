from abc import ABC, abstractmethod
from typing import Any


class LLMProvider(ABC):
    """Abstract LLM provider for text generation and structured JSON output."""

    @abstractmethod
    def generate_text(self, prompt: str, *, system: str | None = None) -> str:
        """Return plain text completion."""

    @abstractmethod
    def generate_json(self, prompt: str, *, system: str | None = None) -> Any:
        """Return parsed JSON object or array."""
