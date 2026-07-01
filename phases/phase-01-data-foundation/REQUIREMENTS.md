# Phase 1 Requirements — Data Foundation

## Scope

Scrape **Google Play reviews from the last 6 months** for `com.spotify.music` from [Google Play](https://play.google.com/store/apps/details?id=com.spotify.music), clean, and store in PostgreSQL.

> **No Google Play API key required.** See [requirements/scrape](../../requirements/scrape/REQUIREMENTS.md).  
> **Window:** `SCRAPE_MONTHS_BACK=6` (default). Reviews older than the cutoff are **not stored**.

## Functional requirements

### FR-1.1 Rolling window scraping

- [x] Paginate reviews via `google-play-scraper` using `continuation_token`
- [x] Stop each pass when batch reviews are older than 6-month cutoff
- [x] Run three sort passes: `NEWEST`, `RATING`, `MOST_RELEVANT` (in-window only)
- [x] Upsert on `external_review_id`; no duplicate rows
- [x] Checkpoint after every batch; resume from last token on failure
- [x] Store raw JSON batches in `data/raw/play_store/`
- [x] Configurable via `SCRAPE_MONTHS_BACK` env or `--months-back` CLI flag

### FR-1.2 Corpus validation

- [x] Verify zero reviews with `review_created_at < cutoff`
- [x] Verify `COUNT(*) == COUNT(DISTINCT external_review_id)`
- [x] Rating distribution sanity check on in-window reviews
- [x] Write results to `scrape_runs.gap_report` with window metadata

### FR-1.3 Cleaning pipeline

- [x] Normalize unicode and whitespace into `text_cleaned`
- [x] Preserve `text_original` always
- [x] Tag spam (`is_spam`) and near-duplicates (`is_near_duplicate`); **do not delete**
- [x] Keep rating-only reviews with null `text_cleaned`

### FR-1.4 Database persistence

- [x] Tables: `reviews`, `scrape_runs`, `scrape_checkpoints`, `dedup_index`
- [x] Processing state: `RAW → CLEANED`

### FR-1.5 CLI

- [x] `scrape.py scrape --mode window` — 6-month window backfill
- [x] `scrape.py scrape --months-back N` — custom window
- [x] `scrape.py scrape --resume` — continue from checkpoint
- [x] `scrape.py scrape --validate` — window + dedup validation
- [x] `scrape.py scrape --since YYYY-MM-DD` — incremental fetch
- [x] `scrape.py scrape --limit N` — dev subset

### FR-1.6 API (Phase 1)

- [x] `POST /api/v1/scrape` — trigger scrape (window default)
- [x] `GET /api/v1/scrape/status` — progress + validation
- [x] `POST /api/v1/ingest` — manual CSV/JSON (dev only; in-window only)
- [x] `GET /api/v1/reviews` — list with filters
- [x] `GET /api/v1/reviews/{id}` — single review

## Exit criteria

- All reviews in DB are within the last 6 months
- Zero duplicate `external_review_id`
- Resume works without data loss
- All in-window scraped reviews retained (no deletion at ingest)
