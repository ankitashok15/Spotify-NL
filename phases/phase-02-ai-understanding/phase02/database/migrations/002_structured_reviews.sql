-- Phase 2: structured extraction tables

CREATE TABLE IF NOT EXISTS structured_reviews (
    id UUID PRIMARY KEY,
    review_id UUID NOT NULL UNIQUE REFERENCES reviews(id),
    detected_language VARCHAR(10),
    text_en TEXT,
    summary TEXT,
    primary_issue VARCHAR(255),
    secondary_issues JSONB,
    emotions JSONB,
    sentiment JSONB,
    recommendation_quality VARCHAR(50),
    user_intent VARCHAR(50),
    listening_context JSONB,
    mentioned_features JSONB,
    feature_requests JSONB,
    pain_points JSONB,
    behaviors JSONB,
    severity VARCHAR(20),
    urgency VARCHAR(20),
    subscription_type VARCHAR(50),
    user_persona_signals JSONB,
    is_discovery_related BOOLEAN DEFAULT FALSE,
    confidence FLOAT,
    metadata_enrichment JSONB,
    extraction_model VARCHAR(100),
    content_hash VARCHAR(64),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_structured_reviews_primary_issue ON structured_reviews(primary_issue);
CREATE INDEX IF NOT EXISTS idx_structured_reviews_subscription_type ON structured_reviews(subscription_type);
CREATE INDEX IF NOT EXISTS idx_structured_reviews_is_discovery ON structured_reviews(is_discovery_related);
CREATE INDEX IF NOT EXISTS idx_structured_reviews_content_hash ON structured_reviews(content_hash);

CREATE TABLE IF NOT EXISTS extraction_cache (
    id UUID PRIMARY KEY,
    content_hash VARCHAR(64) NOT NULL UNIQUE,
    extraction_payload JSONB NOT NULL,
    model_name VARCHAR(100),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_extraction_cache_content_hash ON extraction_cache(content_hash);
