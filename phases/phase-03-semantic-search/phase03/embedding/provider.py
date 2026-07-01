from __future__ import annotations

import logging
import time
from typing import Literal

import google.generativeai as genai

from phase03.shared.config import settings

logger = logging.getLogger(__name__)

# text-embedding-004 = 768d (legacy); gemini-embedding-001 = 3072d (current Google AI Studio)
EMBEDDING_DIMENSION = 3072
DEFAULT_EMBEDDING_MODEL = "gemini-embedding-001"

TaskType = Literal["retrieval_document", "retrieval_query", "semantic_similarity"]


class GeminiEmbeddingProvider:
    def __init__(
        self,
        api_key: str | None = None,
        model_name: str | None = None,
    ) -> None:
        key = api_key or settings.gemini_api_key
        if not key:
            raise ValueError("GEMINI_API_KEY is not set in .env")
        self.model_name = model_name or settings.gemini_embedding_model
        if self.model_name == "text-embedding-004":
            logger.warning(
                "text-embedding-004 is unavailable on many API keys; using gemini-embedding-001"
            )
            self.model_name = DEFAULT_EMBEDDING_MODEL
        self._model = (
            self.model_name if self.model_name.startswith("models/") else f"models/{self.model_name}"
        )
        genai.configure(api_key=key)

    def embed_one(self, text: str, *, task_type: TaskType = "retrieval_document") -> list[float]:
        return self.embed_batch([text], task_type=task_type)[0]

    def embed_batch(
        self,
        texts: list[str],
        *,
        task_type: TaskType = "retrieval_document",
        max_retries: int | None = None,
    ) -> list[list[float]]:
        if not texts:
            return []

        retries = max_retries if max_retries is not None else settings.embed_max_retries
        last_error: Exception | None = None

        for attempt in range(1, retries + 1):
            try:
                result = genai.embed_content(
                    model=self._model,
                    content=texts,
                    task_type=task_type,
                )
                embeddings = result.get("embedding") if isinstance(result, dict) else None
                if embeddings is None:
                    embeddings = getattr(result, "embedding", None)
                if embeddings is None:
                    raise ValueError("Unexpected embedding response shape")

                # Single text returns flat vector; batch returns list of vectors
                if texts and isinstance(embeddings[0], (int, float)):
                    return [embeddings]
                return embeddings
            except Exception as exc:
                last_error = exc
                delay = settings.embed_rate_limit_seconds * attempt
                logger.warning(
                    "Embedding failed (attempt %s/%s): %s — retry in %.1fs",
                    attempt,
                    retries,
                    exc,
                    delay,
                )
                time.sleep(delay)

        raise RuntimeError(f"Embedding failed after {retries} retries") from last_error
