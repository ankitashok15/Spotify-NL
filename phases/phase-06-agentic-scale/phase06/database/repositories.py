from __future__ import annotations

from sqlalchemy.orm import Session

from phase06.agent.schemas import AgentResult
from phase06.database.models import AgentQuery


class AgentQueryRepository:
    def __init__(self, session: Session):
        self.session = session

    def log(self, question: str, result: AgentResult, *, include_trace: bool = False) -> AgentQuery:
        row = AgentQuery(
            question=question,
            answer=result.answer,
            confidence=result.confidence,
            steps=result.steps,
            tool_trace=result.to_dict(include_trace=True).get("tool_trace") if include_trace else None,
            citations=result.citations,
            took_ms=result.took_ms,
        )
        self.session.add(row)
        self.session.flush()
        return row
