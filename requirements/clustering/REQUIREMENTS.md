# Clustering Requirements

**Phase:** 5  
**Source:** `src/clustering/`

## Approach

1. **Unsupervised:** HDBSCAN or K-Means on review embeddings
2. **Labeling:** LLM assigns human-readable theme name + description
3. **Taxonomy mapping:** Align to 12 seed discovery themes

## Seed themes

`repetitive_recommendations`, `poor_discover_weekly`, `playlist_fatigue`, `genre_repetition`, `poor_exploration`, `liked_songs_repetition`, `algorithm_bias`, `podcast_interference`, `missing_niche_artists`, `mood_mismatch`, `context_mismatch`, `discovery_stagnation`

## Modules

| Module | Responsibility |
|--------|----------------|
| `clusterer.py` | HDBSCAN/K-Means fit |
| `labeler.py` | LLM theme naming |
| `assigner.py` | Incremental assignment for new reviews |
| `taxonomy.py` | Seed theme mapping |

## Cluster output fields

`cluster_id`, `label`, `description`, `member_count`, `avg_rating`, `avg_thumbs_up`, `top_subscription_types`, `top_device_types`, `representative_review_ids`, `trend_30d`

## Schedule

- Full re-cluster: weekly
- Incremental assign: daily

## Output

- Tables: `clusters`, `cluster_memberships`
- State: `processing_state = CLUSTERED`
