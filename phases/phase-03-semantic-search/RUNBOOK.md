# Phase 3 — Semantic Search

Embed reviews with **Google Gemini** (`text-embedding-004`), index in **Qdrant**, and search via REST API.

## Prerequisites

- Phase 1 reviews in PostgreSQL
- Phase 2 structured fields recommended (richer embeddings)
- `GEMINI_API_KEY` in `.env`
- Docker running (PostgreSQL on 5433, Qdrant on 6333)

## Setup

```powershell
cd "c:\Users\Hp\OneDrive\Desktop\Spotify NL"

# Start Qdrant
cd phases\phase-03-semantic-search
docker compose up -d

# Install deps
..\..\.venv\Scripts\pip install -r requirements.txt

# Create collection
..\..\.venv\Scripts\python cli\embed.py init-qdrant
```

Add to `.env`:

```env
QDRANT_URL=http://localhost:6333
GEMINI_EMBEDDING_MODEL=text-embedding-004
```

## Embed & index

```powershell
..\..\.venv\Scripts\python cli\embed.py embed --limit 50 --batch-size 10
..\..\.venv\Scripts\python cli\embed.py status
```

From repo root:

```powershell
.\.venv\Scripts\python scripts\index_vectors.py embed --limit 50
```

Processing states: `EXTRACTED → EMBEDDED → INDEXED`

## Search API

```powershell
..\..\.venv\Scripts\python cli\serve.py
```

```http
POST http://localhost:8001/api/v1/search
Content-Type: application/json

{
  "query": "users complaining about repetitive Discover Weekly",
  "filters": {
    "rating_max": 3,
    "subscription_type": "free"
  },
  "top_k": 20
}
```

Health: `GET http://localhost:8001/health`

## Evaluation

Test queries: `tests/phase-03/eval_search.json` (20 queries)

## Exit criteria

- Full corpus embedded and indexed in Qdrant
- Metadata filters: rating, subscription, date range
- Paraphrase matching (e.g. "same songs" ≈ "recommendations never change")

See [REQUIREMENTS.md](./REQUIREMENTS.md).
