_EXTRACTION_SYSTEM = """You are a product analyst for Spotify Google Play reviews.
Focus on music discovery, recommendations, playlists, and personalization pain points.

Extract structured JSON for each review. Use snake_case issue and feature identifiers.
Examples for primary_issue: unwanted_recommendations_in_playlists, repetitive_recommendations,
poor_discover_weekly, skip_limit_frustration, algorithm_not_learning_taste, none.

Set is_discovery_related=true when the review mentions recommendations, discovery, playlists,
algorithm, taste profile, Discover Weekly, Release Radar, Daily Mix, or similar.

Return a JSON object: {"extractions": [ ... one object per review ... ]}
Each extraction must include review_id exactly as provided.
"""

_EXTRACTION_USER_TEMPLATE = """Analyze these Spotify Google Play reviews and return structured extractions.

Reviews:
{reviews_json}

Required fields per review:
review_id, summary, primary_issue, secondary_issues, emotions, sentiment (overall, toward_product, toward_feature),
recommendation_quality, user_intent, listening_context, mentioned_features, feature_requests, pain_points,
behaviors, severity, urgency, subscription_type, user_persona_signals, is_discovery_related, confidence
"""


def build_extraction_prompt(reviews_payload: list[dict]) -> str:
    import json

    return _EXTRACTION_USER_TEMPLATE.format(
        reviews_json=json.dumps(reviews_payload, ensure_ascii=False, indent=2),
    )


def extraction_system_prompt() -> str:
    return _EXTRACTION_SYSTEM
