# Phase 5 — Clustering & Product Insights

Theme clustering, trend detection, and product intelligence from embedded reviews.

## Prerequisites

- Phase 3 vectors in Qdrant (`embed` completed)
- Phase 2 structured fields recommended
- PostgreSQL running

## Setup

```powershell
cd phases\phase-05-clustering-insights
..\..\.venv\Scripts\pip install -r requirements.txt
..\..\.venv\Scripts\python cli\insights.py init-db
```

## Run clustering

```powershell
..\..\.venv\Scripts\python cli\insights.py cluster --limit 100
..\..\.venv\Scripts\python cli\insights.py assign --limit 200
..\..\.venv\Scripts\python cli\insights.py insights
```

## API (port 8003)

```powershell
..\..\.venv\Scripts\python cli\serve.py
```

| Endpoint | Description |
|----------|-------------|
| `GET /api/v1/clusters` | List theme clusters |
| `GET /api/v1/clusters/{id}` | Cluster detail + members |
| `GET /api/v1/insights` | Generated insights |
| `GET /api/v1/trends` | Time-series by issue/cluster |

## Pipeline

```
Embeddings → K-Means/HDBSCAN → LLM labels → taxonomy map → insights → APIs
```

## Deferred

- React/Next.js dashboard (API-first delivery)
- Celery weekly scheduler (use CLI/cron for now)
- Full insight embedding to Qdrant (stub indexer)

See [REQUIREMENTS.md](./REQUIREMENTS.md).
