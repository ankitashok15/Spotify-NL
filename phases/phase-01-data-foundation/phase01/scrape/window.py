"""Rolling time-window helpers for review scraping."""

from datetime import datetime, timedelta, timezone


def scrape_cutoff_date(months_back: int) -> datetime:
    """Return UTC datetime for the start of the scrape window (rolling months)."""
    if months_back <= 0:
        raise ValueError("months_back must be positive")
    return datetime.now(timezone.utc) - timedelta(days=30 * months_back)


def ensure_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


def review_in_window(review: dict, cutoff: datetime) -> bool:
    """True if review date is on or after cutoff."""
    at = review.get("at") or review.get("review_created_at")
    if at is None:
        return True  # keep undated reviews rather than drop
    return ensure_utc(at) >= cutoff


def filter_reviews_in_window(reviews: list[dict], cutoff: datetime) -> list[dict]:
    return [r for r in reviews if review_in_window(r, cutoff)]


def batch_oldest_date(reviews: list[dict]) -> datetime | None:
    dates = [r.get("at") for r in reviews if r.get("at")]
    if not dates:
        return None
    return min(ensure_utc(d) for d in dates)
