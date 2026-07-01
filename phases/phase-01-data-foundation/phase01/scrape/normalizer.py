import hashlib
import json
from datetime import datetime, timezone
from typing import Any

from phase01.database.repositories import hash_author
from phase01.shared.constants import PIPELINE_VERSION, ProcessingState


def _parse_datetime(value: Any) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value
    return None


def normalize_play_review(raw: dict, app_id: str, scrape_run_id: str | None = None) -> dict:
    """Map google-play-scraper review dict to DB row."""
    review_id = raw.get("reviewId") or raw.get("review_id")
    if not review_id:
        raise ValueError("Review missing reviewId")

    user_name = raw.get("userName") or raw.get("user_name")
    content = raw.get("content") or raw.get("text") or ""

    return {
        "external_review_id": str(review_id),
        "app_id": app_id,
        "author_hash": hash_author(user_name),
        "text_original": content or None,
        "text_cleaned": None,
        "rating": raw.get("score") or raw.get("rating"),
        "thumbs_up": int(raw.get("thumbsUpCount") or raw.get("thumbs_up") or 0),
        "device_type": raw.get("device") or raw.get("device_type"),
        "app_version": raw.get("reviewCreatedVersion") or raw.get("app_version"),
        "review_created_at": _parse_datetime(raw.get("at") or raw.get("review_created_at")),
        "developer_reply": raw.get("replyContent") or raw.get("developer_reply"),
        "developer_reply_at": _parse_datetime(raw.get("repliedAt") or raw.get("developer_reply_at")),
        "is_spam": False,
        "is_near_duplicate": False,
        "processing_state": ProcessingState.RAW,
        "pipeline_version": PIPELINE_VERSION,
        "scrape_run_id": scrape_run_id,
    }


def serialize_token(token: Any) -> str | None:
    if token is None:
        return None
    return json.dumps(token, default=str)


def deserialize_token(token_str: str | None) -> Any:
    if not token_str:
        return None
    return json.loads(token_str)
