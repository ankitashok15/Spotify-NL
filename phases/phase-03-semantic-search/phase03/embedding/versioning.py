from __future__ import annotations

from phase03.shared.config import settings


def embedding_model_version() -> str:
    """Stable version string stored on each vector."""
    return f"{settings.gemini_embedding_model}@1"


def qdrant_collection_version() -> str:
    return f"{settings.qdrant_collection}:{embedding_model_version()}"
