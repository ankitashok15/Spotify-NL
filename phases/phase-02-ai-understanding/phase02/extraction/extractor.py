from __future__ import annotations

import logging
import uuid
from dataclasses import dataclass

from phase01.database.models import Review
from phase02.extraction.enrichment import apply_feature_normalization, enrich_with_play_metadata
from phase02.extraction.language import detect_language, is_english
from phase02.extraction.prompts import build_extraction_prompt, extraction_system_prompt
from phase02.extraction.schema import ReviewExtraction
from phase02.extraction.translation import translate_to_english
from phase02.extraction.validator import extract_with_retry
from phase02.shared.llm_provider import LLMProvider

logger = logging.getLogger(__name__)


@dataclass
class PreparedReview:
    review: Review
    review_id: str
    detected_language: str
    text_en: str
    content_hash: str


def prepare_review_text(review: Review, llm: LLMProvider) -> PreparedReview:
    from phase02.extraction.cache import content_hash

    source_text = review.text_cleaned or review.text_original or ""
    lang, _ = detect_language(source_text)
    if is_english(lang):
        text_en = source_text
    else:
        text_en = translate_to_english(str(review.id), source_text, lang, llm)
    return PreparedReview(
        review=review,
        review_id=str(review.id),
        detected_language=lang,
        text_en=text_en,
        content_hash=content_hash(text_en),
    )


def build_llm_payload(prepared: PreparedReview) -> dict:
    r = prepared.review
    return {
        "review_id": prepared.review_id,
        "text_en": prepared.text_en,
        "rating": r.rating,
        "thumbs_up": r.thumbs_up,
        "device_type": r.device_type,
        "app_version": r.app_version,
        "has_developer_reply": bool(r.developer_reply),
    }


def extract_batch(
    prepared_reviews: list[PreparedReview],
    llm: LLMProvider,
) -> list[tuple[PreparedReview, ReviewExtraction, dict]]:
    if not prepared_reviews:
        return []

    payload = [build_llm_payload(p) for p in prepared_reviews]
    expected_ids = [p.review_id for p in prepared_reviews]
    prompt = build_extraction_prompt(payload)
    extractions = extract_with_retry(
        llm,
        prompt,
        system=extraction_system_prompt(),
        expected_ids=expected_ids,
    )

    results: list[tuple[PreparedReview, ReviewExtraction, dict]] = []
    by_id = {e.review_id: e for e in extractions}
    for prepared in prepared_reviews:
        extraction = by_id[prepared.review_id]
        extraction = apply_feature_normalization(extraction)
        extraction, metadata = enrich_with_play_metadata(extraction, prepared.review)
        results.append((prepared, extraction, metadata))
    return results


def extraction_to_row(
    prepared: PreparedReview,
    extraction: ReviewExtraction,
    metadata: dict,
    *,
    model_name: str,
) -> dict:
    return {
        "id": uuid.uuid4(),
        "review_id": uuid.UUID(prepared.review_id),
        "detected_language": prepared.detected_language,
        "text_en": prepared.text_en,
        "summary": extraction.summary,
        "primary_issue": extraction.primary_issue,
        "secondary_issues": extraction.secondary_issues,
        "emotions": extraction.emotions,
        "sentiment": extraction.sentiment.model_dump(),
        "recommendation_quality": extraction.recommendation_quality,
        "user_intent": extraction.user_intent,
        "listening_context": extraction.listening_context,
        "mentioned_features": extraction.mentioned_features,
        "feature_requests": extraction.feature_requests,
        "pain_points": extraction.pain_points,
        "behaviors": extraction.behaviors,
        "severity": extraction.severity,
        "urgency": extraction.urgency,
        "subscription_type": extraction.subscription_type,
        "user_persona_signals": extraction.user_persona_signals,
        "is_discovery_related": extraction.is_discovery_related,
        "confidence": extraction.confidence,
        "metadata_enrichment": metadata,
        "extraction_model": model_name,
        "content_hash": prepared.content_hash,
    }
