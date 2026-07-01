import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from phase01.database.models import Base, get_engine


class QueryLog(Base):
    __tablename__ = "queries"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    answer: Mapped[str | None] = mapped_column(Text)
    intent: Mapped[str | None] = mapped_column(String(50))
    search_query: Mapped[str | None] = mapped_column(Text)
    filters: Mapped[dict | None] = mapped_column(JSONB)
    citations: Mapped[list | None] = mapped_column(JSONB)
    confidence: Mapped[float | None] = mapped_column(Float)
    reviews_considered: Mapped[int | None] = mapped_column(Integer)
    reviews_cited: Mapped[int | None] = mapped_column(Integer)
    took_ms: Mapped[float | None] = mapped_column(Float)
    citation_valid: Mapped[bool] = mapped_column(default=True)
    warnings: Mapped[list | None] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


def init_phase4_tables(database_url: str) -> None:
    from phase01.database.models import init_db
    from phase02.database.models import init_phase2_tables

    init_phase2_tables(database_url)
    engine = get_engine(database_url)
    Base.metadata.create_all(bind=engine, tables=[QueryLog.__table__])
