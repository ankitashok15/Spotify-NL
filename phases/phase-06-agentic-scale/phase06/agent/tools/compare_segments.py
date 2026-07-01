from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.orm import Session

from phase06.agent.tools.base import AgentTool


class CompareSegmentsTool(AgentTool):
    name = "compare_segments"
    description = "Compare discovery issues between two user segments."

    def __init__(self, session: Session) -> None:
        self.session = session

    def run(self, args: dict) -> dict:
        segment_a = args.get("segment_a") or {}
        segment_b = args.get("segment_b") or {}
        topic = args.get("topic")
        limit = int(args.get("limit", 10))

        def fetch(segment: dict) -> list[dict]:
            rows = self.session.execute(
                text(
                    """
                    SELECT
                        sr.primary_issue,
                        COUNT(*) AS review_count,
                        ROUND(AVG(r.rating)::numeric, 2) AS avg_rating
                    FROM structured_reviews sr
                    JOIN reviews r ON r.id = sr.review_id
                    WHERE sr.primary_issue IS NOT NULL
                      AND (:subscription_type IS NULL OR sr.subscription_type = :subscription_type)
                      AND (:device_type IS NULL OR r.device_type = :device_type)
                      AND (:topic IS NULL OR sr.primary_issue ILIKE '%' || :topic || '%'
                           OR sr.text_en ILIKE '%' || :topic || '%')
                    GROUP BY sr.primary_issue
                    ORDER BY review_count DESC
                    LIMIT :limit
                    """
                ),
                {
                    "subscription_type": segment.get("subscription_type"),
                    "device_type": segment.get("device_type"),
                    "topic": topic,
                    "limit": limit,
                },
            ).mappings().all()
            return [dict(row) for row in rows]

        return {
            "segment_a": segment_a,
            "segment_b": segment_b,
            "segment_a_issues": fetch(segment_a),
            "segment_b_issues": fetch(segment_b),
        }
