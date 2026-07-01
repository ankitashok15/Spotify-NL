import sys
from datetime import datetime
from pathlib import Path

import pytest

_PHASE03 = Path(__file__).resolve().parents[2] / "phases" / "phase-03-semantic-search"
sys.path.insert(0, str(_PHASE03))

from phase03.embedding.templates import ReviewEmbedInput, build_embedding_text, build_search_payload  # noqa: E402
from phase03.embedding.versioning import embedding_model_version  # noqa: E402
from phase03.search.schemas import SearchFilters, build_qdrant_filter  # noqa: E402


def test_build_embedding_text_includes_metadata():
    text = build_embedding_text(
        ReviewEmbedInput(
            review_id="abc",
            text_en="Discover Weekly keeps repeating the same artists.",
            rating=2,
            primary_issue="repetitive_recommendations",
            secondary_issues=["poor_discover_weekly"],
            mentioned_features=["discover_weekly"],
        )
    )
    assert "Review: Discover Weekly" in text
    assert "Rating: 2/5" in text
    assert "repetitive_recommendations" in text
    assert "discover_weekly" in text


def test_build_search_payload():
    payload = build_search_payload(
        review_id="rid-1",
        rating=2,
        device_type="phone",
        subscription_type="free",
        primary_issue="repetitive_recommendations",
        is_discovery_related=True,
        review_created_at=datetime(2026, 4, 21),
        thumbs_up=27,
        embedding_model_version=embedding_model_version(),
        text_en="Same songs every week",
        external_review_id="gp-123",
    )
    assert payload["document_id"] == "rid-1"
    assert payload["rating"] == 2
    assert payload["is_discovery_related"] is True
    assert payload["cluster_ids"] == []


def test_build_qdrant_filter_rating_and_subscription():
    filt = build_qdrant_filter(
        SearchFilters(rating_max=3, subscription_type="free", is_discovery_related=True)
    )
    assert filt is not None
    assert len(filt.must) == 3


def test_build_qdrant_filter_date_range():
    filt = build_qdrant_filter(
        SearchFilters(
            date_from=datetime(2025, 1, 1),
            date_to=datetime(2026, 1, 1),
        )
    )
    assert filt is not None
    assert len(filt.must) == 2


def test_embedding_model_version_stable():
    v1 = embedding_model_version()
    v2 = embedding_model_version()
    assert v1 == v2
    assert "gemini-embedding" in v1 or "embedding" in v1 or "@" in v1
