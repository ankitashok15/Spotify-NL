from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass

from phase03.embedding.provider import GeminiEmbeddingProvider
from phase03.embedding.templates import ReviewEmbedInput, build_embedding_text, build_search_payload
from phase03.embedding.versioning import embedding_model_version

logger = logging.getLogger(__name__)


@dataclass
class EmbeddedReview:
    review_id: uuid.UUID
    vector: list[float]
    payload: dict
    embedding_text: str


class ReviewEmbedder:
    def __init__(self, provider: GeminiEmbeddingProvider | None = None):
        self.provider = provider or GeminiEmbeddingProvider()

    def embed_inputs(self, inputs: list[ReviewEmbedInput], metadata: list[dict]) -> list[EmbeddedReview]:
        if not inputs:
            return []
        if len(inputs) != len(metadata):
            raise ValueError("inputs and metadata length mismatch")

        texts = [build_embedding_text(item) for item in inputs]
        vectors = self.provider.embed_batch(texts, task_type="retrieval_document")
        model_version = embedding_model_version()

        embedded: list[EmbeddedReview] = []
        for item, meta, vector, text in zip(inputs, metadata, vectors, texts, strict=True):
            review_id = uuid.UUID(item.review_id)
            payload = build_search_payload(
                review_id=item.review_id,
                rating=meta.get("rating"),
                device_type=meta.get("device_type"),
                subscription_type=meta.get("subscription_type"),
                primary_issue=item.primary_issue or meta.get("primary_issue"),
                is_discovery_related=bool(meta.get("is_discovery_related", False)),
                review_created_at=meta.get("review_created_at"),
                thumbs_up=int(meta.get("thumbs_up") or 0),
                embedding_model_version=model_version,
                text_en=item.text_en,
                external_review_id=meta.get("external_review_id"),
            )
            embedded.append(
                EmbeddedReview(
                    review_id=review_id,
                    vector=vector,
                    payload=payload,
                    embedding_text=text,
                )
            )
        return embedded

    def embed_query(self, query: str) -> list[float]:
        return self.provider.embed_one(query, task_type="retrieval_query")
