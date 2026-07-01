from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session

from phase01.database.repositories import ReviewRepository, ScrapeRunRepository
from phase01.database.session import get_db
from phase01.shared.config import settings as phase1_settings

router = APIRouter(prefix="/api/v1", tags=["dashboard"])


class DashboardStats(BaseModel):
    reviews_total: int
    structured_total: int
    vectors_indexed: int
    clusters_total: int
    insights_total: int
    scrape_status: str | None
    scrape_reviews_new: int
    top_issues: list[dict]


def _qdrant_point_count() -> int:
    try:
        from qdrant_client import QdrantClient
        from phase03.shared.config import settings as phase3_settings

        client = QdrantClient(url=phase3_settings.qdrant_url, check_compatibility=False)
        if not client.collection_exists(phase3_settings.qdrant_collection):
            return 0
        info = client.get_collection(phase3_settings.qdrant_collection)
        return int(info.points_count or 0)
    except Exception:
        return 0


def _safe_count(db: Session, sql: str) -> int:
    try:
        return int(db.execute(text(sql)).scalar_one() or 0)
    except Exception:
        return 0


@router.get("/dashboard/stats", response_model=DashboardStats)
def dashboard_stats(db: Session = Depends(get_db)) -> DashboardStats:
    review_repo = ReviewRepository(db)
    _, reviews_total = review_repo.list_reviews(limit=1, offset=0)

    structured_total = _safe_count(db, "SELECT COUNT(*) FROM structured_reviews")
    clusters_total = _safe_count(db, "SELECT COUNT(*) FROM clusters")
    insights_total = _safe_count(db, "SELECT COUNT(*) FROM insights")

    top_issues: list[dict] = []
    try:
        top_issues = [
            {
                "primary_issue": row["primary_issue"],
                "count": int(row["count"]),
            }
            for row in db.execute(
                text(
                    """
                    SELECT primary_issue, COUNT(*) AS count
                    FROM structured_reviews
                    WHERE primary_issue IS NOT NULL AND primary_issue != 'none'
                    GROUP BY primary_issue
                    ORDER BY count DESC
                    LIMIT 8
                    """
                )
            ).mappings().all()
        ]
    except Exception:
        top_issues = []

    run = ScrapeRunRepository(db).get_latest(phase1_settings.spotify_app_id)
    return DashboardStats(
        reviews_total=reviews_total,
        structured_total=structured_total,
        vectors_indexed=_qdrant_point_count(),
        clusters_total=clusters_total,
        insights_total=insights_total,
        scrape_status=run.status if run else None,
        scrape_reviews_new=run.reviews_new if run else 0,
        top_issues=top_issues,
    )
