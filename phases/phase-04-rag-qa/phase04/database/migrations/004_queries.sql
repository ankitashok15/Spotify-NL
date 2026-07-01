-- Phase 4: RAG query audit log

CREATE TABLE IF NOT EXISTS queries (
    id UUID PRIMARY KEY,
    question TEXT NOT NULL,
    answer TEXT,
    intent VARCHAR(50),
    search_query TEXT,
    filters JSONB,
    citations JSONB,
    confidence FLOAT,
    reviews_considered INTEGER,
    reviews_cited INTEGER,
    took_ms FLOAT,
    citation_valid BOOLEAN DEFAULT TRUE,
    warnings JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_queries_created_at ON queries(created_at);
