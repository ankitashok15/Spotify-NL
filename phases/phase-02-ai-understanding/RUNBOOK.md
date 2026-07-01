# Phase 2 — AI Understanding

Run language detection, translation, and Google Gemini structured extraction on Phase 1 reviews.

## Prerequisites

- Phase 1 complete: reviews in PostgreSQL (`processing_state = CLEANED`)
- `GEMINI_API_KEY` set in repo root `.env`
- PostgreSQL running

## Setup

```powershell
cd "c:\Users\Hp\OneDrive\Desktop\Spotify NL"
.\.venv\Scripts\pip install -r requirements.txt

cd phases\phase-02-ai-understanding
..\..\.venv\Scripts\python cli\extract.py init-db
```

## Run extraction

```powershell
# Process up to 100 reviews (batch size 25)
..\..\.venv\Scripts\python cli\extract.py extract --limit 100 --batch-size 25

# Check progress
..\..\.venv\Scripts\python cli\extract.py status
```

From repo root:

```powershell
.\.venv\Scripts\python scripts\extract.py extract --limit 50
```

## Pipeline flow

```
reviews (CLEANED) → language detect → translate (Gemini) → Gemini extract → structured_reviews
```

Processing states: `CLEANED → TRANSLATED → EXTRACTED`

## Output tables

| Table | Purpose |
|-------|---------|
| `structured_reviews` | LLM-extracted fields per review |
| `extraction_cache` | Content-hash cache to reduce API cost |

## Analytics

```powershell
psql $env:DATABASE_URL -f scripts\analytics_issues.sql
```

## Exit criteria

- 90%+ schema validity on 500-review sample
- `is_discovery_related` tagged correctly
- SQL filters on `subscription_type`, `primary_issue`, `device_type`

See [REQUIREMENTS.md](./REQUIREMENTS.md) and [requirements/llm](../../requirements/llm/REQUIREMENTS.md).
