import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from phase01.database.models import Base, get_engine


class AgentQuery(Base):
    __tablename__ = "agent_queries"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    answer: Mapped[str] = mapped_column(Text, nullable=False)
    confidence: Mapped[float | None] = mapped_column(Float)
    steps: Mapped[int] = mapped_column(default=0)
    tool_trace: Mapped[dict | None] = mapped_column(JSONB)
    citations: Mapped[list | None] = mapped_column(JSONB)
    took_ms: Mapped[float | None] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


def init_phase6_tables(database_url: str) -> None:
    from phase05.database.models import init_phase5_tables

    init_phase5_tables(database_url)
    engine = get_engine(database_url)
    Base.metadata.create_all(bind=engine, tables=[AgentQuery.__table__])
