import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from phase01.database.models import Base, get_engine


class StructuredReview(Base):
    __tablename__ = "structured_reviews"
    __table_args__ = (UniqueConstraint("review_id", name="uq_structured_reviews_review_id"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    review_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("reviews.id"), nullable=False, index=True)
    detected_language: Mapped[str | None] = mapped_column(String(10))
    text_en: Mapped[str | None] = mapped_column(Text)
    summary: Mapped[str | None] = mapped_column(Text)
    primary_issue: Mapped[str | None] = mapped_column(String(255), index=True)
    secondary_issues: Mapped[list | None] = mapped_column(JSONB)
    emotions: Mapped[list | None] = mapped_column(JSONB)
    sentiment: Mapped[dict | None] = mapped_column(JSONB)
    recommendation_quality: Mapped[str | None] = mapped_column(String(50))
    user_intent: Mapped[str | None] = mapped_column(String(50))
    listening_context: Mapped[list | None] = mapped_column(JSONB)
    mentioned_features: Mapped[list | None] = mapped_column(JSONB)
    feature_requests: Mapped[list | None] = mapped_column(JSONB)
    pain_points: Mapped[list | None] = mapped_column(JSONB)
    behaviors: Mapped[list | None] = mapped_column(JSONB)
    severity: Mapped[str | None] = mapped_column(String(20))
    urgency: Mapped[str | None] = mapped_column(String(20))
    subscription_type: Mapped[str | None] = mapped_column(String(50), index=True)
    user_persona_signals: Mapped[list | None] = mapped_column(JSONB)
    is_discovery_related: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    confidence: Mapped[float | None] = mapped_column(Float)
    metadata_enrichment: Mapped[dict | None] = mapped_column(JSONB)
    extraction_model: Mapped[str | None] = mapped_column(String(100))
    content_hash: Mapped[str | None] = mapped_column(String(64), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class ExtractionCache(Base):
    __tablename__ = "extraction_cache"
    __table_args__ = (UniqueConstraint("content_hash", name="uq_extraction_cache_content_hash"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    extraction_payload: Mapped[dict] = mapped_column(JSONB, nullable=False)
    model_name: Mapped[str | None] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


def init_phase2_tables(database_url: str) -> None:
    """Create Phase 2 tables (requires Phase 1 tables to exist)."""
    from phase01.database.models import init_db

    init_db(database_url)
    engine = get_engine(database_url)
    Base.metadata.create_all(bind=engine, tables=[StructuredReview.__table__, ExtractionCache.__table__])
