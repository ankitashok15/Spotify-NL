# Phase 4 — RAG Q&A

Hybrid retrieval + **Google Gemini** grounded answers with mandatory citations.

## Prerequisites

- Phase 1 reviews in PostgreSQL
- Phase 2 structured extraction (recommended)
- Phase 3 vectors indexed in Qdrant (`embed` run)
- `GEMINI_API_KEY` in `.env`

## Setup

```powershell
cd "c:\Users\Hp\OneDrive\Desktop\Spotify NL\phases\phase-04-rag-qa"
..\..\.venv\Scripts\pip install -r requirements.txt
..\..\.venv\Scripts\python cli\query.py init-db
```

Ensure `.env` includes:

```env
GEMINI_MODEL_RAG=gemini-2.5-flash
QDRANT_URL=http://localhost:6333
```

## Ask from CLI

```powershell
..\..\.venv\Scripts\python cli\query.py ask "Why do users dislike Discover Weekly?"
```

## RAG API (port 8002)

```powershell
..\..\.venv\Scripts\python cli\serve.py
```

```http
POST http://localhost:8002/api/v1/query
Content-Type: application/json

{
  "question": "Why do free users struggle with music discovery?",
  "filters": { "subscription_type": "free", "rating_max": 3 }
}
```

## Pipeline

```
Question → Router → Enhancement → Dense + BM25 + SQL → RRF → Rerank → Context → Gemini → Citations
```

## Evaluation

- `tests/phase-04/eval_rag.json` — 20 starter questions
- `tests/phase-04/eval_citations.py` — citation scorer

## Exit criteria

- Answers cite only retrieved reviews
- Citation validation on every response
- Hybrid retrieval with metadata filters

See [REQUIREMENTS.md](./REQUIREMENTS.md).
