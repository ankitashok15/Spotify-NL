CREATE TABLE IF NOT EXISTS agent_queries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    confidence DOUBLE PRECISION,
    steps INTEGER DEFAULT 0,
    tool_trace JSONB,
    citations JSONB,
    took_ms DOUBLE PRECISION,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_agent_queries_created_at ON agent_queries (created_at DESC);
