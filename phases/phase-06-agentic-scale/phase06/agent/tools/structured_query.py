from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.orm import Session

from phase06.agent.tools.base import AgentTool


class StructuredQueryTool(AgentTool):
    name = "structured_query"
    description = "SQL aggregations: top issues, counts by segment, rankings."

    def __init__(self, session: Session) -> None:
        self.session = session

    def run(self, args: dict) -> list[dict]:
        group_by = args.get("group_by", "primary_issue")
        if group_by not in {"primary_issue", "subscription_type", "device_type", "rating"}:
            raise ValueError(f"Unsupported group_by: {group_by}")

        filters = args.get("filters") or {}
        limit = int(args.get("limit", 15))

        sql = f"""
            SELECT
                sr.{group_by} AS dimension,
                COUNT(*) AS review_count,
                ROUND(AVG(r.rating)::numeric, 2) AS avg_rating
            FROM structured_reviews sr
            JOIN reviews r ON r.id = sr.review_id
            WHERE sr.{group_by} IS NOT NULL
              AND (:subscription_type IS NULL OR sr.subscription_type = :subscription_type)
              AND (:device_type IS NULL OR r.device_type = :device_type)
              AND (:primary_issue IS NULL OR sr.primary_issue = :primary_issue)
              AND (:date_from IS NULL OR r.review_created_at >= :date_from)
              AND (:date_to IS NULL OR r.review_created_at <= :date_to)
              AND (:is_discovery_related IS NULL OR sr.is_discovery_related = :is_discovery_related)
            GROUP BY sr.{group_by}
            ORDER BY review_count DESC
            LIMIT :limit
        """
        rows = self.session.execute(
            text(sql),
            {
                "subscription_type": filters.get("subscription_type"),
                "device_type": filters.get("device_type"),
                "primary_issue": filters.get("primary_issue"),
                "date_from": filters.get("date_from"),
                "date_to": filters.get("date_to"),
                "is_discovery_related": filters.get("is_discovery_related"),
                "limit": limit,
            },
        ).mappings().all()
        return [dict(row) for row in rows]
