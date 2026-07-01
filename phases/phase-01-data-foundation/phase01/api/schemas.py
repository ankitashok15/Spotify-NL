import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class ScrapeRequest(BaseModel):
    mode: str = Field(default="window", pattern="^(window|full|incremental)$")
    app_id: str | None = None
    limit: int | None = None
    months_back: int | None = Field(default=None, ge=1, le=24)
    since: datetime | None = None


class ScrapeResponse(BaseModel):
    run_id: uuid.UUID
    message: str


class ScrapeStatusResponse(BaseModel):
    run_id: uuid.UUID | None
    status: str | None
    app_id: str
    reviews_target: int | None
    reviews_scraped: int
    reviews_new: int
    reviews_updated: int
    gap_report: dict | None
    started_at: datetime | None
    ended_at: datetime | None


class ReviewResponse(BaseModel):
    id: uuid.UUID
    external_review_id: str
    app_id: str
    text_original: str | None
    text_cleaned: str | None
    rating: int | None
    thumbs_up: int
    device_type: str | None
    app_version: str | None
    review_created_at: datetime | None
    developer_reply: str | None
    is_spam: bool
    is_near_duplicate: bool
    processing_state: str
    collected_at: datetime

    model_config = {"from_attributes": True}


class ReviewListResponse(BaseModel):
    items: list[ReviewResponse]
    total: int
    limit: int
    offset: int


class ValidationResponse(BaseModel):
    report: dict
