import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

_PHASE_ROOT = Path(__file__).resolve().parents[2] / "phases" / "phase-01-data-foundation"
sys.path.insert(0, str(_PHASE_ROOT))

from phase01.cleaning.normalizer import content_hash, normalize_text  # noqa: E402
from phase01.cleaning.spam_filter import is_spam  # noqa: E402
from phase01.scrape.normalizer import normalize_play_review  # noqa: E402
from phase01.scrape.window import (  # noqa: E402
    filter_reviews_in_window,
    review_in_window,
    scrape_cutoff_date,
)


def test_normalize_text_strips_html():
    assert normalize_text("<b>Hello</b> world") == "Hello world"


def test_normalize_text_collapses_whitespace():
    assert normalize_text("too   many   spaces") == "too many spaces"


def test_content_hash_stable():
    h1 = content_hash("Same text")
    h2 = content_hash("same text")
    assert h1 == h2


def test_spam_detection():
    assert is_spam("CLICK HERE to download free money!!!") is True
    assert is_spam("I love Spotify but Discover Weekly is repetitive") is False


def test_normalize_play_review():
    raw = {
        "reviewId": "abc123",
        "userName": "Test User",
        "content": "Great app but recommendations repeat.",
        "score": 3,
        "thumbsUpCount": 5,
        "at": None,
    }
    row = normalize_play_review(raw, "com.spotify.music")
    assert row["external_review_id"] == "abc123"
    assert row["rating"] == 3
    assert row["thumbs_up"] == 5
    assert row["author_hash"] is not None


def test_scrape_cutoff_date_six_months():
    cutoff = scrape_cutoff_date(6)
    now = datetime.now(timezone.utc)
    delta = now - cutoff
    assert 175 <= delta.days <= 185


def test_review_in_window():
    cutoff = datetime.now(timezone.utc) - timedelta(days=30)
    recent = {"at": datetime.now(timezone.utc)}
    old = {"at": datetime.now(timezone.utc) - timedelta(days=200)}
    assert review_in_window(recent, cutoff) is True
    assert review_in_window(old, cutoff) is False


def test_filter_reviews_in_window():
    cutoff = datetime.now(timezone.utc) - timedelta(days=30)
    reviews = [
        {"at": datetime.now(timezone.utc), "reviewId": "1"},
        {"at": datetime.now(timezone.utc) - timedelta(days=200), "reviewId": "2"},
    ]
    filtered = filter_reviews_in_window(reviews, cutoff)
    assert len(filtered) == 1
    assert filtered[0]["reviewId"] == "1"
