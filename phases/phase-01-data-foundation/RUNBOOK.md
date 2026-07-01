# Phase 1 — Data Foundation Runbook

## Review window

**Default: last 6 months only.** Configure via:

```env
SCRAPE_MONTHS_BACK=6
```

Reviews with `review_created_at` before the cutoff are not scraped or stored.

## Setup

```bash
pip install -r requirements.txt
cp config\.env.example .env
cd phases\phase-01-data-foundation
docker compose up -d
python cli\scrape.py init-db
```

## Scrape commands

```bash
# Dev test (50 reviews, still respects 6-month window)
python cli\scrape.py scrape --limit 50

# Full 6-month window (3 sort passes)
python cli\scrape.py scrape --mode window

# Custom window (e.g. 3 months)
python cli\scrape.py scrape --months-back 3

# Validate: zero reviews older than window
python cli\scrape.py scrape --validate

# Resume interrupted scrape
python cli\scrape.py scrape --resume

# Incremental (new reviews since date, within window)
python cli\scrape.py scrape --since 2026-06-01
```

## API

```bash
python cli\serve.py
# POST /api/v1/scrape  { "mode": "window", "months_back": 6 }
# GET  /api/v1/scrape/validate
```
