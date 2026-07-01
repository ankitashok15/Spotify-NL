from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.orm import Session


class OpportunityFinder:
    def __init__(self, session: Session):
        self.session = session

    def feature_request_frequency(self, *, limit: int = 20) -> list[dict]:
        rows = self.session.execute(
            text(
                """
                SELECT
                    elem.value AS feature_request,
                    COUNT(*) AS mention_count
                FROM structured_reviews sr
                CROSS JOIN LATERAL jsonb_array_elements_text(COALESCE(sr.feature_requests, '[]'::jsonb)) AS elem(value)
                GROUP BY elem.value
                ORDER BY mention_count DESC
                LIMIT :limit
                """
            ),
            {"limit": limit},
        ).mappings().all()
        return [dict(row) for row in rows]

    def unmet_needs_cooccurrence(self, *, limit: int = 15) -> list[dict]:
        rows = self.session.execute(
            text(
                """
                SELECT
                    sr.primary_issue,
                    elem.value AS feature_request,
                    COUNT(*) AS co_occurrence
                FROM structured_reviews sr
                CROSS JOIN LATERAL jsonb_array_elements_text(COALESCE(sr.feature_requests, '[]'::jsonb)) AS elem(value)
                WHERE sr.primary_issue IS NOT NULL
                GROUP BY sr.primary_issue, elem.value
                ORDER BY co_occurrence DESC
                LIMIT :limit
                """
            ),
            {"limit": limit},
        ).mappings().all()
        return [dict(row) for row in rows]
