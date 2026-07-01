import sys
import uuid
from pathlib import Path

import pytest

_PHASE01 = Path(__file__).resolve().parents[2] / "phases" / "phase-01-data-foundation"
_PHASE02 = Path(__file__).resolve().parents[2] / "phases" / "phase-02-ai-understanding"
sys.path.insert(0, str(_PHASE01))
sys.path.insert(0, str(_PHASE02))

from phase01.database.models import Review  # noqa: E402
from phase02.extraction.enrichment import (  # noqa: E402
    apply_feature_normalization,
    enrich_with_play_metadata,
    normalize_feature_list,
)
from phase02.extraction.language import detect_language, is_english  # noqa: E402
from phase02.extraction.schema import ReviewExtraction, SentimentDetail  # noqa: E402
from phase02.extraction.validator import validate_extraction_batch  # noqa: E402


def _sample_extraction(**overrides) -> ReviewExtraction:
    data = {
        "review_id": str(uuid.uuid4()),
        "summary": "User complains about repetitive Discover Weekly picks.",
        "primary_issue": "repetitive_recommendations",
        "secondary_issues": ["poor_discover_weekly"],
        "emotions": ["frustration"],
        "sentiment": SentimentDetail(overall="negative", toward_product="negative", toward_feature="negative"),
        "recommendation_quality": "poor",
        "user_intent": "complaint",
        "mentioned_features": ["DW", "playlists"],
        "feature_requests": ["better discover weekly"],
        "pain_points": ["same songs every week"],
        "is_discovery_related": True,
        "confidence": 0.9,
    }
    data.update(overrides)
    return ReviewExtraction.model_validate(data)


def test_normalize_feature_list_aliases():
    assert normalize_feature_list(["DW", "Discover Weekly", "playlists"]) == [
        "discover_weekly",
        "playlists",
    ]


def test_apply_feature_normalization():
    extraction = _sample_extraction()
    normalized = apply_feature_normalization(extraction)
    assert "discover_weekly" in normalized.mentioned_features
    assert "DW" not in normalized.mentioned_features


def test_enrich_with_play_metadata_misaligned_sentiment():
    extraction = _sample_extraction(
        sentiment=SentimentDetail(overall="positive", toward_product="positive", toward_feature="positive"),
        severity="low",
    )
    review = Review(
        id=uuid.uuid4(),
        external_review_id="ext1",
        app_id="com.spotify.music",
        rating=1,
        thumbs_up=25,
        device_type="phone",
        developer_reply=None,
    )
    updated, metadata = enrich_with_play_metadata(extraction, review)
    assert updated.severity == "high"
    assert metadata["rating_sentiment_aligned"] is False
    assert metadata["thumbs_up_weight"] == "medium"


def test_validate_extraction_batch():
    rid = str(uuid.uuid4())
    payload = {
        "extractions": [
            _sample_extraction(review_id=rid).model_dump(),
        ]
    }
    result = validate_extraction_batch(payload, [rid])
    assert len(result) == 1
    assert result[0].review_id == rid


def test_validate_extraction_batch_missing_id():
    rid = str(uuid.uuid4())
    with pytest.raises(ValueError, match="Missing review_id"):
        validate_extraction_batch({"extractions": []}, [rid])


def test_detect_language_english():
    lang, confidence = detect_language("I love Spotify but recommendations repeat too often.")
    assert is_english(lang)
    assert confidence > 0


def test_review_extraction_discovery_flag():
    extraction = _sample_extraction(is_discovery_related=True)
    assert extraction.is_discovery_related is True
    assert extraction.subscription_type == "unknown"
