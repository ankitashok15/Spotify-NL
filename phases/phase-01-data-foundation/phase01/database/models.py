import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    create_engine,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker


class Base(DeclarativeBase):
    pass


class ScrapeRun(Base):
    __tablename__ = "scrape_runs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    run_type: Mapped[str] = mapped_column(String(50), nullable=False)
    app_id: Mapped[str] = mapped_column(String(255), nullable=False)
    reviews_target: Mapped[int | None] = mapped_column(Integer)
    reviews_scraped: Mapped[int] = mapped_column(Integer, default=0)
    reviews_new: Mapped[int] = mapped_column(Integer, default=0)
    reviews_updated: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(20), default="running")
    gap_report: Mapped[dict | None] = mapped_column(JSONB)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    checkpoints: Mapped[list["ScrapeCheckpoint"]] = relationship(back_populates="scrape_run")
    reviews: Mapped[list["Review"]] = relationship(back_populates="scrape_run")


class ScrapeCheckpoint(Base):
    __tablename__ = "scrape_checkpoints"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    scrape_run_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("scrape_runs.id"), nullable=False)
    sort_order: Mapped[str] = mapped_column(String(50), nullable=False)
    lang: Mapped[str] = mapped_column(String(10), default="en")
    country: Mapped[str] = mapped_column(String(10), default="us")
    continuation_token: Mapped[str | None] = mapped_column(Text)
    reviews_scraped_in_pass: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(20), default="in_progress")
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    scrape_run: Mapped["ScrapeRun"] = relationship(back_populates="checkpoints")


class Review(Base):
    __tablename__ = "reviews"
    __table_args__ = (UniqueConstraint("external_review_id", name="uq_reviews_external_review_id"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    external_review_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    app_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    author_hash: Mapped[str | None] = mapped_column(String(64))
    text_original: Mapped[str | None] = mapped_column(Text)
    text_cleaned: Mapped[str | None] = mapped_column(Text)
    rating: Mapped[int | None] = mapped_column(Integer, index=True)
    thumbs_up: Mapped[int] = mapped_column(Integer, default=0)
    device_type: Mapped[str | None] = mapped_column(String(50))
    app_version: Mapped[str | None] = mapped_column(String(50))
    review_created_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)
    developer_reply: Mapped[str | None] = mapped_column(Text)
    developer_reply_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    is_spam: Mapped[bool] = mapped_column(Boolean, default=False)
    is_near_duplicate: Mapped[bool] = mapped_column(Boolean, default=False)
    processing_state: Mapped[str] = mapped_column(String(20), default="RAW", index=True)
    pipeline_version: Mapped[str] = mapped_column(String(20), default="1.0")
    scrape_run_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("scrape_runs.id"))
    collected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    scrape_run: Mapped["ScrapeRun | None"] = relationship(back_populates="reviews")


class DedupIndex(Base):
    __tablename__ = "dedup_index"
    __table_args__ = (UniqueConstraint("content_hash", name="uq_dedup_content_hash"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    review_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("reviews.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


_engine = None
_SessionLocal = None


def get_engine(database_url: str):
    global _engine
    if _engine is None:
        _engine = create_engine(database_url, pool_pre_ping=True)
    return _engine


def get_session_factory(database_url: str):
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(bind=get_engine(database_url), autoflush=False, autocommit=False)
    return _SessionLocal


def init_db(database_url: str) -> None:
    engine = get_engine(database_url)
    Base.metadata.create_all(bind=engine)
