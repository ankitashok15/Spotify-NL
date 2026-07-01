from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from phase05.api.schemas import InsightItem, InsightListResponse
from phase05.database.repositories import InsightRepository
from phase05.database.session import get_db_session

router = APIRouter(prefix="/api/v1", tags=["insights"])


def get_session():
    with get_db_session() as session:
        yield session


@router.get("/insights", response_model=InsightListResponse)
def list_insights(
    insight_type: str | None = Query(default=None),
    limit: int = 50,
    session: Session = Depends(get_session),
):
    repo = InsightRepository(session)
    items = repo.list_insights(insight_type=insight_type, limit=limit)
    return InsightListResponse(
        items=[InsightItem.model_validate(i) for i in items],
        total=len(items),
    )
