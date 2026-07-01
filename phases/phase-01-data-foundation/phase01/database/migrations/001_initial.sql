-- Phase 1 initial schema (also created via SQLAlchemy init_db)

CREATE TABLE IF NOT EXISTS scrape_runs (
    id UUID PRIMARY KEY,
    run_type VARCHAR(50) NOT NULL,
    app_id VARCHAR(255) NOT NULL,
    reviews_target INTEGER,
    reviews_scraped INTEGER DEFAULT 0,
    reviews_new INTEGER DEFAULT 0,
    reviews_updated INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'running',
    gap_report JSONB,
    started_at TIMESTAMPTZ DEFAULT NOW(),
    ended_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS scrape_checkpoints (
    id UUID PRIMARY KEY,
    scrape_run_id UUID REFERENCES scrape_runs(id),
    sort_order VARCHAR(50) NOT NULL,
    lang VARCHAR(10) DEFAULT 'en',
    country VARCHAR(10) DEFAULT 'us',
    continuation_token TEXT,
    reviews_scraped_in_pass INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'in_progress',
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS reviews (
    id UUID PRIMARY KEY,
    external_review_id VARCHAR(255) NOT NULL UNIQUE,
    app_id VARCHAR(255) NOT NULL,
    author_hash VARCHAR(64),
    text_original TEXT,
    text_cleaned TEXT,
    rating INTEGER,
    thumbs_up INTEGER DEFAULT 0,
    device_type VARCHAR(50),
    app_version VARCHAR(50),
    review_created_at TIMESTAMPTZ,
    developer_reply TEXT,
    developer_reply_at TIMESTAMPTZ,
    is_spam BOOLEAN DEFAULT FALSE,
    is_near_duplicate BOOLEAN DEFAULT FALSE,
    processing_state VARCHAR(20) DEFAULT 'RAW',
    pipeline_version VARCHAR(20) DEFAULT '1.0',
    scrape_run_id UUID REFERENCES scrape_runs(id),
    collected_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_reviews_rating ON reviews(rating);
CREATE INDEX IF NOT EXISTS idx_reviews_review_created_at ON reviews(review_created_at);
CREATE INDEX IF NOT EXISTS idx_reviews_processing_state ON reviews(processing_state);

CREATE TABLE IF NOT EXISTS dedup_index (
    id UUID PRIMARY KEY,
    content_hash VARCHAR(64) NOT NULL UNIQUE,
    review_id UUID REFERENCES reviews(id),
    created_at TIMESTAMPTZ DEFAULT NOW()
);
