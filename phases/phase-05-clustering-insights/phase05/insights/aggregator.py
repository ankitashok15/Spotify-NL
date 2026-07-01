from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.orm import Session


class ComplaintAggregator:
    def __init__(self, session: Session):
        self.session = session

    def top_complaints(self, *, limit: int = 15) -> list[dict]:
        rows = self.session.execute(
            text(
                """
                SELECT
                    sr.primary_issue,
                    COUNT(*) AS review_count,
                    ROUND(AVG(r.rating)::numeric, 2) AS avg_rating,
                    ROUND(AVG(sr.confidence)::numeric, 2) AS avg_confidence
                FROM structured_reviews sr
                JOIN reviews r ON r.id = sr.review_id
                WHERE sr.primary_issue IS NOT NULL
                  AND sr.primary_issue != 'none'
                GROUP BY sr.primary_issue
                ORDER BY review_count DESC
                LIMIT :limit
                """
            ),
            {"limit": limit},
        ).mappings().all()
        return [dict(row) for row in rows]

    def segment_breakdown(self) -> list[dict]:
        rows = self.session.execute(
            text(
                """
                SELECT
                    sr.subscription_type,
                    sr.primary_issue,
                    COUNT(*) AS review_count,
                    ROUND(AVG(r.rating)::numeric, 2) AS avg_rating
                FROM structured_reviews sr
                JOIN reviews r ON r.id = sr.review_id
                WHERE sr.primary_issue IS NOT NULL
                GROUP BY sr.subscription_type, sr.primary_issue
                ORDER BY review_count DESC
                LIMIT 30
                """
            )
        ).mappings().all()
        return [dict(row) for row in rows]
