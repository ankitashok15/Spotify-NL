# Scrape Requirements

**Phases:** 1 (full backfill), 6 (incremental)  
**Source:** `src/scrape/`

## Prerequisites & credentials

### Google Play API key — not required

This project does **not** use the official Google Play Developer API. You do **not** need:

- Google Cloud project with Play Developer API enabled
- OAuth credentials or service account
- Play Console access for `com.spotify.music`

Reviews are collected from **public Play Store data** using `google-play-scraper`, which paginates through the same data visible on the [Spotify listing page](https://play.google.com/store/apps/details?id=com.spotify.music).

### What you need for Phase 1

| Item | Required? | Notes |
|------|-----------|-------|
| Python 3.11+ | Yes | Runtime |
| `google-play-scraper` | Yes | `pip install google-play-scraper` |
| PostgreSQL | Yes | Persist scraped reviews |
| Internet access | Yes | Fetch from Play Store |
| Google Play API key | **No** | Not used |
| SerpAPI key | No | Optional fallback only |
| Paid subscription | No | Free to start |

### Access methods compared

| Method | API key | Cost | Full corpus? | Our usage |
|--------|---------|------|--------------|-----------|
| `google-play-scraper` | None | Free | Yes (paginated) | **Primary** |
| SerpAPI Google Play Reviews | `SERPAPI_KEY` | Paid per request | Yes | Fallback if blocked |
| CSV / JSON upload | None | Free | Depends on export | Dev/bootstrap |
| Google Play Developer API | OAuth + Console | Free for owners | Owner's app only | **Not used** |

### Environment variables (Phase 1)

```env
# Required to persist data
DATABASE_URL=postgresql://user:pass@localhost:5432/spotify_nl

# Optional — defaults shown
SPOTIFY_APP_ID=com.spotify.music
SCRAPE_DELAY_SECONDS=2
SCRAPE_BATCH_SIZE=200

# Optional fallback only
SERPAPI_KEY=
```

### Quick start (no API keys)

```bash
pip install google-play-scraper
python -c "from google_play_scraper import reviews, Sort; print(reviews('com.spotify.music', count=5))"
```

If this returns review objects, scraping works without any credentials.

### When you might need other keys

| Situation | Solution |
|-----------|----------|
| IP rate-limited or blocked | Increase `SCRAPE_DELAY_SECONDS`; add proxy rotation; try SerpAPI |
| SerpAPI fallback enabled | Set `SERPAPI_KEY` in `.env` |
| Persisting to database | Set `DATABASE_URL` |

LLM and embedding API keys are **not** needed for scraping — only for Phase 2 onward.

---

| Field | Value |
|-------|-------|
| App ID | `com.spotify.music` |
| URL | https://play.google.com/store/apps/details?id=com.spotify.music |
| Volume | Subset of listing (~last 6 months only) |
| Window | `SCRAPE_MONTHS_BACK=6` (rolling) |
| Coverage | All in-window reviews; zero rows older than cutoff |

## Components

| Module | Responsibility |
|--------|----------------|
| `scraper.py` | `GooglePlayReviewScraper` — main orchestrator |
| `pagination.py` | `continuation_token` loop, batch fetch (200/page) |
| `window.py` | 6-month cutoff date + in-window filtering |
| `validator.py` | Corpus count, dedup, distribution checks |
| `rate_limiter.py` | Delays, exponential backoff |
| `normalizer.py` | Raw Play Store JSON → `PlayStoreReviewDocument` |

## Sort passes

1. `NEWEST` — primary backfill
2. `RATING` — older/low-visibility reviews
3. `MOST_RELEVANT` — alternate ranking coverage

## CLI (`scripts/scrape.py`)

```
--mode full | incremental
--resume
--validate
--since YYYY-MM-DD
--limit N
--app-id com.spotify.music
```

## Dependencies

- `google-play-scraper` (primary)
- SerpAPI (fallback)

## Data output

- Raw batches → `data/raw/play_store/{batch_id}.json`
- Normalized rows → PostgreSQL `reviews` via upsert

## Non-functional

- Checkpoint every batch
- Idempotent upsert on `external_review_id`
- 1–3s between requests; backoff on 429/503
