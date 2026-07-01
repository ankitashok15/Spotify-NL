# Spotify NL — Unified Backend

Single FastAPI gateway exposing all phase APIs on **port 8080**.

## Endpoints

| Route | Description |
|-------|-------------|
| `GET /health` | Health check |
| `GET /api/v1/dashboard/stats` | Dashboard aggregates |
| `GET/POST /api/v1/reviews` | Review corpus |
| `POST /api/v1/search` | Semantic search |
| `POST /api/v1/query` | RAG Q&A |
| `GET /api/v1/clusters` | Theme clusters |
| `GET /api/v1/insights` | Generated insights |
| `GET /api/v1/trends` | Time-series |
| `POST /api/v1/agent/query` | Multi-step agent |
| `POST /api/v1/scrape` | Trigger scrape |

## Run

```powershell
# From repo root (Postgres + Qdrant must be running)
.\.venv\Scripts\python scripts\serve_api.py
```

API docs: http://localhost:8080/docs
