import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from phase01.database.models import Base, get_engine


class Cluster(Base):
    __tablename__ = "clusters"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cluster_key: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    label: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    taxonomy_theme_id: Mapped[str | None] = mapped_column(String(100), index=True)
    member_count: Mapped[int] = mapped_column(Integer, default=0)
    avg_rating: Mapped[float | None] = mapped_column(Float)
    avg_thumbs_up: Mapped[float | None] = mapped_column(Float)
    top_subscription_types: Mapped[list | None] = mapped_column(JSONB)
    top_device_types: Mapped[list | None] = mapped_column(JSONB)
    representative_review_ids: Mapped[list | None] = mapped_column(JSONB)
    centroid: Mapped[list | None] = mapped_column(JSONB)
    trend_30d: Mapped[float | None] = mapped_column(Float)
    stats: Mapped[dict | None] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class ClusterMembership(Base):
    __tablename__ = "cluster_memberships"
    __table_args__ = (UniqueConstraint("review_id", name="uq_cluster_memberships_review_id"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cluster_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("clusters.id"), index=True)
    review_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("reviews.id"), index=True)
    assigned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Insight(Base):
    __tablename__ = "insights"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    insight_type: Mapped[str] = mapped_column(String(50), index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    confidence: Mapped[float | None] = mapped_column(Float)
    evidence_document_ids: Mapped[list | None] = mapped_column(JSONB)
    affected_personas: Mapped[list | None] = mapped_column(JSONB)
    payload: Mapped[dict | None] = mapped_column(JSONB)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


def init_phase5_tables(database_url: str) -> None:
    from phase04.database.models import init_phase4_tables

    init_phase4_tables(database_url)
    engine = get_engine(database_url)
    Base.metadata.create_all(
        bind=engine,
        tables=[Cluster.__table__, ClusterMembership.__table__, Insight.__table__],
    )
