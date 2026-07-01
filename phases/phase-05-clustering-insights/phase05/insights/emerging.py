from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.orm import Session

from phase05.shared.config import settings


class EmergingIssuesDetector:
    def __init__(self, session: Session):
        self.session = session

    def detect(self, *, days: int = 30) -> list[dict]:
        rows = self.session.execute(
            text(
                """
                WITH recent AS (
                    SELECT sr.primary_issue, COUNT(*) AS cnt
                    FROM structured_reviews sr
                    JOIN reviews r ON r.id = sr.review_id
                    WHERE r.review_created_at >= NOW() - (:days || ' days')::interval
                      AND sr.primary_issue IS NOT NULL
                    GROUP BY sr.primary_issue
                ),
                prior AS (
                    SELECT sr.primary_issue, COUNT(*) AS cnt
                    FROM structured_reviews sr
                    JOIN reviews r ON r.id = sr.review_id
                    WHERE r.review_created_at >= NOW() - (:days2 || ' days')::interval
                      AND r.review_created_at < NOW() - (:days || ' days')::interval
                      AND sr.primary_issue IS NOT NULL
                    GROUP BY sr.primary_issue
                )
                SELECT
                    COALESCE(recent.primary_issue, prior.primary_issue) AS primary_issue,
                    COALESCE(recent.cnt, 0) AS recent_count,
                    COALESCE(prior.cnt, 0) AS prior_count,
                    CASE
                        WHEN COALESCE(prior.cnt, 0) = 0 THEN NULL
                        ELSE (COALESCE(recent.cnt, 0)::float - prior.cnt) / prior.cnt
                    END AS growth_rate
                FROM recent
                FULL OUTER JOIN prior ON recent.primary_issue = prior.primary_issue
                ORDER BY growth_rate DESC NULLS LAST
                """
            ),
            {"days": days, "days2": days * 2},
        ).mappings().all()

        threshold = settings.emerging_growth_threshold
        emerging = []
        for row in rows:
            growth = row["growth_rate"]
            if growth is not None and growth >= threshold:
                emerging.append(dict(row))
        return emerging
