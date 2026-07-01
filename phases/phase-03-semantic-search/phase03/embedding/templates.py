from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class ReviewEmbedInput:
    review_id: str
    text_en: str
    rating: int | None = None
    primary_issue: str | None = None
    secondary_issues: list[str] | None = None
    mentioned_features: list[str] | None = None


def build_embedding_text(data: ReviewEmbedInput) -> str:
    secondary = ", ".join(data.secondary_issues or []) or "none"
    features = ", ".join(data.mentioned_features or []) or "none"
    rating = data.rating if data.rating is not None else "unknown"
    issue = data.primary_issue or "none"
    return (
        f"Review: {data.text_en.strip()}\n"
        f"Rating: {rating}/5\n"
        f"Issues: {issue}, {secondary}\n"
        f"Features: {features}"
    )


def build_search_payload(
    *,
    review_id: str,
    rating: int | None,
    device_type: str | None,
    subscription_type: str | None,
    primary_issue: str | None,
    is_discovery_related: bool,
    review_created_at: datetime | None,
    thumbs_up: int,
    embedding_model_version: str,
    text_en: str,
    external_review_id: str | None = None,
) -> dict:
    return {
        "document_id": review_id,
        "external_review_id": external_review_id,
        "rating": rating,
        "device_type": device_type,
        "subscription_type": subscription_type or "unknown",
        "primary_issue": primary_issue,
        "is_discovery_related": is_discovery_related,
        "review_created_at": review_created_at.isoformat() if review_created_at else None,
        "thumbs_up": thumbs_up,
        "cluster_ids": [],
        "embedding_model_version": embedding_model_version,
        "text_en": (text_en or "")[:2000],
    }
