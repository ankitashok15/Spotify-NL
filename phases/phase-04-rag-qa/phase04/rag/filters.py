from __future__ import annotations

from datetime import datetime

from phase03.search.schemas import SearchFilters
from phase04.rag.schemas import RouterFilters


def router_filters_to_search_filters(filters: RouterFilters) -> SearchFilters:
    return SearchFilters(
        rating_min=filters.rating_min,
        rating_max=filters.rating_max,
        subscription_type=filters.subscription_type,
        device_type=filters.device_type,
        is_discovery_related=filters.is_discovery_related,
        primary_issue=filters.primary_issue,
        date_from=filters.date_from,
        date_to=filters.date_to,
    )


def merge_filters(
    explicit: SearchFilters | None,
    routed: RouterFilters,
) -> SearchFilters:
    base = router_filters_to_search_filters(routed)
    if explicit is None:
        return base
    return SearchFilters(
        rating_min=explicit.rating_min if explicit.rating_min is not None else base.rating_min,
        rating_max=explicit.rating_max if explicit.rating_max is not None else base.rating_max,
        subscription_type=explicit.subscription_type or base.subscription_type,
        device_type=explicit.device_type or base.device_type,
        is_discovery_related=(
            explicit.is_discovery_related
            if explicit.is_discovery_related is not None
            else base.is_discovery_related
        ),
        primary_issue=explicit.primary_issue or base.primary_issue,
        date_from=explicit.date_from or base.date_from,
        date_to=explicit.date_to if explicit.date_to else base.date_to,
    )
