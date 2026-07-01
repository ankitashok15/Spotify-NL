# Phase 5 Requirements — Clustering & Insights

## Scope

Theme clustering, trend detection, and actionable product intelligence from the full review corpus.

## Functional requirements

### FR-5.1 Clustering

- [ ] HDBSCAN / K-Means on review embeddings
- [ ] LLM theme labeling per cluster
- [ ] Map to seed taxonomy (12 discovery themes)
- [ ] Incremental assignment for new reviews
- [ ] Update `processing_state` to `CLUSTERED`

### FR-5.2 Cluster API

- [ ] `GET /api/v1/clusters` — list themes with stats
- [ ] `GET /api/v1/clusters/{id}` — detail + sample reviews

### FR-5.3 Insight generation

- [ ] Top recurring complaints
- [ ] Emerging issues (30-day growth)
- [ ] Feature request frequency
- [ ] Root cause summaries with evidence IDs
- [ ] Segment analysis (free vs premium, device)

### FR-5.4 Trends API

- [ ] `GET /api/v1/trends` — time-series per theme/issue
- [ ] `GET /api/v1/insights` — generated insight records

### FR-5.5 Dashboard

- [ ] Top 10 themes with drill-down
- [ ] Sentiment/emotion per theme
- [ ] Rating distribution per cluster
- [ ] Timeline of complaint volume

## Exit criteria

- 12 seed themes with >100 reviews each (on full corpus)
- Weekly insight reports without manual intervention
- Dashboard backed by real review evidence
