-- Phase 5: generated insights

CREATE TABLE IF NOT EXISTS insights (
    id UUID PRIMARY KEY,
    insight_type VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    summary TEXT NOT NULL,
    confidence FLOAT,
    evidence_document_ids JSONB,
    affected_personas JSONB,
    payload JSONB,
    generated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_insights_type ON insights(insight_type);
CREATE INDEX IF NOT EXISTS idx_insights_generated_at ON insights(generated_at);
