# API Requirements

**Phases:** 1–6 (cumulative)  
**Source:** `src/api/`

## Framework

- FastAPI
- Base path: `/api/v1`
- Auth: API key (internal teams)

## Endpoints by phase

### Phase 1 — Scrape & Reviews

| Method | Path | Description |
|--------|------|-------------|
| POST | `/scrape` | Trigger full or incremental scrape |
| GET | `/scrape/status` | Run progress + corpus validation |
| POST | `/ingest` | Manual CSV/JSON upload (dev) |
| GET | `/reviews` | List reviews (filters: rating, date, device) |
| GET | `/reviews/{id}` | Single review detail |

### Phase 3 — Search

| Method | Path | Description |
|--------|------|-------------|
| POST | `/search` | Semantic search (no LLM) |

### Phase 4 — RAG

| Method | Path | Description |
|--------|------|-------------|
| POST | `/query` | RAG Q&A with citations |

### Phase 5 — Intelligence

| Method | Path | Description |
|--------|------|-------------|
| GET | `/clusters` | Theme list with stats |
| GET | `/clusters/{id}` | Cluster detail + samples |
| GET | `/insights` | Generated insights |
| GET | `/trends` | Time-series data |

### Phase 6 — Agent

| Method | Path | Description |
|--------|------|-------------|
| POST | `/agent/query` | Multi-step agent Q&A |

## Project layout

```
src/api/
├── main.py              # FastAPI app
├── dependencies.py      # DB, auth
├── routes/
│   ├── scrape.py
│   ├── reviews.py
│   ├── search.py
│   ├── query.py
│   ├── clusters.py
│   ├── insights.py
│   ├── trends.py
│   └── agent.py
└── schemas/             # Request/response Pydantic models
```

## Response standards

- All RAG/agent responses include `citations[]` with `document_id`, `rating`, `excerpt`, `review_created_at`
- Never expose raw `user_name` — use `author_hash` only
- Paginated list endpoints: `limit`, `offset`, `total`
