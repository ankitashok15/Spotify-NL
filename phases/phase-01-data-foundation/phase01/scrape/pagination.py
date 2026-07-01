import logging
from dataclasses import dataclass

from google_play_scraper import Sort, app, reviews

from phase01.shared.config import settings

logger = logging.getLogger(__name__)

_SORT_MAP = {
    "NEWEST": Sort.NEWEST,
    "RATING": Sort.RATING,
    "MOST_RELEVANT": Sort.MOST_RELEVANT,
}


@dataclass
class AppMetadata:
    app_id: str
    title: str
    reviews_count: int
    score: float


def get_sort_enum(sort_name: str) -> Sort:
    key = sort_name.upper()
    if key not in _SORT_MAP:
        raise ValueError(f"Unknown sort: {sort_name}")
    return _SORT_MAP[key]


def fetch_app_metadata(app_id: str, lang: str = "en", country: str = "us") -> AppMetadata:
    data = app(app_id, lang=lang, country=country)
    return AppMetadata(
        app_id=app_id,
        title=data.get("title", ""),
        reviews_count=int(data.get("reviews", 0)),
        score=float(data.get("score", 0)),
    )


def fetch_review_page(
    app_id: str,
    *,
    sort: Sort,
    count: int,
    lang: str = "en",
    country: str = "us",
    continuation_token=None,
) -> tuple[list[dict], object | None]:
    kwargs = {
        "lang": lang,
        "country": country,
        "sort": sort,
        "count": count,
    }
    if continuation_token is not None:
        result, token = reviews(app_id, continuation_token=continuation_token)
    else:
        result, token = reviews(app_id, **kwargs)
    return list(result), token
