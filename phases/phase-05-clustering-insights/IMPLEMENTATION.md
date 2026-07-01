# Phase 5 Implementation Summary

**Status:** Code complete (API-first). Dashboard and Celery scheduler deferred.

This file maps [docs/ragarchitecture.md](../../docs/ragarchitecture.md) Phase 5 and [src/implementationplan.md](../../src/implementationplan.md) §8 to the delivered code under `phases/phase-05-clustering-insights/`.

---

## Folder layout

```
phases/phase-05-clustering-insights/
├── phase05/
│   ├── clustering/          # K-Means/HDBSCAN, LLM labeler, taxonomy, assigner
│   ├── insights/            # Aggregator, emerging, trends, root cause, reporter
│   ├── database/            # clusters, cluster_memberships, insights models
│   ├── api/                   # FastAPI routes (port 8003)
│   ├── pipeline.py            # ClusteringPipeline, InsightsPipeline, IncrementalPipeline
│   └── shared/config.py
├── cli/
│   ├── insights.py            # init-db | cluster | assign | insights
│   └── serve.py               # uvicorn on :8003
├── tests/phase-05/            # Unit tests (taxonomy, stats aggregation)
├── RUNBOOK.md
├── REQUIREMENTS.md
└── IMPLEMENTATION.md          # This file
```

---

## Sprint 5.1 — Clustering

| Task | File | Notes |
|------|------|-------|
| 5.1.1 HDBSCAN/K-Means | `phase05/clustering/clusterer.py` | Scrolls Qdrant collection; `CLUSTER_ALGORITHM=kmeans\|hdbscan` |
| 5.1.2 LLM theme labeler | `phase05/clustering/labeler.py` | Gemini JSON; heuristic fallback without API key |
| 5.1.3 Seed taxonomy (12 themes) | `phase05/clustering/taxonomy.py` | Keyword + primary_issue mapping |
| 5.1.4 Incremental assigner | `phase05/clustering/assigner.py` | Nearest-centroid for new vectors |
| 5.1.5 DB migrations | `phase05/database/migrations/003_clusters.sql`, `005_insights.sql` | Also via SQLAlchemy `init_phase5_tables()` |
| 5.1.6 Celery weekly job | — | **Deferred** — use CLI + cron/Task Scheduler |

**Pipeline:** `ClusteringPipeline.run_full()` → load vectors → fit → label → root cause → persist memberships → `processing_state=CLUSTERED`.

---

## Sprint 5.2 — Insights engine

| Task | File | Notes |
|------|------|-------|
| 5.2.1 Top complaints | `phase05/insights/aggregator.py` | SQL over `structured_reviews` |
| 5.2.2 Emerging issues | `phase05/insights/emerging.py` | 30-day growth vs prior window |
| 5.2.3 Trend analyzer | `phase05/insights/trends.py` | Monthly issue + cluster series |
| 5.2.4 Root cause | `phase05/insights/root_cause.py` | LLM synthesis with evidence IDs |
| 5.2.5 Opportunities | `phase05/insights/opportunities.py` | Feature request frequency |
| 5.2.6 Weekly report | `phase05/insights/reporter.py` | Builds + persists insight rows |
| 5.2.7 Insights table | `phase05/database/models.py` (`Insight`) | Types: top_complaint, emerging_issue, feature_request, weekly_report |

**Pipeline:** `InsightsPipeline.run()` → `InsightReporter.build_weekly_report()` → `persist_insights()` → stub indexer.

---

## Sprint 5.3 — API

| Endpoint | File | Port |
|----------|------|------|
| `GET /api/v1/clusters` | `phase05/api/routes/clusters.py` | 8003 |
| `GET /api/v1/clusters/{id}` | same | |
| `GET /api/v1/insights` | `phase05/api/routes/insights.py` | |
| `GET /api/v1/trends` | `phase05/api/routes/trends.py` | |
| `GET /health` | `phase05/api/main.py` | |

**Deferred:** React/Next.js dashboard (`frontend/`). **Stub:** `phase05/insights/indexer.py` (Qdrant insight embeddings for Phase 6 RAG).

---

## CLI usage

```powershell
cd phases\phase-05-clustering-insights
..\..\scripts\insights.py init-db
..\..\scripts\insights.py cluster --limit 100
..\..\scripts\insights.py assign --limit 200
..\..\scripts\insights.py insights
..\..\phases\phase-05-clustering-insights\cli\serve.py
```

Or from repo root: `python scripts/insights.py cluster`

---

## Prerequisites

1. **Phase 3** — vectors indexed in Qdrant (`spotify_reviews` collection)
2. **Phase 2** — `structured_reviews` for SQL-based insights (aggregator, emerging, trends)
3. **PostgreSQL** — `DATABASE_URL` in repo `.env`

---

## Environment variables (Phase 5)

| Variable | Default | Purpose |
|----------|---------|---------|
| `DATABASE_URL` | `postgresql://spotify:spotify@localhost:5433/spotify_nl` | Postgres |
| `GEMINI_API_KEY` | — | Cluster labeling + root cause (optional with fallbacks) |
| `GEMINI_MODEL` | `gemini-2.5-flash` | LLM |
| `QDRANT_URL` | `http://localhost:6333` | Vector source |
| `QDRANT_COLLECTION` | `spotify_reviews` | Collection name |
| `CLUSTER_ALGORITHM` | `kmeans` | `kmeans` or `hdbscan` |
| `CLUSTER_K` | `12` | K-Means clusters (aligns with 12 seed themes) |
| `EMERGING_GROWTH_THRESHOLD` | `0.20` | 20% growth for emerging issues |

---

## Exit criteria (runtime — not yet validated on full corpus)

| Criterion | Code ready | Runtime |
|-----------|------------|---------|
| 12 seed themes with >100 reviews each | Taxonomy + k=12 | Needs full embed + cluster run |
| Weekly insight reports automatic | CLI `insights` command | Wire to cron/Celery later |
| Dashboard drill-down | API returns evidence IDs | UI deferred |
| Trend API time-series | `GET /api/v1/trends` | Needs clustered + dated reviews |

---

## Tests

```powershell
python -m pytest tests/phase-05/ -v
```

Covers: 12 seed themes, taxonomy mapping, cluster stat aggregation.
