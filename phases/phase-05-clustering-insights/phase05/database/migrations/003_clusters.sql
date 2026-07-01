-- Phase 5: clusters and cluster memberships

CREATE TABLE IF NOT EXISTS clusters (
    id UUID PRIMARY KEY,
    cluster_key VARCHAR(100) NOT NULL UNIQUE,
    label VARCHAR(255) NOT NULL,
    description TEXT,
    taxonomy_theme_id VARCHAR(100),
    member_count INTEGER DEFAULT 0,
    avg_rating FLOAT,
    avg_thumbs_up FLOAT,
    top_subscription_types JSONB,
    top_device_types JSONB,
    representative_review_ids JSONB,
    centroid JSONB,
    trend_30d FLOAT,
    stats JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_clusters_taxonomy_theme_id ON clusters(taxonomy_theme_id);

CREATE TABLE IF NOT EXISTS cluster_memberships (
    id UUID PRIMARY KEY,
    cluster_id UUID REFERENCES clusters(id),
    review_id UUID REFERENCES reviews(id) UNIQUE,
    assigned_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_cluster_memberships_cluster_id ON cluster_memberships(cluster_id);
CREATE INDEX IF NOT EXISTS idx_cluster_memberships_review_id ON cluster_memberships(review_id);
