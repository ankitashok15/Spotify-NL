# Phase 6 — Agentic Workflows & Production Scale

Multi-step agent orchestrator, incremental ingestion, Redis cache, and production deployment assets.

## Prerequisites

- Phases 1–5 implemented
- PostgreSQL, Qdrant, Redis (for workers/cache)
- `GEMINI_API_KEY` in repo `.env` (optional — heuristic planner works without it)

## Setup

```powershell
cd phases\phase-06-agentic-scale
..\..\.venv\Scripts\pip install -r requirements.txt
..\..\.venv\Scripts\python cli\agent.py init-db
```

## Agent CLI

```powershell
..\..\.venv\Scripts\python cli\agent.py query "What discovery issues do free phone users report most, and how has that changed in 2026?" --debug
..\..\.venv\Scripts\python cli\agent.py pipeline --extract-limit 100 --embed-limit 100 --assign-limit 100
..\..\.venv\Scripts\python cli\agent.py pipeline --weekly
```

From repo root: `python scripts/agent.py query "..."`

## API (port 8004)

```powershell
..\..\.venv\Scripts\python cli\serve.py
```

| Endpoint | Method | Description |
|----------|--------|-------------|
| `POST /api/v1/agent/query` | POST | Multi-step agent Q&A with citations |
| `GET /health` | GET | Health check |

Optional auth: set `API_KEY` in `.env`, pass `X-API-Key` header.

## Workers (Celery + Redis)

```powershell
# Terminal 1 — worker
celery -A phase06.orchestration.celery_app:celery_app worker --loglevel=INFO

# Terminal 2 — beat (daily scrape + pipeline)
celery -A phase06.orchestration.celery_app:celery_app beat --loglevel=INFO
```

## Production compose

```powershell
docker compose -f docker-compose.prod.yml up -d
```

See [RUNBOOK.md](./RUNBOOK.md) and [IMPLEMENTATION.md](./IMPLEMENTATION.md).
