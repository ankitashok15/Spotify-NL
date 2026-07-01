from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.orm import Session


class TrendAnalyzer:
    def __init__(self, session: Session):
        self.session = session

    def issue_time_series(self, *, months: int = 6) -> list[dict]:
        rows = self.session.execute(
            text(
                """
                SELECT
                    date_trunc('month', r.review_created_at) AS month,
                    sr.primary_issue,
                    COUNT(*) AS review_count,
                    ROUND(AVG(r.rating)::numeric, 2) AS avg_rating
                FROM structured_reviews sr
                JOIN reviews r ON r.id = sr.review_id
                WHERE r.review_created_at >= NOW() - (:months || ' months')::interval
                  AND sr.primary_issue IS NOT NULL
                GROUP BY 1, 2
                ORDER BY 1 ASC, review_count DESC
                """
            ),
            {"months": months},
        ).mappings().all()
        return [dict(row) for row in rows]

    def cluster_time_series(self, *, months: int = 6) -> list[dict]:
        rows = self.session.execute(
            text(
                """
                SELECT
                    date_trunc('month', cm.assigned_at) AS month,
                    c.label AS cluster_label,
                    c.taxonomy_theme_id,
                    COUNT(*) AS member_count
                FROM cluster_memberships cm
                JOIN clusters c ON c.id = cm.cluster_id
                WHERE cm.assigned_at >= NOW() - (:months || ' months')::interval
                GROUP BY 1, 2, 3
                ORDER BY 1 ASC, member_count DESC
                """
            ),
            {"months": months},
        ).mappings().all()
        return [dict(row) for row in rows]
