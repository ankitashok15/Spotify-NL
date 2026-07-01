from __future__ import annotations

import json
import logging
import re

from phase02.shared.llm_gemini import GeminiProvider
from phase04.rag.schemas import RouterFilters, RouterResult

logger = logging.getLogger(__name__)

_ROUTER_SYSTEM = """You route Spotify Google Play review analytics questions.
Extract a semantic search query and optional metadata filters.
Return JSON only with keys: intent, search_query, filters, requires_aggregation.

intent examples: why_complaint, show_reviews, top_issues, trend_analysis, feature_requests, general_question
filters keys (all optional): rating_min, rating_max, subscription_type, device_type,
is_discovery_related, primary_issue, date_from, date_to, mentioned_feature
Use snake_case for primary_issue and mentioned_feature when obvious.
"""

_KEYWORD_FILTERS: list[tuple[re.Pattern, dict]] = [
    (re.compile(r"\bpremium\b", re.I), {"subscription_type": "premium"}),
    (re.compile(r"\bfree\b", re.I), {"subscription_type": "free"}),
    (re.compile(r"\bfamily plan\b", re.I), {"subscription_type": "family"}),
    (re.compile(r"\bstudent\b", re.I), {"subscription_type": "student"}),
    (re.compile(r"\b1[- ]?star\b", re.I), {"rating_min": 1, "rating_max": 1}),
    (re.compile(r"\bphone\b", re.I), {"device_type": "phone"}),
    (re.compile(r"\bdiscover weekly\b", re.I), {"mentioned_feature": "discover_weekly"}),
    (re.compile(r"\bdiscovery\b", re.I), {"is_discovery_related": True}),
]


class QueryRouter:
    def __init__(self, llm: GeminiProvider | None = None):
        self.llm = llm

    def route(self, question: str) -> RouterResult:
        heuristic = self._heuristic_route(question)
        if self.llm is None:
            return heuristic

        try:
            payload = self.llm.generate_json(
                json.dumps({"question": question}, ensure_ascii=False),
                system=_ROUTER_SYSTEM,
            )
            filters = RouterFilters.model_validate(payload.get("filters") or {})
            merged = RouterFilters.model_validate(
                {**heuristic.filters.model_dump(exclude_none=True), **filters.model_dump(exclude_none=True)}
            )
            return RouterResult(
                intent=payload.get("intent") or heuristic.intent,
                search_query=payload.get("search_query") or heuristic.search_query,
                filters=merged,
                requires_aggregation=bool(payload.get("requires_aggregation", False)),
            )
        except Exception as exc:
            logger.warning("LLM router failed, using heuristics: %s", exc)
            return heuristic

    def _heuristic_route(self, question: str) -> RouterResult:
        filters_data: dict = {}
        for pattern, data in _KEYWORD_FILTERS:
            if pattern.search(question):
                filters_data.update(data)

        intent = "general_question"
        lower = question.lower()
        if lower.startswith("show ") or "mentioning" in lower:
            intent = "show_reviews"
        elif lower.startswith("why ") or "why do" in lower or "complain about" in lower:
            intent = "why_complaint"
        elif "feature request" in lower or "most often" in lower:
            intent = "feature_requests"
        elif "changed" in lower or "trend" in lower or "this year" in lower:
            intent = "trend_analysis"
        elif "top " in lower and "issue" in lower:
            intent = "top_issues"

        return RouterResult(
            intent=intent,
            search_query=question.strip(),
            filters=RouterFilters.model_validate(filters_data),
        )
