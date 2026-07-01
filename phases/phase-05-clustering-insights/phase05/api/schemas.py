from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class ClusterSummary(BaseModel):
    id: UUID
    cluster_key: str
    label: str
    description: str | None = None
    taxonomy_theme_id: str | None = None
    member_count: int
    avg_rating: float | None = None
    avg_thumbs_up: float | None = None
    top_subscription_types: list[str] | None = None
    top_device_types: list[str] | None = None
    representative_review_ids: list[str] | None = None
    trend_30d: float | None = None

    model_config = {"from_attributes": True}


class ClusterListResponse(BaseModel):
    items: list[ClusterSummary]
    total: int


class ClusterDetailResponse(ClusterSummary):
    member_review_ids: list[str] = Field(default_factory=list)


class InsightItem(BaseModel):
    id: UUID
    insight_type: str
    title: str
    summary: str
    confidence: float | None = None
    evidence_document_ids: list[str] | None = None
    affected_personas: list[str] | None = None
    payload: dict | None = None
    generated_at: datetime

    model_config = {"from_attributes": True}


class InsightListResponse(BaseModel):
    items: list[InsightItem]
    total: int


class TrendPoint(BaseModel):
    month: datetime | str | None
    primary_issue: str | None = None
    cluster_label: str | None = None
    review_count: int
    avg_rating: float | None = None


class TrendResponse(BaseModel):
    issue_series: list[TrendPoint]
    cluster_series: list[TrendPoint]
