from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from pydantic import BaseModel, Field


class RouterFilters(BaseModel):
    rating_min: int | None = Field(default=None, ge=1, le=5)
    rating_max: int | None = Field(default=None, ge=1, le=5)
    subscription_type: str | None = None
    device_type: str | None = None
    is_discovery_related: bool | None = None
    primary_issue: str | None = None
    date_from: datetime | None = None
    date_to: datetime | None = None
    mentioned_feature: str | None = None


class RouterResult(BaseModel):
    intent: str = "general_question"
    search_query: str
    filters: RouterFilters = Field(default_factory=RouterFilters)
    requires_aggregation: bool = False


@dataclass
class EvidenceDocument:
    """Single review used as RAG evidence with citation index."""

    citation_id: int
    review_id: str
    external_review_id: str | None
    rating: int | None
    thumbs_up: int
    device_type: str | None
    subscription_type: str | None
    primary_issue: str | None
    emotions: list[str] = field(default_factory=list)
    pain_points: list[str] = field(default_factory=list)
    review_created_at: datetime | None = None
    text_en: str = ""
    dense_score: float = 0.0
    sparse_score: float = 0.0
    rrf_score: float = 0.0
    rerank_score: float = 0.0

    @property
    def excerpt(self) -> str:
        text = self.text_en.strip()
        return text[:400] + ("..." if len(text) > 400 else "")
