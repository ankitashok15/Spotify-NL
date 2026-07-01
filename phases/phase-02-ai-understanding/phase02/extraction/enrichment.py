from __future__ import annotations

import re

from phase01.database.models import Review
from phase02.extraction.schema import ReviewExtraction

FEATURE_ALIASES: dict[str, str] = {
    "dw": "discover_weekly",
    "discover weekly": "discover_weekly",
    "discover_weekly": "discover_weekly",
    "release radar": "release_radar",
    "daily mix": "daily_mix",
    "daily mixes": "daily_mix",
    "made for you": "made_for_you",
    "spotify wrapped": "spotify_wrapped",
    "ai dj": "ai_dj",
    "autoplay": "autoplay",
    "shuffle": "shuffle",
    "repeat": "repeat",
}


def _normalize_token(value: str) -> str:
    cleaned = value.strip().lower()
    cleaned = re.sub(r"[^\w\s-]", "", cleaned)
    cleaned = re.sub(r"[\s-]+", "_", cleaned)
    return FEATURE_ALIASES.get(cleaned, cleaned)


def normalize_feature_list(features: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for feature in features:
        normalized = _normalize_token(feature)
        if normalized and normalized not in seen:
            seen.add(normalized)
            result.append(normalized)
    return result


def apply_feature_normalization(extraction: ReviewExtraction) -> ReviewExtraction:
    data = extraction.model_dump()
    data["mentioned_features"] = normalize_feature_list(extraction.mentioned_features)
    data["feature_requests"] = normalize_feature_list(extraction.feature_requests)
    return ReviewExtraction.model_validate(data)


def _rating_sentiment_bucket(rating: int | None) -> str:
    if rating is None:
        return "neutral"
    if rating >= 4:
        return "positive"
    if rating == 3:
        return "neutral"
    return "negative"


def enrich_with_play_metadata(
    extraction: ReviewExtraction,
    review: Review,
) -> tuple[ReviewExtraction, dict]:
    """Cross-check sentiment with rating; weight by thumbs_up; flag developer reply."""
    rating_bucket = _rating_sentiment_bucket(review.rating)
    llm_sentiment = extraction.sentiment.overall
    aligned = (
        (rating_bucket == "positive" and llm_sentiment in ("positive", "mixed"))
        or (rating_bucket == "negative" and llm_sentiment in ("negative", "mixed"))
        or (rating_bucket == "neutral" and llm_sentiment in ("neutral", "mixed"))
    )

    severity = extraction.severity
    if not aligned and review.rating is not None:
        if review.rating <= 2 and llm_sentiment == "positive":
            severity = "high"
        elif review.rating >= 4 and llm_sentiment == "negative":
            severity = "high"

    thumbs_weight = "low"
    if (review.thumbs_up or 0) >= 50:
        thumbs_weight = "high"
    elif (review.thumbs_up or 0) >= 10:
        thumbs_weight = "medium"

    metadata = {
        "rating": review.rating,
        "thumbs_up": review.thumbs_up,
        "device_type": review.device_type,
        "app_version": review.app_version,
        "rating_sentiment_aligned": aligned,
        "thumbs_up_weight": thumbs_weight,
        "has_developer_reply": bool(review.developer_reply),
        "developer_reply_resolved_hint": bool(review.developer_reply and review.rating and review.rating >= 4),
    }

    updated = extraction.model_copy(update={"severity": severity})
    return updated, metadata
