from __future__ import annotations

from datetime import datetime

from phase03.search.schemas import SearchFilters
from phase03.search.semantic_search import SemanticSearchService
from phase06.agent.tools.base import AgentTool


class SemanticSearchTool(AgentTool):
    name = "semantic_search"
    description = "Find reviews by meaning with optional metadata filters."

    def __init__(self) -> None:
        self._service = SemanticSearchService()

    def run(self, args: dict) -> list[dict]:
        query = args.get("query") or args.get("q") or ""
        if not query:
            raise ValueError("semantic_search requires 'query'")

        filters = self._build_filters(args.get("filters") or {})
        top_k = int(args.get("top_k", 10))
        response = self._service.search(query, filters=filters, top_k=top_k)
        return [
            {
                "review_id": hit.review_id,
                "score": hit.score,
                "rating": hit.rating,
                "subscription_type": hit.subscription_type,
                "device_type": hit.device_type,
                "primary_issue": hit.primary_issue,
                "text_en": (hit.text_en or "")[:400],
                "review_created_at": hit.review_created_at.isoformat() if hit.review_created_at else None,
            }
            for hit in response.results
        ]

    def _build_filters(self, raw: dict) -> SearchFilters | None:
        if not raw:
            return None
        date_from = raw.get("date_from")
        date_to = raw.get("date_to")
        return SearchFilters(
            rating_min=raw.get("rating_min"),
            rating_max=raw.get("rating_max"),
            subscription_type=raw.get("subscription_type"),
            device_type=raw.get("device_type"),
            is_discovery_related=raw.get("is_discovery_related"),
            primary_issue=raw.get("primary_issue"),
            date_from=datetime.fromisoformat(date_from) if isinstance(date_from, str) else date_from,
            date_to=datetime.fromisoformat(date_to) if isinstance(date_to, str) else date_to,
        )
