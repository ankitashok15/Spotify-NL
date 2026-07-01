from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field
from qdrant_client.http import models as qmodels


class SearchFilters(BaseModel):
    rating_min: int | None = Field(default=None, ge=1, le=5)
    rating_max: int | None = Field(default=None, ge=1, le=5)
    subscription_type: str | None = None
    device_type: str | None = None
    is_discovery_related: bool | None = None
    date_from: datetime | None = None
    date_to: datetime | None = None
    primary_issue: str | None = None


class SearchRequest(BaseModel):
    query: str = Field(min_length=1)
    filters: SearchFilters | None = None
    top_k: int = Field(default=20, ge=1, le=100)


class SearchHit(BaseModel):
    review_id: str
    score: float
    rating: int | None = None
    device_type: str | None = None
    subscription_type: str | None = None
    primary_issue: str | None = None
    is_discovery_related: bool | None = None
    review_created_at: datetime | None = None
    thumbs_up: int | None = None
    text_en: str | None = None
    external_review_id: str | None = None


class SearchResponse(BaseModel):
    query: str
    top_k: int
    took_ms: float
    results: list[SearchHit]


def build_qdrant_filter(filters: SearchFilters | None) -> qmodels.Filter | None:
    if filters is None:
        return None

    must: list[qmodels.Condition] = []

    if filters.rating_min is not None:
        must.append(
            qmodels.FieldCondition(
                key="rating",
                range=qmodels.Range(gte=filters.rating_min),
            )
        )
    if filters.rating_max is not None:
        must.append(
            qmodels.FieldCondition(
                key="rating",
                range=qmodels.Range(lte=filters.rating_max),
            )
        )
    if filters.subscription_type:
        must.append(
            qmodels.FieldCondition(
                key="subscription_type",
                match=qmodels.MatchValue(value=filters.subscription_type),
            )
        )
    if filters.device_type:
        must.append(
            qmodels.FieldCondition(
                key="device_type",
                match=qmodels.MatchValue(value=filters.device_type),
            )
        )
    if filters.is_discovery_related is not None:
        must.append(
            qmodels.FieldCondition(
                key="is_discovery_related",
                match=qmodels.MatchValue(value=filters.is_discovery_related),
            )
        )
    if filters.primary_issue:
        must.append(
            qmodels.FieldCondition(
                key="primary_issue",
                match=qmodels.MatchValue(value=filters.primary_issue),
            )
        )
    if filters.date_from:
        must.append(
            qmodels.FieldCondition(
                key="review_created_at",
                range=qmodels.DatetimeRange(gte=filters.date_from),
            )
        )
    if filters.date_to:
        must.append(
            qmodels.FieldCondition(
                key="review_created_at",
                range=qmodels.DatetimeRange(lte=filters.date_to),
            )
        )

    return qmodels.Filter(must=must) if must else None
