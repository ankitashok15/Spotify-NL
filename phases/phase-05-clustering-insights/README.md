# Phase 5 — Clustering & Product Insights

**Goal:** Group reviews into discovery themes, detect trends, and generate actionable product intelligence.

## Related requirements

- [requirements/clustering](../../requirements/clustering/REQUIREMENTS.md)
- [requirements/insights](../../requirements/insights/REQUIREMENTS.md)

## Source code

- `phase05/clustering/` — K-Means/HDBSCAN, LLM labeler, taxonomy, incremental assigner
- `phase05/insights/` — aggregator, emerging issues, trends, root cause, reporter
- `phase05/api/` — `/clusters`, `/insights`, `/trends`
- `cli/insights.py` — init-db, cluster, assign, insights
- `cli/serve.py` — API on port 8003

## Prerequisite

Phase 3 embeddings indexed in Qdrant. Phase 2 structured fields strongly recommended.

See [RUNBOOK.md](./RUNBOOK.md) and [REQUIREMENTS.md](./REQUIREMENTS.md).
