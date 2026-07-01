from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from phase05.api.schemas import TrendPoint, TrendResponse
from phase05.database.session import get_db_session
from phase05.insights.trends import TrendAnalyzer

router = APIRouter(prefix="/api/v1", tags=["trends"])


def get_session():
    with get_db_session() as session:
        yield session


@router.get("/trends", response_model=TrendResponse)
def get_trends(months: int = 6, session: Session = Depends(get_session)):
    analyzer = TrendAnalyzer(session)
    issue_rows = analyzer.issue_time_series(months=months)
    cluster_rows = analyzer.cluster_time_series(months=months)
    return TrendResponse(
        issue_series=[TrendPoint(**row) for row in issue_rows],
        cluster_series=[
            TrendPoint(
                month=row.get("month"),
                cluster_label=row.get("cluster_label"),
                review_count=row.get("member_count", 0),
            )
            for row in cluster_rows
        ],
    )
