# AI-Powered Review Discovery Engine — RAG Architecture

## 1. Overview

This document defines the **phase-wise technical architecture** for an AI-Powered Review Discovery Engine scoped to a **single data source**: public user reviews of **Spotify: Music and Podcasts** on the **Google Play Store**.

| Field | Value |
|-------|-------|
| **App** | Spotify: Music and Podcasts |
| **Developer** | Spotify AB |
| **Package ID** | `com.spotify.music` |
| **Play Store URL** | [https://play.google.com/store/apps/details?id=com.spotify.music](https://play.google.com/store/apps/details?id=com.spotify.music) |
| **Review volume (listing)** | ~35M+ total on Play Store |
| **Review window** | **Last 6 months only** (rolling) |
| **Overall rating** | 4.3 stars |

The system's **first task** is to **scrape Google Play reviews from the last 6 months** for Spotify (`com.spotify.music`) from [the official listing](https://play.google.com/store/apps/details?id=com.spotify.music). Reviews older than the rolling 6-month window are **not collected or stored**. Once the windowed corpus is collected, the pipeline transforms unstructured feedback into structured product intelligence and exposes it through **Retrieval-Augmented Generation (RAG)** for evidence-backed, conversational querying about music discovery and recommendation pain points.

> **Scope constraint:** No Reddit, App Store, social media, or other sources in this version. The architecture is designed for one connector first, with a clean interface so additional sources can be added later without redesign.

> **Corpus constraint:** The knowledge base represents **Google Play reviews from the last 6 months** for `com.spotify.music`. Reviews older than `SCRAPE_MONTHS_BACK` (default: 6) are skipped at ingestion. Downstream relevance filters may tag discovery-related reviews, but **no in-window review is discarded at ingest time**.

### 1.1 Design Principles

| Principle | Description |
|-----------|-------------|
| **Single-source focus** | All pipelines, schemas, and filters are optimized for Google Play review structure (star rating, device type, helpful votes, developer replies). |
| **Evidence-first** | Every AI insight cites the original Play Store review with rating, date, and review ID. |
| **Semantic over lexical** | Cluster and retrieve by meaning — "same songs" and "recommendations never change" map to the same theme. |
| **Multi-signal extraction** | One review can yield sentiment, emotion, feature request, pain point, and subscription signals simultaneously. |
| **Grounded generation** | RAG answers are constrained to retrieved reviews; citations are mandatory. |
| **Phase-gated delivery** | Each phase ships a working, testable increment before the next layer is built. |
| **Complete window** | Scrape all Play Store reviews within the rolling 6-month window; checkpointed, resumable, and validated for date compliance. |

---

## 2. Phase-Wise Architecture Overview

```
PHASE 1 — Data Foundation
  6-Month Window Scrape → Cleaning → PostgreSQL Store
       │
       ▼
PHASE 2 — AI Understanding
  Language Detection → Translation → Structured LLM Extraction
       │
       ▼
PHASE 3 — Semantic Search
  Embeddings → Vector DB → Semantic Search API
       │
       ▼
PHASE 4 — RAG Q&A
  Hybrid Retrieval → Reranking → Grounded Answers + Citations
       │
       ▼
PHASE 5 — Clustering & Insights
  Theme Clustering → Trend Analysis → Product Intelligence Dashboard
       │
       ▼
PHASE 6 — Agentic & Scale
  Multi-step Agent → Incremental Ingestion → Production Hardening
```

Each phase below includes: **goal**, **architecture diagram**, **components**, **deliverables**, and **exit criteria**.

---

## 2.1 Project Folder Structure

Implementation is organized into **phase folders** (delivery timeline) and **requirement domains** (technical components).

```
Spotify NL/
├── docs/
│   ├── problemstatement.md
│   └── ragarchitecture.md          # This document
│
├── phases/                          # Phase-gated delivery
│   ├── README.md
│   ├── phase-01-data-foundation/    # Scrape all reviews + PostgreSQL
│   ├── phase-02-ai-understanding/   # LLM extraction
│   ├── phase-03-semantic-search/    # Embeddings + search API
│   ├── phase-04-rag-qa/             # RAG Q&A with citations
│   ├── phase-05-clustering-insights/# Themes, trends, dashboard
│   └── phase-06-agentic-scale/      # Agent + production scale
│
├── requirements/                    # Cross-cutting domain specs
│   ├── README.md
│   ├── scrape/                      # Full corpus Google Play scraper
│   ├── database/                    # PostgreSQL, vector DB, schemas
│   ├── api/                         # REST endpoints (all phases)
│   ├── cleaning/                    # Normalization pipeline
│   ├── extraction/                  # Language + LLM structured output
│   ├── embedding/                   # Vector generation + indexing
│   ├── rag/                         # Hybrid retrieval + grounded Q&A
│   ├── clustering/                  # Theme discovery
│   ├── insights/                    # Trends + product intelligence
│   ├── agent/                       # Multi-step tool-calling agent
│   └── orchestration/               # Jobs, queues, deployment
│
├── src/                             # Implementation code
│   ├── scrape/                      # → requirements/scrape
│   ├── cleaning/                    # → requirements/cleaning
│   ├── database/                    # → requirements/database
│   │   ├── models/
│   │   ├── migrations/
│   │   └── repositories/
│   ├── api/                         # → requirements/api
│   │   ├── routes/
│   │   └── schemas/
│   ├── extraction/                  # → requirements/extraction
│   ├── embedding/                     # → requirements/embedding
│   ├── search/                        # Phase 3 semantic search
│   ├── rag/                           # → requirements/rag
│   ├── clustering/                    # → requirements/clustering
│   ├── insights/                      # → requirements/insights
│   ├── agent/                         # → requirements/agent
│   ├── orchestration/                 # → requirements/orchestration
│   └── shared/                        # Config, constants, utils
│
├── scripts/
│   └── scrape.py                      # Phase 1 CLI entry point
│
├── tests/
│   ├── phase-01/ … phase-06/          # Tests per phase
│
├── data/
│   └── raw/play_store/                # Raw scrape JSON batches
│
└── config/
    └── .env.example
```

### Phase → folder mapping

| Phase | Phase folder | Primary `src/` modules | Requirement docs |
|-------|--------------|------------------------|------------------|
| 1 | `phases/phase-01-data-foundation/` | `scrape`, `cleaning`, `database`, `api/routes` | `scrape`, `database`, `api`, `cleaning` |
| 2 | `phases/phase-02-ai-understanding/` | `extraction`, `database` | `extraction` |
| 3 | `phases/phase-03-semantic-search/` | `embedding`, `search`, `api/routes` | `embedding`, `database` |
| 4 | `phases/phase-04-rag-qa/` | `rag`, `api/routes` | `rag` |
| 5 | `phases/phase-05-clustering-insights/` | `clustering`, `insights`, `api/routes` | `clustering`, `insights` |
| 6 | `phases/phase-06-agentic-scale/` | `agent`, `orchestration`, `scrape` | `agent`, `orchestration`, `scrape` |

Each phase folder contains `README.md` (overview + links) and `REQUIREMENTS.md` (checklist + exit criteria).

---

## 3. Data Source Specification

### 3.1 Google Play Store — Spotify App

**Target listing:** [Spotify: Music and Podcasts on Google Play](https://play.google.com/store/apps/details?id=com.spotify.music)

The Play Store exposes rich, structured review metadata that the pipeline must preserve:

| Field | Description | Use in Pipeline |
|-------|-------------|-----------------|
| `review_id` | Unique review identifier | Deduplication, citation linking |
| `user_name` | Reviewer display name | Hash for privacy; no raw PII in outputs |
| `content` | Review text body | Primary NLP input |
| `score` | 1–5 star rating | Sentiment prior, filter dimension |
| `thumbs_up_count` | Helpful votes | Popularity / severity signal |
| `review_created_version` | App version at review time | Version regression analysis |
| `at` | Review timestamp | Trend analysis, time filters |
| `device` | Device metadata (Phone, Tablet, Watch, etc.) | Segment analysis |
| `reply_content` | Spotify developer reply (if any) | Separate document or linked metadata |
| `app_version` | Current app version on listing | Context for ingestion runs |

### 3.2 Sample Review Signals (from Play Store)

Real reviews on the listing illustrate the multi-signal extraction challenge:

| Review theme | Example signal |
|--------------|----------------|
| Free vs Premium | *"The free version is terrible… I pay for premium now"* |
| Recommendation interference | *"Recommendations into the playlists you're listening to"* |
| Pricing | *"Maybe lower the price instead of increasing an extra dollar every year"* |
| Ads | *"FIVE ads? That's unnecessary"* |
| App stability | *"Whenever I leave the app… it closes and turns my music off"* |
| Audiobook limits | *"Audiobooks are severely limited (15 hours with premium)"* |

The extraction layer must capture discovery/recommendation issues **and** adjacent signals (ads, pricing, stability) when they appear in the same review.

### 3.3 Rolling Window Review Scraping (Core Requirement)

The platform's data layer is built on reviews from a **rolling 6-month window** on Spotify's Google Play listing. Historical reviews older than 6 months are **out of scope** — this keeps the corpus recent, relevant, and manageable while still capturing millions of recent user voices.

#### 3.3.1 Scraping Objective

| Target | Detail |
|--------|--------|
| **App** | `com.spotify.music` — [Spotify: Music and Podcasts](https://play.google.com/store/apps/details?id=com.spotify.music) |
| **Scope** | Public reviews with `review_created_at` within the last **6 months** |
| **Window config** | `SCRAPE_MONTHS_BACK=6` (env var; rolling 180-day cutoff) |
| **Expected volume** | Subset of ~35M total listing reviews (recent months only) |
| **Coverage goal** | All in-window reviews captured via paginated scrape; zero reviews older than 6 months in DB |
| **Retention** | 100% of in-window scraped reviews stored; no dropping at scrape time |

#### 3.3.2 Scraping Architecture

```
┌──────────────────────────────────────────────────────────────────────────┐
│                    6-MONTH WINDOW SCRAPE ORCHESTRATOR                     │
│  cutoff = now - 6 months │ Checkpoint manager │ Rate limiter             │
└─────────────────────────────────┬────────────────────────────────────────┘
                                  │
         ┌────────────────────────┼────────────────────────┐
         ▼                        ▼                        ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Scrape Worker 1  │    │ Scrape Worker 2  │    │ Scrape Worker N  │
│ sort=newest      │    │ sort=rating      │    │ sort=most_relevant│
│ continuation_token│   │ continuation_token│   │ continuation_token│
└────────┬────────┘    └────────┬────────┘    └────────┬────────┘
         │                      │                      │
         └──────────────────────┼──────────────────────┘
                                ▼
              ┌─────────────────────────────────────┐
              │  google-play-scraper                 │
              │  app_id = com.spotify.music          │
              │  paginate until reviews older than 6-month cutoff │
              └─────────────────┬───────────────────┘
                                │ RawReview batches (200/page)
                                ▼
              ┌─────────────────────────────────────┐
              │  Raw Object Store                    │
              │  data/raw/play_store/{batch_id}.json │
              └─────────────────┬───────────────────┘
                                ▼
              ┌─────────────────────────────────────┐
              │  Deduplication + PostgreSQL upsert   │
              │  ON CONFLICT (external_review_id)    │
              └─────────────────┬───────────────────┘
                                ▼
              ┌─────────────────────────────────────┐
              │  scrape_checkpoints + scrape_runs    │
              └─────────────────────────────────────┘
```

#### 3.3.3 Scraping Strategy

Google Play does not expose a date-filtered review API. The scraper **paginates the review stream** and **stops when reviews fall before the 6-month cutoff** (`SCRAPE_MONTHS_BACK=6`).

**Primary tool:** [`google-play-scraper`](https://github.com/JoMingyu/google-play-scraper) (Python)

```python
from google_play_scraper import reviews, Sort

result, continuation_token = reviews(
    "com.spotify.music",
    lang="en",        # default pass
    country="us",
    sort=Sort.NEWEST,
    count=200,        # max per page
)

while continuation_token:
    result, continuation_token = reviews(
        "com.spotify.music",
        continuation_token=continuation_token
    )
  # skip reviews where review.at < cutoff_date (6 months ago)
  # stop pass when entire batch is older than cutoff
    # persist in-window batch → checkpoint
```

**Multi-pass sort strategy** (maximize coverage — some reviews surface under different sort orders):

| Pass | Sort order | Purpose |
|------|------------|---------|
| 1 | `NEWEST` | Capture latest reviews; primary backfill stream |
| 2 | `RATING` | Surface older/low-visibility reviews |
| 3 | `MOST_RELEVANT` | Catch reviews ranked differently by Play Store |

Each pass maintains its own `continuation_token` checkpoint. Reviews deduplicated by `external_review_id` across passes — only new IDs are inserted.

**Multi-locale passes** (optional Phase 1 extension): Re-run with `lang` / `country` variants (`en`, `es`, `pt`, `de`, `fr`, etc.) to capture reviews written in non-English that may appear under locale-specific fetches. Deduplicate globally by `review_id`.

#### 3.3.4 Pagination & Checkpointing

Every scrape batch is **resumable** after failure or rate-limit interruption.

**Checkpoint record (`scrape_checkpoints`):**

```json
{
  "checkpoint_id": "uuid",
  "app_id": "com.spotify.music",
  "sort_order": "newest",
  "lang": "en",
  "country": "us",
  "continuation_token": "encoded_token...",
  "last_review_id": "gp_review_xyz",
  "reviews_scraped_in_pass": 1245000,
  "status": "in_progress",
  "updated_at": "2026-06-30T12:00:00Z"
}
```

| Rule | Behavior |
|------|----------|
| **Batch size** | 200 reviews per API call (library maximum) |
| **Checkpoint frequency** | After every successful batch |
| **Idempotency** | `UPSERT` on `external_review_id`; re-scraping is safe |
| **Resume** | On restart, load latest checkpoint per sort pass and continue from `continuation_token` |
| **Completion** | Pass marked `completed` when `continuation_token` is `null` |

#### 3.3.5 Rate Limiting & Reliability

| Control | Setting |
|---------|---------|
| Request delay | 1–3 seconds between batches (configurable) |
| Exponential backoff | On HTTP 429 / 503: wait 30s → 60s → 120s, then retry |
| Max retries per batch | 5; then mark batch failed and alert |
| Concurrent workers | 1 worker per sort pass (avoid IP throttling); scale passes, not threads |
| Proxy rotation | Optional for large backfill if IP-blocked |
| User-Agent | Rotate realistic browser user-agents |

**Fallback scrapers** (if primary library is blocked):

| Fallback | Use when |
|----------|----------|
| SerpAPI Google Play Reviews API | Primary scraper consistently rate-limited |
| Custom Play Store internal API client | Library unmaintained or broken |
| Pre-purchased review dataset | Emergency bootstrap only; still run live scraper to validate |

#### 3.3.6 Corpus Validation

After each scrape pass and after full backfill, validate completeness:

| Check | Method |
|-------|--------|
| **Count in window** | All stored reviews have `review_created_at >= cutoff` |
| **Zero out-of-window** | `COUNT(*) WHERE review_created_at < cutoff` must be 0 |
| **Duplicate check** | `COUNT(*) == COUNT(DISTINCT external_review_id)` |
| **Date range** | `MIN(review_created_at)` should be near 6-month cutoff |
| **Rating distribution** | Sanity check on in-window reviews |

**Acceptance threshold:** Zero reviews older than 6 months in DB; all in-window passes complete without error. Gap analysis logged in `scrape_runs.gap_report`.

#### 3.3.7 Scrape Run Lifecycle

```
PLANNED → RUNNING → [PAUSED] → COMPLETED
                  ↘ FAILED → RETRY (from checkpoint)
```

**`scrape_runs` table tracks each full backfill:**

| Column | Purpose |
|--------|---------|
| `run_id` | Unique scrape campaign ID |
| `run_type` | `full_backfill` \| `incremental` \| `pass_rating` |
| `reviews_target` | Expected total from Play Store listing |
| `reviews_scraped` | Running count |
| `reviews_new` | Inserts (excluding duplicates) |
| `reviews_updated` | Existing rows refreshed (e.g., thumbs_up changed) |
| `started_at` / `ended_at` | Duration tracking |
| `status` | `running` \| `completed` \| `failed` |
| `gap_report` | JSON: missing count, validation results |

#### 3.3.8 Incremental Scraping (Post-Backfill)

After the full corpus is collected, a **daily incremental job** fetches only new reviews:

1. Run `sort=NEWEST` pass until `review_created_at <= last_scraped_at`
2. Upsert new reviews; update `thumbs_up` / `developer_reply` on existing rows if changed
3. Enqueue new documents into the processing pipeline (Phase 2+)

Incremental runs are lightweight (typically hundreds–thousands of reviews/day vs millions in backfill).

#### 3.3.9 Estimated Scrape Timeline (6-month window)

| Window | Batch size | Delay | Approx. duration |
|--------|------------|-------|------------------|
| 6 months | 200/batch | 2s/batch | Hours to ~1 day (depends on recent review volume) |
| 3 sort passes | — | — | ~3× single pass; still far faster than full 35M backfill |

Actual duration depends on how many reviews Spotify received in the last 6 months and Play Store rate limits.

#### 3.3.10 Scraper Connector Interface

```
GooglePlayReviewScraper
├── scrape_all(app_id: "com.spotify.music") → ScrapeRun
│     Orchestrates all sort passes until corpus validation passes
├── scrape_pass(sort: Sort, lang: str, country: str) → ScrapePassResult
│     Single paginated stream with checkpointing
├── resume(checkpoint_id: str) → ScrapePassResult
│     Continue from saved continuation_token
├── scrape_incremental(since: datetime) → RawReview[]
│     Daily new-review fetch
├── validate_corpus() → ValidationReport
│     Count, dedup, distribution checks vs Play Store listing
├── get_app_metadata() → AppMetadata
│     Live review count, rating, version from listing page
└── normalize(raw) → PlayStoreReviewDocument
```

#### 3.3.11 Development vs Production Scraping

| Environment | Strategy |
|-------------|----------|
| **Development** | Scrape 1,000–10,000 reviews (`--limit 10000`) to test pipeline; use `--mock` fixtures for unit tests |
| **Staging** | Scrape 100K reviews across all sort passes; validate checkpoint resume |
| **Production** | `scrape_all()` with `SCRAPE_MONTHS_BACK=6`; validate zero out-of-window rows |

---

### 3.4 Supplementary Ingestion Methods

| Method | Priority | Notes |
|--------|----------|-------|
| **google-play-scraper** (Python library) | **Primary** | Full corpus pagination via `continuation_token` |
| **SerpAPI / third-party Play Store API** | Fallback | Rate-limited; use if primary scraper is blocked |
| **CSV / JSON manual upload** | Dev bootstrap | Pre-exported dumps for local testing only |
| **Scheduled incremental jobs** | Phase 6 | Daily fetch of new reviews since last `collected_at` |

---

### 3.5 Prerequisites & Credentials

#### Do you need a Google Play Store API key?

**No.** There is no public Google Play API key that lets third parties download all reviews for an app like Spotify. Phase 1 uses **public scraping** via the unofficial [`google-play-scraper`](https://github.com/JoMingyu/google-play-scraper) library — no Google account, OAuth, or Play Console access required.

| Access method | Google Play API key? | Who can use it | Used in this project? |
|---------------|----------------------|----------------|---------------------|
| **google-play-scraper** | No | Anyone (public data) | **Yes — primary** |
| **CSV / JSON manual upload** | No | Dev/testing | Yes — bootstrap only |
| **SerpAPI** (third-party) | No (uses **SerpAPI key**) | Anyone with SerpAPI account | Optional fallback |
| **Google Play Developer API** | OAuth + Play Console | **App owner only** (Spotify AB) | **No — not applicable** |

The **Google Play Developer API** (Google Cloud + OAuth) is for developers managing **their own** apps in Play Console (reply to reviews, view ratings). It cannot be used by an external team to bulk-fetch all public Spotify reviews.

#### Credentials by phase

| Phase | Required | Optional | Not required |
|-------|----------|----------|--------------|
| **1 — Scrape** | Python 3.11+, `google-play-scraper`, PostgreSQL | SerpAPI key (fallback) | Google Play API key |
| **2 — Extraction** | `GEMINI_API_KEY` | Google Translate API (optional) | Google Play API key |
| **3 — Embeddings** | `GEMINI_API_KEY` (text-embedding-004) | — | Google Play API key |
| **4 — RAG** | `GEMINI_API_KEY` | Cohere Rerank API key (optional) | Google Play API key |
| **5 — Insights** | `GEMINI_API_KEY` | — | Google Play API key |
| **6 — Production** | Redis URL, deployment secrets | Proxy service credentials | Google Play API key |

#### Phase 1 setup (scraping only)

```bash
pip install google-play-scraper psycopg2-binary sqlalchemy
```

No `.env` secrets are required to start scraping. Minimum environment:

| Variable | Required | Default | Purpose |
|----------|----------|---------|---------|
| `SPOTIFY_APP_ID` | No | `com.spotify.music` | Target app package ID |
| `DATABASE_URL` | Yes (to persist) | — | PostgreSQL connection string |
| `SCRAPE_MONTHS_BACK` | No | `6` | Rolling review window in months |
| `SCRAPE_DELAY_SECONDS` | No | `2` | Delay between pagination batches |

#### Optional credentials (later phases)

Copy `config/.env.example` to `.env` and fill in as each phase is built:

| Variable | Phase | Purpose |
|----------|-------|---------|
| `GEMINI_API_KEY` | 2–6 | LLM extraction, RAG, insights, agent ([Google AI Studio](https://aistudio.google.com/apikey)) |
| `GEMINI_MODEL` | 2–6 | Default model (e.g. `gemini-2.0-flash`) |
| `GEMINI_MODEL_RAG` | 4–6 | RAG / agent answers |
| `GEMINI_EMBEDDING_MODEL` | 3 | Embeddings (default: `text-embedding-004`) |
| `QDRANT_URL` / `QDRANT_API_KEY` | 3 | Vector database |
| `COHERE_API_KEY` | 4 | Reranking (optional) |
| `REDIS_URL` | 6 | Job queue for workers |

> **LLM provider:** This project uses **Google Gemini only** — not OpenAI or Anthropic.
| `SERPAPI_KEY` | No | — | Only if using SerpAPI fallback |

#### Rolling window default

All scrape modes use `SCRAPE_MONTHS_BACK=6` unless overridden. Reviews with `review_created_at` before `now - 6 months` are **skipped and not stored**.

Without an official API, scraping relies on polite access patterns:

- 1–3 second delay between batches (200 reviews per batch)
- Exponential backoff on HTTP 429 / 503
- Checkpoint/resume so interrupted runs do not restart from zero
- Optional proxy rotation only if IP throttling occurs at scale

See [requirements/scrape/REQUIREMENTS.md](../requirements/scrape/REQUIREMENTS.md) for full scrape prerequisites.

---

All phases share a single internal schema regardless of how reviews arrive.

```json
{
  "document_id": "uuid",
  "source": "google_play",
  "app_id": "com.spotify.music",
  "app_name": "Spotify: Music and Podcasts",
  "external_review_id": "gp_review_abc123",
  "author_hash": "sha256(...)",
  "text_original": "The free version is terrible. Bro you can only do 6 skips per hour...",
  "text_en": "The free version is terrible. Bro you can only do 6 skips per hour...",
  "language": "en",
  "rating": 2,
  "thumbs_up": 27,
  "device_type": "phone",
  "app_version": "9.0.12",
  "review_created_at": "2026-04-21T00:00:00Z",
  "collected_at": "2026-06-30T08:00:00Z",
  "developer_reply": null,
  "play_store_url": "https://play.google.com/store/apps/details?id=com.spotify.music",
  "processing_state": "INDEXED",
  "pipeline_version": "1.0"
}
```

**Processing state machine (all phases):**

```
RAW → CLEANED → TRANSLATED → EXTRACTED → EMBEDDED → CLUSTERED → INDEXED
```

---

# PHASE 1 — Data Foundation

## Goal

**Scrape all reviews from the last 6 months** of Spotify (`com.spotify.music`) from Google Play, clean and deduplicate them, and persist to PostgreSQL.

## Architecture

```
┌──────────────────────────────────────────────────────────────────────────┐
│              FULL CORPUS SCRAPE ORCHESTRATOR                              │
│  scrape_all() │ 6-month cutoff │ 3 sort passes │ corpus validation      │
│  app_id: com.spotify.music                                                │
└────────────────────────────┬─────────────────────────────────────────────┘
                             │ RawReview[] (batched, 200/page)
                             ▼
┌──────────────────────────────────────────────────────────────────────────┐
│              RAW OBJECT STORE + CHECKPOINTS                               │
│  data/raw/play_store/ │ scrape_checkpoints │ scrape_runs                 │
└────────────────────────────┬─────────────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────────────┐
│              CLEANING & NORMALIZATION                                       │
│  Dedup (by review_id) │ Spam tag │ HTML strip │ Unicode normalize        │
│  ⚠ No review dropped — all scraped reviews retained                      │
└────────────────────────────┬─────────────────────────────────────────────┘
                             │ CleanedReview[]
                             ▼
┌──────────────────────────────────────────────────────────────────────────┐
│              POSTGRESQL (System of Record)                                │
│  reviews │ scrape_checkpoints │ scrape_runs │ dedup_index                │
└──────────────────────────────────────────────────────────────────────────┘
```

## Components

### 1.1 Full Corpus Scrape Service

The scrape service is the **primary Phase 1 deliverable**. It must collect every review from the Play Store listing.

| Step | Action |
|------|--------|
| 1 | Fetch `SCRAPE_MONTHS_BACK` cutoff date (default: 6 months ago) |
| 2 | Launch scrape passes: `NEWEST` → `RATING` → `MOST_RELEVANT` |
| 3 | Paginate; **stop each pass when batch reviews are older than cutoff** |
| 4 | Checkpoint after every batch; resume on failure |
| 5 | Upsert into PostgreSQL (`ON CONFLICT external_review_id DO UPDATE`) |
| 6 | Run `validate_corpus()` — confirm zero reviews older than 6 months |
| 7 | Log results in `scrape_runs`; repeat passes if gap > 0.5% |

**CLI commands:**

```bash
# 6-month window backfill (default)
python scrape.py --app-id com.spotify.music --mode window

# Same as window (--mode full is legacy alias)
python scrape.py --app-id com.spotify.music --mode full

# Custom window (e.g. 3 months)
python scrape.py --months-back 3

# Resume interrupted scrape from last checkpoint
python scrape.py --app-id com.spotify.music --resume

# Dev/test — limited scrape
python scrape.py --app-id com.spotify.music --limit 10000

# Incremental — new reviews since date
python scrape.py --app-id com.spotify.music --since 2026-06-01

# Validate corpus completeness
python scrape.py --app-id com.spotify.music --validate
```

### 1.2 Cleaning Pipeline

Cleaning **tags and normalizes** reviews but does **not remove** them from the corpus. Relevance filtering (discovery-related) is deferred to Phase 2 extraction (`is_discovery_related` flag), not Phase 1.

| Step | Details |
|------|---------|
| Exact dedup | `external_review_id` unique constraint; upsert on re-scrape |
| Near-dedup flag | SimHash match → mark `is_near_duplicate`, keep both rows |
| Spam tag | Heuristic score → `is_spam` boolean; row retained |
| HTML / markup strip | Clean `text_cleaned`; preserve `text_original` |
| Empty text | Rating-only reviews kept with `text_cleaned = null` |
| Unicode normalization | NFC normalization, collapse whitespace |

### 1.3 PostgreSQL Schema (Phase 1)

| Table | Key Columns |
|-------|-------------|
| `reviews` | `id`, `external_review_id` (UNIQUE), `text_original`, `text_cleaned`, `rating`, `thumbs_up`, `device_type`, `app_version`, `review_created_at`, `developer_reply`, `is_spam`, `is_near_duplicate`, `processing_state`, `scrape_run_id` |
| `scrape_runs` | `id`, `run_type`, `reviews_target`, `reviews_scraped`, `reviews_new`, `status`, `gap_report`, `started_at`, `ended_at` |
| `scrape_checkpoints` | `id`, `scrape_run_id`, `sort_order`, `continuation_token`, `reviews_scraped_in_pass`, `status`, `updated_at` |
| `dedup_index` | `content_hash`, `review_id` |

## Deliverables

- [ ] `GooglePlayReviewScraper` with `scrape_all()`, `resume()`, `validate_corpus()`
- [ ] Multi-pass scraping (NEWEST, RATING, MOST_RELEVANT) with checkpointing
- [ ] Raw JSON batch storage in `data/raw/play_store/`
- [ ] PostgreSQL schema with `reviews`, `scrape_runs`, `scrape_checkpoints`
- [ ] Cleaning pipeline (normalize all reviews; no deletion)
- [ ] CLI: `scrape.py --mode full`, `--resume`, `--validate`, `--since`
- [ ] Corpus validation report comparing scraped count to Play Store listing total
- [ ] Dev subset mode (`--limit 10000`) for pipeline testing without full backfill

## Exit Criteria

- **In-window coverage:** All reviews from last 6 months captured (3 sort passes)
- **Zero out-of-window:** No reviews with `review_created_at` older than 6 months
- **Zero duplicate IDs:** `COUNT(*) == COUNT(DISTINCT external_review_id)`
- **Resumable:** Kill mid-scrape → `--resume` continues without data loss or duplicates
- **All reviews retained:** No rows deleted during cleaning; spam/duplicate flags only
- **Validation passes:** Rating distribution and spot-audit checks documented in `gap_report`

---

# PHASE 2 — AI Review Understanding

## Goal

Extract structured product intelligence from every review using LLM-based extraction, language detection, and translation.

## Architecture

```
┌──────────────┐     ┌──────────────────┐     ┌─────────────────────┐
│  reviews     │────▶│  Language         │────▶│  LLM Structured      │
│  (CLEANED)   │     │  Detection +      │     │  Extraction          │
│              │     │  Translation      │     │  (JSON schema)       │
└──────────────┘     └──────────────────┘     └──────────┬──────────┘
                                                          │
                                                          ▼
                                               ┌─────────────────────┐
                                               │  structured_reviews  │
                                               │  (PostgreSQL)      │
                                               └─────────────────────┘
```

## Components

### 2.1 Language Detection & Translation

| Step | Tool |
|------|------|
| Detect language | `langdetect` / FastText / CLD3 |
| Translate non-English | LLM or Google Translate API |
| Store both | `text_original` + `text_en` always preserved |

### 2.2 Structured Extraction Schema

Each review is enriched with discovery-focused fields:

```json
{
  "document_id": "uuid",
  "summary": "Free-tier user frustrated by skip limits and unwanted playlist recommendations.",
  "primary_issue": "unwanted_recommendations_in_playlists",
  "secondary_issues": ["skip_limit_frustration", "free_tier_limitations"],
  "emotions": ["frustration", "anger"],
  "sentiment": {
    "overall": "negative",
    "toward_product": "mixed",
    "toward_feature": "negative"
  },
  "recommendation_quality": "poor",
  "user_intent": "complaint",
  "listening_context": [],
  "mentioned_features": ["playlists", "recommendations", "skip_limit"],
  "feature_requests": ["remove_auto_recommendations_from_playlists"],
  "pain_points": ["6 skips per hour", "robot recommends into my playlists"],
  "behaviors": ["created_own_playlist"],
  "severity": "medium",
  "urgency": "low",
  "subscription_type": "free",
  "user_persona_signals": ["playlist_creator"],
  "is_discovery_related": true,
  "confidence": 0.91
}
```

### 2.3 Extraction Pipeline

1. Batch reviews (20–50 per LLM call with structured output)
2. Validate against Pydantic schema; retry on failure
3. Post-process: normalize feature names (`"DW"` → `discover_weekly`)
4. Write to `structured_reviews`; update `processing_state = EXTRACTED`

### 2.4 Play Store-Specific Enrichment

Leverage metadata available only from Google Play:

| Metadata | Extraction use |
|----------|----------------|
| `rating` (1–5) | Cross-check LLM sentiment; low-star + negative text = high severity |
| `thumbs_up` | Weight pain points by community agreement |
| `device_type` | Segment: phone vs watch vs car experience |
| `app_version` | Correlate issues with release regressions |
| `developer_reply` | Flag resolved vs unresolved complaints |

## Deliverables

- [ ] Language detection + translation module
- [ ] LLM extraction service with JSON schema validation
- [ ] `structured_reviews` table populated for full corpus
- [ ] SQL analytics queries: top `primary_issue` by rating, device, subscription type

## Exit Criteria

- 90%+ extraction schema validity on sample of 500 reviews
- Discovery-related reviews correctly tagged (`is_discovery_related = true`)
- Structured fields enable SQL filters: `WHERE subscription_type = 'free' AND primary_issue = 'repetitive_recommendations'`

---

# PHASE 3 — Semantic Search Layer

## Goal

Generate embeddings for all reviews and enable semantic similarity search over the Google Play corpus.

## Architecture

```
┌──────────────┐     ┌──────────────────┐     ┌─────────────────────┐
│  structured  │────▶│  Embedding        │────▶│  Vector Database     │
│  reviews     │     │  Service (batch)  │     │  (Qdrant / pgvector) │
└──────────────┘     └──────────────────┘     └──────────┬──────────┘
                                                          │
                                                          ▼
                                               ┌─────────────────────┐
                                               │  /api/v1/search      │
                                               │  Semantic Search API │
                                               └─────────────────────┘
```

## Components

### 3.1 Embedding Service

| Aspect | Choice |
|--------|--------|
| Model | `text-embedding-004` (Google Gemini) or `bge-m3` (local fallback) |
| Input template | `Review: {text_en}\nRating: {rating}/5\nIssues: {primary_issue}\nFeatures: {mentioned_features}` |
| Batch size | 100–500 reviews per batch |
| Versioning | Store `embedding_model_version` per vector |

### 3.2 Vector Index Payload

```json
{
  "document_id": "uuid",
  "rating": 2,
  "device_type": "phone",
  "subscription_type": "free",
  "primary_issue": "unwanted_recommendations_in_playlists",
  "is_discovery_related": true,
  "review_created_at": "2026-04-21",
  "thumbs_up": 27,
  "cluster_ids": []
}
```

### 3.3 Semantic Search API

```
POST /api/v1/search
{
  "query": "users complaining about repetitive Discover Weekly",
  "filters": {
    "rating_max": 3,
    "subscription_type": "premium",
    "date_from": "2025-01-01"
  },
  "top_k": 20
}
```

Returns ranked reviews with similarity scores — no LLM generation yet.

## Deliverables

- [ ] Batch embedding job for full corpus
- [ ] Vector DB indexed with metadata payloads
- [ ] Semantic search REST endpoint
- [ ] Evaluation: 20 test queries with expected relevant reviews

## Exit Criteria

- Semantic search returns paraphrased matches (e.g., "same songs every week" finds "recommendations never change")
- Search p95 latency < 500ms on dev corpus
- Metadata filters (rating, subscription, date) work correctly

---

# PHASE 4 — RAG Question Answering

## Goal

Enable natural-language product questions with **grounded, citation-backed answers** retrieved from Google Play reviews.

## Architecture

```
User Question: "Why do free users struggle with music discovery?"
       │
       ▼
┌─────────────┐
│ Query Router │  Extract filters: subscription=free, topic=discovery
└──────┬──────┘
       ▼
┌─────────────────────────────────────────┐
│ Hybrid Retriever                         │
│  ├── Dense: vector similarity            │
│  ├── Sparse: BM25 on text_en + pain_pts │
│  └── SQL pre-filter on structured fields  │
└──────┬──────────────────────────────────┘
       │ top-K = 50
       ▼
┌─────────────┐
│ Reranker    │  Cross-encoder → top-N = 15
└──────┬──────┘
       ▼
┌─────────────┐
│ Context     │  Build evidence pack with Play Store metadata
│ Builder     │
└──────┬──────┘
       ▼
┌─────────────┐
│ LLM +       │  Answer with [1][2] citations
│ Citations   │
└──────┬──────┘
       ▼
┌─────────────┐
│ Citation    │  Validate all claims are grounded
│ Validator   │
└──────┬──────┘
       ▼
  Answer + Evidence List
```

## Components

### 4.1 Supported Question Types

| Question | Retrieval strategy |
|----------|-------------------|
| "Why do users dislike Discover Weekly?" | Vector search on `discover_weekly` + cluster context |
| "Show reviews mentioning recommendation fatigue" | Semantic search, no generation |
| "What do Premium users complain about?" | Filter `subscription_type=premium` + aggregate |
| "What are top discovery issues among 1-star reviews?" | Filter `rating=1` + `is_discovery_related=true` |
| "Which feature requests appear most often?" | SQL count on `feature_requests` field |
| "How have discovery complaints changed this year?" | Time-filtered retrieval + synthesis |
| "What do phone users say about playlists?" | Filter `device_type=phone` + semantic search |

### 4.2 Evidence Context Format

```
[1] Google Play | ★2/5 | 27 helpful | Phone | Free user | 2026-04-21
    "The free version is terrible. Bro you can only do 6 skips per hour
     and then it gives you a whole bunch of recommendations into the
     playlists you're listening to!"
    Issues: unwanted_recommendations_in_playlists, skip_limit_frustration
    Emotion: frustration
```

### 4.3 RAG API

```
POST /api/v1/query
{
  "question": "Why do users dislike Discover Weekly?",
  "filters": {
    "rating_max": 3,
    "date_from": "2025-01-01"
  }
}
```

**Response:**

```json
{
  "answer": "Google Play reviewers criticize Discover Weekly primarily for...",
  "citations": [
    {
      "id": 1,
      "document_id": "uuid",
      "rating": 2,
      "thumbs_up": 27,
      "device_type": "phone",
      "excerpt": "My Discover Weekly hasn't changed in months...",
      "review_created_at": "2026-03-15"
    }
  ],
  "confidence": 0.87,
  "reviews_considered": 64,
  "reviews_cited": 8
}
```

## Deliverables

- [ ] Hybrid retriever (dense + BM25 + SQL filters)
- [ ] Cross-encoder reranker
- [ ] RAG `/api/v1/query` endpoint with citation validation
- [ ] 50-question evaluation set with human-reviewed answers

## Exit Criteria

- Answers cite only retrieved Play Store reviews
- Citation accuracy > 90% on evaluation set
- RAG p95 latency < 8 seconds
- Correctly answers all 8 question types from problem statement

---

# PHASE 5 — Clustering & Product Insights

## Goal

Automatically group similar reviews into themes, detect trends, and generate actionable product intelligence reports.

## Architecture

```
┌──────────────┐     ┌──────────────────┐     ┌─────────────────────┐
│  Embeddings  │────▶│  Clustering       │────▶│  Theme Labels (LLM)  │
│  (all reviews)│     │  HDBSCAN/K-Means  │     │  + Taxonomy          │
└──────────────┘     └──────────────────┘     └──────────┬──────────┘
                                                          │
                         ┌────────────────────────────────┤
                         ▼                                ▼
              ┌─────────────────────┐         ┌─────────────────────┐
              │  Insight Generator   │         │  Trend Analyzer      │
              │  (LLM synthesis)     │         │  (time-series)       │
              └──────────┬──────────┘         └──────────┬──────────┘
                         │                                │
                         └────────────┬───────────────────┘
                                      ▼
                           ┌─────────────────────┐
                           │  Dashboard + Reports   │
                           │  /api/v1/insights    │
                           │  /api/v1/clusters    │
                           └─────────────────────┘
```

## Components

### 5.1 Theme Clustering

**Seed themes** (discovery-focused, from problem statement):

| Theme ID | Label |
|----------|-------|
| `repetitive_recommendations` | Repetitive recommendations |
| `poor_discover_weekly` | Poor Discover Weekly |
| `playlist_fatigue` | Playlist fatigue |
| `genre_repetition` | Genre repetition |
| `poor_exploration` | Poor exploration |
| `liked_songs_repetition` | Liked Songs repetition |
| `algorithm_bias` | Algorithm bias |
| `podcast_interference` | Podcast interference |
| `missing_niche_artists` | Missing niche artists |
| `mood_mismatch` | Mood mismatch |
| `context_mismatch` | Context mismatch |
| `discovery_stagnation` | Discovery stagnation |

**Process:**
1. Cluster embeddings with HDBSCAN
2. LLM labels each cluster with human-readable name + description
3. Map clusters to seed taxonomy where overlap exists
4. Incremental assignment for new reviews (daily)

### 5.2 Cluster Output

```json
{
  "cluster_id": "cluster_07",
  "label": "Unwanted Recommendations in User Playlists",
  "description": "Free users report Spotify injecting recommendations into manually curated playlists.",
  "member_count": 4821,
  "avg_rating": 2.1,
  "avg_thumbs_up": 18.4,
  "top_subscription_types": ["free", "premium"],
  "top_device_types": ["phone"],
  "representative_reviews": ["uuid1", "uuid2", "uuid3"],
  "trend_30d": 0.08
}
```

### 5.3 Insight Generator

Produces scheduled reports:

| Insight type | Example output |
|--------------|----------------|
| Top recurring complaints | Ranked list with review counts and avg rating |
| Emerging issues | Clusters with >20% growth in 30 days |
| Feature request frequency | "Remove auto-recommendations from playlists" — 4,821 mentions |
| Root cause summary | LLM synthesis across cluster evidence |
| Segment analysis | Free vs Premium discovery pain points |
| Version regression | Spike in complaints after app version X |

### 5.4 Dashboard Views

- Top 10 discovery themes (bar chart + drill-down)
- Sentiment/emotion distribution per theme
- Rating distribution per cluster
- Timeline: complaint volume over months
- Device breakdown (phone / tablet / watch / car)

## Deliverables

- [ ] Clustering pipeline with LLM theme labeling
- [ ] `/api/v1/clusters` and `/api/v1/insights` endpoints
- [ ] `/api/v1/trends` time-series endpoint
- [ ] Web dashboard (React/Next.js) with theme explorer

## Exit Criteria

- 12 seed themes populated with >100 reviews each (on full corpus)
- Insight reports generated weekly without manual intervention
- Dashboard shows top complaints backed by real review evidence

---

# PHASE 6 — Agentic Workflows & Production Scale

## Goal

Handle complex multi-step analytical questions via an agent orchestrator, enable continuous incremental ingestion, and harden for production scale (~35M reviews).

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    AGENT ORCHESTRATOR                        │
│  Plan → Tool Call → Observe → Iterate → Synthesize          │
└────────────────────────────┬────────────────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        ▼                    ▼                    ▼
┌──────────────┐   ┌──────────────┐   ┌──────────────────┐
│semantic_search│   │structured_  │   │get_trends         │
│              │   │query (SQL)  │   │compare_segments   │
└──────────────┘   └──────────────┘   └──────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│              INCREMENTAL INGESTION (daily)                   │
│  New Play Store reviews → pipeline → index (no full rebuild) │
└─────────────────────────────────────────────────────────────┘
```

## Components

### 6.1 Agent Tools

| Tool | Use case |
|------|----------|
| `semantic_search` | Find reviews by meaning + metadata filters |
| `structured_query` | SQL aggregations (counts, top issues by segment) |
| `get_cluster` | Fetch cluster details + representative reviews |
| `compare_segments` | Free vs Premium, Phone vs Watch, etc. |
| `get_trends` | Time-series for a theme or issue |
| `summarize_evidence` | Synthesize a set of review IDs |

### 6.2 Example Agent Trace

**Question:** *"What discovery issues do free users on phones report most, and how has that changed in 2026?"*

```
Step 1: structured_query → top primary_issue WHERE subscription=free AND device=phone
Step 2: get_trends → discovery issues, filter 2026, subscription=free
Step 3: semantic_search → sample reviews for top 3 issues
Step 4: summarize_evidence → comparative report with citations
```

### 6.3 Production Scale Strategy

| Concern | Strategy |
|---------|----------|
| 35M+ reviews | Partitioned vector index by year; batch backfill in chunks |
| Incremental ingestion | Daily job: fetch reviews since last `collected_at` |
| LLM cost | Cache extractions by content hash; batch processing |
| Query latency | Metadata pre-filter before vector search; Redis cache for top queries |
| Reindexing | Versioned embeddings; blue-green index swap |
| Monitoring | Langfuse (LLM traces), Prometheus (pipeline metrics) |

### 6.4 Deployment

```
┌──────────────┐
│  Load Balancer│
└──────┬───────┘
       │
  ┌────┴────┐
  ▼         ▼
API ×2    Worker Pool ×N
  │         │
  └────┬────┘
       │
  ┌────┴────────────────────────┐
  ▼              ▼              ▼
PostgreSQL    Qdrant/pgvector   Redis
  │
  ▼
Object Store (raw Play Store JSON)
```

## Deliverables

- [ ] Agent orchestrator with 6 tools
- [ ] Full corpus scrape completed and validated (≥ 99.5% coverage)
- [ ] Daily incremental scrape job
- [ ] Production deployment (Docker / cloud)
- [ ] Monitoring + alerting

## Exit Criteria

- Agent correctly answers 3+ step analytical questions
- Daily incremental scrape runs without manual intervention
- System handles full corpus (~35M reviews) with target SLAs
- Full platform matches all success criteria from problem statement

---

## 5. Technology Stack

| Layer | Phase introduced | Technology |
|-------|-----------------|------------|
| Language | 1 | Python 3.11+ |
| Play Store scraping | 1 | `google-play-scraper` (full corpus pagination) |
| API | 3 | FastAPI |
| Database | 1 | PostgreSQL 15+ |
| Vector DB | 3 | Qdrant or pgvector |
| Job queue | 2 | Celery + Redis |
| Embeddings | 3 | Google `text-embedding-004` / BGE-M3 (local) |
| LLM | 2 | **Google Gemini** (`gemini-2.0-flash`, `gemini-1.5-pro`) |
| Reranker | 4 | Cohere Rerank / cross-encoder |
| BM25 | 4 | PostgreSQL full-text or Elasticsearch |
| Dashboard | 5 | React / Next.js |
| Agent | 6 | LangGraph or custom tool-calling loop |
| Observability | 6 | Langfuse, Prometheus + Grafana |

---

## 6. End-to-End Data Flow Example

**Source:** [Google Play — Spotify Reviews](https://play.google.com/store/apps/details?id=com.spotify.music)

**Input review:**
> *"The free version is terrible. Bro you can only do 6 skips per hour and then it gives you a whole bunch of recommendations into the playlists you're listening to! like bro when I make a playlist I like it how it is I don't need some robot to recommend things for it!"* — ★2, 27 helpful, Phone, Apr 2026

| Phase | What happens |
|-------|-------------|
| **1 — Scrape** | Full corpus fetch via `google-play-scraper`; 3 sort passes; checkpointed; validated against ~35.8M listing count |
| **2 — Extract** | `primary_issue=unwanted_recommendations_in_playlists`, `subscription_type=free`, `emotions=[frustration]` |
| **3 — Embed** | Vector stored in Qdrant with metadata payload |
| **4 — RAG** | Query *"Why do free users hate playlist recommendations?"* retrieves and cites this review |
| **5 — Cluster** | Assigned to cluster *"Unwanted Recommendations in User Playlists"* (4,821 members) |
| **6 — Agent** | Segment comparison confirms this is a top-3 free-tier discovery complaint in 2026 |

---

## 7. API Reference (Cumulative by Phase)

| Endpoint | Phase | Method | Purpose |
|----------|-------|--------|---------|
| `/api/v1/scrape` | 1 | POST | Trigger full or incremental scrape |
| `/api/v1/scrape/status` | 1 | GET | Scrape run progress + corpus validation |
| `/api/v1/ingest` | 1 | POST | Manual CSV/JSON upload (dev only) |
| `/api/v1/reviews` | 1 | GET | List reviews with SQL filters |
| `/api/v1/reviews/{id}` | 1 | GET | Single review detail |
| `/api/v1/search` | 3 | POST | Semantic search |
| `/api/v1/query` | 4 | POST | RAG Q&A with citations |
| `/api/v1/clusters` | 5 | GET | Theme clusters |
| `/api/v1/clusters/{id}` | 5 | GET | Cluster detail + samples |
| `/api/v1/insights` | 5 | GET | Generated insights |
| `/api/v1/trends` | 5 | GET | Time-series data |
| `/api/v1/agent/query` | 6 | POST | Multi-step agent Q&A |

---

## 8. Success Criteria Mapping

| Success Criterion | Phase | Enabler |
|-------------------|-------|---------|
| Aggregate **6-month** Google Play reviews into unified knowledge base | 1 | Window scraper + PostgreSQL |
| Transform unstructured → structured | 2 | LLM structured extraction |
| Identify recurring issues semantically | 3, 5 | Embeddings + clustering |
| Conversational RAG querying | 4 | Hybrid retrieval + grounded generation |
| Evidence-backed product opportunities | 5 | Insight generator + citations |
| Distinguish user segments | 2, 4 | `subscription_type`, `device_type`, persona signals |
| Reveal hidden behavioral patterns | 5, 6 | Clustering + agent workflows |
| Scale to large datasets | 6 | Partitioned indexes, incremental ingestion |

---

## 9. Security & Compliance

| Area | Approach |
|------|----------|
| Data source | Public Google Play reviews only; respect Play Store ToS and rate limits |
| PII | Hash reviewer names; never expose raw `user_name` in API responses |
| Rate limiting | 1–3s delay between scrape batches; exponential backoff on 429/503 |
| Scrape ToS | Public reviews only; respect Play Store terms; throttle requests |
| Access control | API key auth for internal product team access |
| Audit | Log all RAG queries and generated insights |

---

## 10. Summary

This architecture delivers a **phase-gated AI Product Research Assistant** built exclusively on **all Google Play reviews of Spotify** (`com.spotify.music`). The pipeline begins with a **complete, checkpointed scrape** of every public review on the [Play Store listing](https://play.google.com/store/apps/details?id=com.spotify.music) (~35M+), then layers understanding, search, RAG, and insights on top of that full corpus. Each phase ships a testable increment:

1. **Foundation** — scrape last 6 months of Play Store reviews; resumable with date validation
2. **Understanding** — structured extraction of discovery pain points
3. **Semantic search** — find reviews by meaning, not keywords
4. **RAG Q&A** — conversational, citation-backed product questions
5. **Insights** — automated theme clustering and trend reports
6. **Agent & scale** — complex multi-step analysis at production volume

The result is an evidence-driven platform that listens to the voice of Spotify users on Google Play and empowers product teams to make data-backed decisions about music discovery and recommendation quality.
