from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator


class SentimentDetail(BaseModel):
    overall: Literal["positive", "negative", "neutral", "mixed"] = "neutral"
    toward_product: Literal["positive", "negative", "neutral", "mixed"] = "neutral"
    toward_feature: Literal["positive", "negative", "neutral", "mixed"] = "neutral"


class ReviewExtraction(BaseModel):
    """Structured fields extracted from a single review."""

    review_id: str
    summary: str = Field(min_length=1, max_length=500)
    primary_issue: str = Field(min_length=1, max_length=255)
    secondary_issues: list[str] = Field(default_factory=list)
    emotions: list[str] = Field(default_factory=list)
    sentiment: SentimentDetail = Field(default_factory=SentimentDetail)
    recommendation_quality: Literal["excellent", "good", "fair", "poor", "not_applicable"] = "not_applicable"
    user_intent: Literal[
        "complaint",
        "praise",
        "feature_request",
        "question",
        "comparison",
        "general_feedback",
    ] = "general_feedback"
    listening_context: list[str] = Field(default_factory=list)
    mentioned_features: list[str] = Field(default_factory=list)
    feature_requests: list[str] = Field(default_factory=list)
    pain_points: list[str] = Field(default_factory=list)
    behaviors: list[str] = Field(default_factory=list)
    severity: Literal["low", "medium", "high", "critical"] = "low"
    urgency: Literal["low", "medium", "high"] = "low"
    subscription_type: Literal["free", "premium", "family", "student", "unknown"] = "unknown"
    user_persona_signals: list[str] = Field(default_factory=list)
    is_discovery_related: bool = False
    confidence: float = Field(ge=0.0, le=1.0, default=0.5)

    @field_validator(
        "secondary_issues",
        "emotions",
        "listening_context",
        "mentioned_features",
        "feature_requests",
        "pain_points",
        "behaviors",
        "user_persona_signals",
        mode="before",
    )
    @classmethod
    def coerce_list(cls, value):
        if value is None:
            return []
        if isinstance(value, str):
            return [value] if value else []
        return value


class BatchExtractionResponse(BaseModel):
    extractions: list[ReviewExtraction]

    @classmethod
    def from_llm_payload(cls, payload) -> "BatchExtractionResponse":
        if isinstance(payload, dict):
            if "extractions" in payload:
                items = payload["extractions"]
            elif "reviews" in payload:
                items = payload["reviews"]
            else:
                items = [payload]
        elif isinstance(payload, list):
            items = payload
        else:
            raise ValueError("Unexpected LLM extraction payload shape")
        return cls(extractions=[ReviewExtraction.model_validate(item) for item in items])


class TranslatedReview(BaseModel):
    review_id: str
    detected_language: str
    text_en: str
