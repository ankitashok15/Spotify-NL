from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class AgentTool(ABC):
    name: str
    description: str

    @abstractmethod
    def run(self, args: dict) -> Any:
        pass

    def summary(self, result: Any) -> str:
        if isinstance(result, list):
            return f"{len(result)} items"
        if isinstance(result, dict):
            keys = ", ".join(list(result.keys())[:5])
            return f"dict({keys})"
        return str(result)[:200]
