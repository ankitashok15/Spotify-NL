import uuid

from sqlalchemy.orm import Session

from phase04.database.models import QueryLog
from phase04.rag.pipeline import RAGResult


class QueryLogRepository:
    def __init__(self, session: Session):
        self.session = session

    def log(self, question: str, result: RAGResult, filters: dict | None = None) -> uuid.UUID:
        row = QueryLog(
            id=uuid.uuid4(),
            question=question,
            answer=result.answer,
            intent=result.intent,
            search_query=result.search_query,
            filters=filters,
            citations=result.citations,
            confidence=result.confidence,
            reviews_considered=result.reviews_considered,
            reviews_cited=result.reviews_cited,
            took_ms=result.took_ms,
            citation_valid=result.citation_valid,
            warnings=result.warnings,
        )
        self.session.add(row)
        self.session.flush()
        return row.id
