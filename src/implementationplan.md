# Phase-Wise Implementation Plan

**Project:** Spotify NL — AI-Powered Review Discovery Engine  
**Data source:** [Spotify on Google Play](https://play.google.com/store/apps/details?id=com.spotify.music) (`com.spotify.music`)  
**References:** [problemstatement.md](../docs/problemstatement.md) · [ragarchitecture.md](../docs/ragarchitecture.md)

---

## 1. Executive Summary

This plan implements an **AI Product Research Assistant** that transforms **the last 6 months** of Spotify Google Play reviews into structured, searchable, citation-backed product intelligence about **music discovery and recommendation** pain points.

| Aspect | Decision |
|--------|----------|
| **Scope (v1)** | Google Play reviews only (not Reddit, App Store, social) |
| **Corpus** | **Last 6 months only** (rolling window via `SCRAPE_MONTHS_BACK=6`) |
| **Delivery model** | 6 phases; each phase ships a testable increment |
| **Google Play API key** | Not required — use `google-play-scraper` |
| **Primary LLM** | **Google Gemini** (`GEMINI_API_KEY`) — not OpenAI |
| **Primary stack** | Python 3.11+, PostgreSQL, Qdrant/pgvector, FastAPI, Celery, **Google Gemini** |

### Problem statement → pipeline mapping

| Problem statement step | Implementation phase |
|------------------------|----------------------|
| Step 1 — Data collection | Phase 1 |
| Step 2 — Data cleaning | Phase 1 |
| Step 3 — Language detection | Phase 2 |
| Step 4 — AI review understanding | Phase 2 |
| Step 5 — Semantic embeddings | Phase 3 |
| Step 6 — Clustering | Phase 5 |
| Step 7 — Insight generation | Phase 5 |
| Step 8 — Question answering (RAG) | Phase 4 (+ Phase 6 agent) |

### Key challenges addressed

| Challenge | Addressed in |
|-----------|--------------|
| Massive scale (6-month recent window) | Phase 1 scrape + Phase 6 scale |
| Unstructured language (slang, multilingual) | Phase 2 translation + extraction |
| Duplicate opinions (semantic similarity) | Phase 3 embeddings + Phase 5 clustering |
| Mixed sentiment per review | Phase 2 multi-signal extraction |
| Context understanding (gym, driving, etc.) | Phase 2 `listening_context` field |
| User diversity (free/premium, personas) | Phase 2 persona signals + Phase 4/5 filters |

---

## 2. Implementation Timeline Overview

```
Week 1–2   │ PHASE 1 — Data Foundation (6-month window scraper + PostgreSQL)
Week 3     │ PHASE 2 — AI Understanding (on 6-month corpus)
Week 6     │ PHASE 3 — Semantic Search
Week 7–8   │ PHASE 4 — RAG Q&A
Week 9–10  │ PHASE 5 — Clustering & Insights + Dashboard
Week 11–12 │ PHASE 6 — Agent, incremental scrape, production hardening
```

Phases 4 and 5 can overlap after Phase 3 completes. Phase 1 scrapes only reviews from the **last 6 months** — use `--limit` for dev testing.

---

## 3. Prerequisites (Before Phase 1)

### 3.1 Environment setup

```bash
# Repository root
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt  # create during Phase 1

cp config/.env.example .env
# Set DATABASE_URL at minimum
```

### 3.2 Infrastructure

| Service | Phase needed | Local dev |
|---------|--------------|-----------|
| PostgreSQL 15+ | 1 | Docker or local install |
| Redis | 2 | Docker (Celery jobs) |
| Qdrant or pgvector | 3 | Docker Qdrant |
| LLM API (Google Gemini) | 2 | `GEMINI_API_KEY` in `.env` |

### 3.3 Credentials checklist

| Credential | Required when | Required? |
|------------|---------------|-----------|
| `DATABASE_URL` | Phase 1 | Yes |
| Google Play API key | Never | **No** |
| `GEMINI_API_KEY` | Phase 2+ | Yes |
| `QDRANT_URL` | Phase 3 | Yes |
| `REDIS_URL` | Phase 2+ | Yes |
| `SERPAPI_KEY` | Only if scraper blocked | Optional |

---

## 4. Phase 1 — Data Foundation

**Goal:** Scrape **last 6 months** of Spotify Google Play reviews, clean, persist to PostgreSQL.  
**Window:** `SCRAPE_MONTHS_BACK=6` (configurable via `.env` or `--months-back`)

### 4.1 Implementation tasks (in order)

#### Sprint 1.1 — Project bootstrap (Days 1–2)

| # | Task | Files / output |
|---|------|--------------|
| 1.1.1 | Create `requirements.txt` (google-play-scraper, sqlalchemy, psycopg2-binary, pydantic, fastapi, uvicorn) | `requirements.txt` |
| 1.1.2 | Shared config loader | `src/shared/config.py` |
| 1.1.3 | App constants (`SPOTIFY_APP_ID`, defaults) | `src/shared/constants.py` |
| 1.1.4 | Docker Compose for PostgreSQL | `config/docker-compose.yml` |

#### Sprint 1.2 — Database layer (Days 3–4)

| # | Task | Files / output |
|---|------|--------------|
| 1.2.1 | SQLAlchemy models: `Review`, `ScrapeRun`, `ScrapeCheckpoint`, `DedupIndex` | `src/database/models/` |
| 1.2.2 | Alembic migration — initial schema | `src/database/migrations/001_initial.sql` |
| 1.2.3 | Review repository (upsert, list, get by id) | `src/database/repositories/review_repo.py` |
| 1.2.4 | Scrape run repository | `src/database/repositories/scrape_repo.py` |
| 1.2.5 | DB session factory | `src/database/session.py` |

#### Sprint 1.3 — Scraper core (Days 5–8)

| # | Task | Files / output |
|---|------|--------------|
| 1.3.1 | Play Store review normalizer (raw → `PlayStoreReviewDocument`) | `src/scrape/normalizer.py` |
| 1.3.2 | Pagination loop with `continuation_token` | `src/scrape/pagination.py` |
| 1.3.3 | Rate limiter + exponential backoff | `src/scrape/rate_limiter.py` |
| 1.3.4 | Checkpoint save/resume | `src/scrape/checkpoint.py` |
| 1.3.5 | Main orchestrator: `scrape_all()` with 6-month cutoff | `phase01/scrape/scraper.py` |
| 1.3.6 | Window filter + cutoff helpers | `phase01/scrape/window.py` |
| 1.3.7 | Corpus validator (zero out-of-window rows) | `phase01/scrape/validator.py` |
| 1.3.7 | Raw batch writer to `data/raw/play_store/` | `src/scrape/batch_writer.py` |

#### Sprint 1.4 — Cleaning pipeline (Days 9–10)

| # | Task | Files / output |
|---|------|--------------|
| 1.4.1 | Unicode normalization, whitespace collapse | `src/cleaning/normalizer.py` |
| 1.4.2 | Spam tagger (heuristic; flag only, no delete) | `src/cleaning/spam_filter.py` |
| 1.4.3 | Near-duplicate detector (SimHash) | `src/cleaning/dedup.py` |
| 1.4.4 | Cleaning orchestrator | `src/cleaning/pipeline.py` |

#### Sprint 1.5 — CLI & API (Days 11–12)

| # | Task | Files / output |
|---|------|--------------|
| 1.5.1 | CLI: `--mode window`, `--months-back 6`, `--resume`, `--validate` | `phases/phase-01-data-foundation/cli/scrape.py` |
| 1.5.2 | FastAPI app skeleton | `src/api/main.py` |
| 1.5.3 | `POST /api/v1/scrape`, `GET /api/v1/scrape/status` | `src/api/routes/scrape.py` |
| 1.5.4 | `GET /api/v1/reviews`, `GET /api/v1/reviews/{id}` | `src/api/routes/reviews.py` |
| 1.5.5 | `POST /api/v1/ingest` (CSV/JSON dev upload) | `src/api/routes/ingest.py` |
| 1.5.6 | Pydantic request/response schemas | `src/api/schemas/` |

#### Sprint 1.6 — Testing & dev subset (Days 13–14)

| # | Task | Files / output |
|---|------|--------------|
| 1.6.1 | Unit tests: normalizer, checkpoint, dedup | `tests/phase-01/` |
| 1.6.2 | Integration test: scrape 100 reviews → DB | `tests/phase-01/test_scrape_integration.py` |
| 1.6.3 | Scrape 10K dev subset: `python scripts/scrape.py --limit 10000` | Dev corpus ready |
| 1.6.4 | Document runbook | `phases/phase-01-data-foundation/RUNBOOK.md` |

#### Sprint 1.7 — Window backfill (Days 15+)

| # | Task | Notes |
|---|------|-------|
| 1.7.1 | Run `scrape.py scrape --mode window` (3 sort passes, 6-month cutoff) | Hours–1 day typical |
| 1.7.2 | Run `scrape.py scrape --validate` | Zero reviews older than 6 months |
| 1.7.3 | Fix gaps; re-run incomplete passes | Until validation passes |

### 4.2 Phase 1 exit criteria

- [ ] All reviews in DB have `review_created_at` within last 6 months
- [ ] Zero reviews older than `SCRAPE_MONTHS_BACK` cutoff
- [ ] `COUNT(*) == COUNT(DISTINCT external_review_id)`
- [ ] `--resume` works after simulated crash
- [ ] All reviews retained (spam flagged, not deleted)
- [ ] API returns filtered review lists

### 4.3 Phase 1 business questions enabled

*None yet — data layer only. Enables manual SQL exploration of raw reviews.*

---

## 5. Phase 2 — AI Understanding

**Goal:** Structured LLM extraction for every review.  
**Folder:** `phases/phase-02-ai-understanding/`  
**Code:** `src/extraction/`, `src/database/models/structured_review.py`

**Prerequisite:** Phase 1 dev subset (10K reviews) minimum; full corpus preferred.

### 5.1 Implementation tasks (in order)

#### Sprint 2.1 — Schema & provider abstraction (Days 1–2)

| # | Task | Files / output |
|---|------|--------------|
| 2.1.1 | Pydantic extraction schema (all fields from architecture) | `src/extraction/schema.py` |
| 2.1.2 | Gemini LLM provider (`google-generativeai`) | `phase02/shared/llm_gemini.py` |
| 2.1.3 | Provider abstraction | `phase02/shared/llm_provider.py` |
| 2.1.4 | `structured_reviews` table migration | `src/database/migrations/002_structured_reviews.sql` |

#### Sprint 2.2 — Language pipeline (Days 3–4)

| # | Task | Files / output |
|---|------|--------------|
| 2.2.1 | Language detection (langdetect / CLD3) | `src/extraction/language.py` |
| 2.2.2 | Translation to `text_en` (Gemini or Google Translate API) | `src/extraction/translation.py` |
| 2.2.3 | Update `processing_state`: `CLEANED → TRANSLATED` | pipeline hook |

#### Sprint 2.3 — LLM extraction (Days 5–8)

| # | Task | Files / output |
|---|------|--------------|
| 2.3.1 | Extraction prompt template (multi-signal, discovery-focused) | `src/extraction/prompts.py` |
| 2.3.2 | Batch extractor (20–50 reviews per call, structured JSON) | `src/extraction/extractor.py` |
| 2.3.3 | Schema validation + retry logic | `src/extraction/validator.py` |
| 2.3.4 | Feature name post-processor (`DW` → `discover_weekly`) | `src/extraction/enrichment.py` |
| 2.3.5 | Play Store metadata cross-check (rating vs sentiment) | `src/extraction/enrichment.py` |

#### Sprint 2.4 — Job queue (Days 9–10)

| # | Task | Files / output |
|---|------|--------------|
| 2.4.1 | Celery app + Redis config | `src/orchestration/celery_app.py` |
| 2.4.2 | `extract_reviews` task (batch by ID range) | `src/orchestration/tasks/extract.py` |
| 2.4.3 | CLI: `python scripts/extract.py --batch-size 50` | `scripts/extract.py` |
| 2.4.4 | Extraction cache by content hash (cost control) | `src/extraction/cache.py` |

#### Sprint 2.5 — Testing & validation (Days 11–12)

| # | Task | Files / output |
|---|------|--------------|
| 2.5.1 | Unit tests: schema validation, enrichment | `tests/phase-02/` |
| 2.5.2 | Evaluate 500 reviews: ≥ 90% schema validity | `tests/phase-02/eval_extraction.py` |
| 2.5.3 | SQL analytics: top `primary_issue` by rating, subscription | `scripts/analytics_issues.sql` |
| 2.5.4 | Run extraction on full corpus (background job) | Celery workers |

### 5.2 Phase 2 exit criteria

- [ ] 90%+ extraction validity on 500-review sample
- [ ] `is_discovery_related` correctly tagged
- [ ] SQL filters: `subscription_type`, `primary_issue`, `device_type`
- [ ] `processing_state = EXTRACTED` for processed rows

### 5.3 Problem statement questions partially enabled

- Which user groups face different discovery challenges? (via `user_persona_signals`, `subscription_type`)
- What emotions do users express? (via `emotions` field)
- Which feature requests appear most frequently? (via `feature_requests` SQL count)

---

## 6. Phase 3 — Semantic Search

**Goal:** Embed all reviews; expose semantic search API.  
**Folder:** `phases/phase-03-semantic-search/`  
**Code:** `src/embedding/`, `src/search/`, `src/api/routes/search.py`

**Prerequisite:** Phase 1 corpus; Phase 2 recommended (richer embedding input).

### 6.1 Implementation tasks (in order)

#### Sprint 3.1 — Embedding service (Days 1–4)

| # | Task | Files / output |
|---|------|--------------|
| 3.1.1 | Gemini embedding provider (`text-embedding-004`) | `src/embedding/provider.py` |
| 3.1.2 | Input text template (review + rating + issues + features) | `src/embedding/templates.py` |
| 3.1.3 | Batch embedder (100–500 per batch) | `src/embedding/embedder.py` |
| 3.1.4 | Model version tracking | `src/embedding/versioning.py` |
| 3.1.5 | Celery task: `embed_reviews` | `src/orchestration/tasks/embed.py` |

#### Sprint 3.2 — Vector database (Days 5–7)

| # | Task | Files / output |
|---|------|--------------|
| 3.2.1 | Qdrant client wrapper (or pgvector adapter) | `src/embedding/indexer.py` |
| 3.2.2 | Index creation with metadata payload schema | `src/embedding/indexer.py` |
| 3.2.3 | Bulk index from PostgreSQL | `scripts/index_vectors.py` |
| 3.2.4 | Update `processing_state`: `EMBEDDED → INDEXED` | pipeline hook |

#### Sprint 3.3 — Search API (Days 8–10)

| # | Task | Files / output |
|---|------|--------------|
| 3.3.1 | Semantic search service (query embed + vector search + filters) | `src/search/semantic_search.py` |
| 3.3.2 | `POST /api/v1/search` endpoint | `src/api/routes/search.py` |
| 3.3.3 | Online query embedding | `src/embedding/embedder.py` |
| 3.3.4 | Eval set: 20 test queries with expected matches | `tests/phase-03/eval_search.json` |

### 6.2 Phase 3 exit criteria

- [ ] Full corpus embedded and indexed
- [ ] Paraphrase matching works ("same songs" ≈ "recommendations never change")
- [ ] Metadata filters: rating, subscription, date range
- [ ] Search p95 < 500ms on dev corpus

### 6.3 Problem statement questions enabled

- "Show reviews mentioning recommendation fatigue" (semantic search)
- Duplicate opinions recognized by meaning (foundation for clustering)

---

## 7. Phase 4 — RAG Q&A

**Goal:** Citation-backed answers to natural-language product questions.  
**Folder:** `phases/phase-04-rag-qa/`  
**Code:** `src/rag/`, `src/api/routes/query.py`

**Prerequisite:** Phase 3 complete.

### 7.1 Implementation tasks (in order)

#### Sprint 4.1 — Retrieval layer (Days 1–5)

| # | Task | Files / output |
|---|------|--------------|
| 4.1.1 | Query router (intent + filter extraction) | `src/rag/router.py` |
| 4.1.2 | Query enhancement (rewrite, optional HyDE) | `src/rag/enhancement.py` |
| 4.1.3 | Dense retriever (vector search) | `src/rag/retriever.py` |
| 4.1.4 | Sparse retriever (BM25 / PostgreSQL full-text) | `src/rag/bm25.py` |
| 4.1.5 | SQL metadata pre-filter | `src/rag/filters.py` |
| 4.1.6 | Reciprocal Rank Fusion | `src/rag/fusion.py` |
| 4.1.7 | Cross-encoder reranker | `src/rag/reranker.py` |

#### Sprint 4.2 — Generation layer (Days 6–8)

| # | Task | Files / output |
|---|------|--------------|
| 4.2.1 | Context builder (evidence pack with Play Store metadata) | `src/rag/context.py` |
| 4.2.2 | Grounded generation prompt | `src/rag/prompts.py` |
| 4.2.3 | LLM answer generator with `[1][2]` citations | `src/rag/generator.py` |
| 4.2.4 | Citation validator | `src/rag/citations.py` |
| 4.2.5 | RAG pipeline orchestrator | `src/rag/pipeline.py` |

#### Sprint 4.3 — API & evaluation (Days 9–12)

| # | Task | Files / output |
|---|------|--------------|
| 4.3.1 | `POST /api/v1/query` endpoint | `src/api/routes/query.py` |
| 4.3.2 | 50-question eval set (from problem statement) | `tests/phase-04/eval_rag.json` |
| 4.3.3 | Citation accuracy scorer | `tests/phase-04/eval_citations.py` |
| 4.3.4 | Query audit log → `queries` table | `src/database/models/query_log.py` |

### 7.2 Phase 4 exit criteria

- [ ] Answers cite only retrieved Play Store reviews
- [ ] Citation accuracy > 90% on eval set
- [ ] RAG p95 < 8 seconds
- [ ] All 8 problem-statement question types answered correctly

### 7.3 Problem statement questions fully enabled (RAG)

| Business question | RAG support |
|-------------------|-------------|
| Why do users struggle to discover new music? | Thematic synthesis + citations |
| Why do recommendation algorithms become repetitive? | Semantic retrieval on repetition themes |
| What prevents users from finding fresh artists? | Cluster + search evidence |
| What causes recommendation fatigue? | Trend + semantic search |
| Which recommendation surfaces receive the most criticism? | `mentioned_features` filter + RAG |
| Which user groups face different discovery challenges? | `subscription_type` / persona filters |
| What emotions do users express? | Extraction fields + synthesis |
| Which feature requests appear most often? | Structured query + RAG |
| Which discovery journeys produce frustration? | `listening_context` + pain_points |
| What unmet user needs consistently emerge? | Cross-review synthesis |

---

## 8. Phase 5 — Clustering & Insights

**Goal:** Theme discovery, trends, product intelligence dashboard.  
**Folder:** `phases/phase-05-clustering-insights/`  
**Code:** `src/clustering/`, `src/insights/`, `src/api/routes/clusters.py`, `insights.py`, `trends.py`

**Prerequisite:** Phase 3 embeddings; Phase 2 structured fields recommended.

### 8.1 Implementation tasks (in order)

#### Sprint 5.1 — Clustering (Days 1–6)

| # | Task | Files / output |
|---|------|--------------|
| 5.1.1 | HDBSCAN/K-Means on embedding vectors | `src/clustering/clusterer.py` |
| 5.1.2 | LLM theme labeler per cluster | `src/clustering/labeler.py` |
| 5.1.3 | Seed taxonomy mapper (12 discovery themes) | `src/clustering/taxonomy.py` |
| 5.1.4 | Incremental assigner for new reviews | `src/clustering/assigner.py` |
| 5.1.5 | `clusters`, `cluster_memberships` migrations | `src/database/migrations/003_clusters.sql` |
| 5.1.6 | Celery task: weekly `cluster_reviews` | `src/orchestration/tasks/cluster.py` |

#### Sprint 5.2 — Insights engine (Days 7–10)

| # | Task | Files / output |
|---|------|--------------|
| 5.2.1 | Top complaints aggregator | `src/insights/aggregator.py` |
| 5.2.2 | Emerging issues detector (30-day growth) | `src/insights/emerging.py` |
| 5.2.3 | Trend analyzer (time-series per theme) | `src/insights/trends.py` |
| 5.2.4 | Root cause synthesizer (LLM + cluster evidence) | `src/insights/root_cause.py` |
| 5.2.5 | Opportunity finder (unmet needs, feature co-occurrence) | `src/insights/opportunities.py` |
| 5.2.6 | Weekly report generator | `src/insights/reporter.py` |
| 5.2.7 | `insights` table migration | `src/database/migrations/004_insights.sql` |

#### Sprint 5.3 — API & dashboard (Days 11–14)

| # | Task | Files / output |
|---|------|--------------|
| 5.3.1 | `GET /api/v1/clusters`, `GET /api/v1/clusters/{id}` | `src/api/routes/clusters.py` |
| 5.3.2 | `GET /api/v1/insights` | `src/api/routes/insights.py` |
| 5.3.3 | `GET /api/v1/trends` | `src/api/routes/trends.py` |
| 5.3.4 | React/Next.js dashboard (theme explorer, charts) | `frontend/` or `src/dashboard/` |
| 5.3.5 | Embed insights for RAG retrieval | `src/insights/indexer.py` |

### 8.2 Phase 5 exit criteria

- [ ] 12 seed themes populated with >100 reviews each
- [ ] Weekly insight reports run automatically
- [ ] Dashboard shows top complaints with evidence drill-down
- [ ] Trend API returns time-series per theme

### 8.3 Expected outputs (from problem statement)

- [ ] Top recurring user complaints
- [ ] Most common recommendation failures
- [ ] Discovery pain-point taxonomy
- [ ] User segment analysis
- [ ] Listening behavior insights
- [ ] Emotional analysis
- [ ] Feature request frequency
- [ ] Trend analysis over time
- [ ] Theme clustering
- [ ] AI-generated product insights
- [ ] Root cause summaries
- [ ] Evidence-backed recommendations

---

## 9. Phase 6 — Agentic & Production Scale

**Goal:** Multi-step agent, incremental scraping, production hardening at ~35M scale.  
**Folder:** `phases/phase-06-agentic-scale/`  
**Code:** `src/agent/`, `src/orchestration/`, `config/deployment/`

**Prerequisite:** Phases 1–5 complete or near-complete.

### 9.1 Implementation tasks (in order)

#### Sprint 6.1 — Agent orchestrator (Days 1–6)

| # | Task | Files / output |
|---|------|--------------|
| 6.1.1 | Agent loop (plan → tool call → observe → synthesize) | `src/agent/orchestrator.py` |
| 6.1.2 | Tool: `semantic_search` | `src/agent/tools/semantic_search.py` |
| 6.1.3 | Tool: `structured_query` | `src/agent/tools/structured_query.py` |
| 6.1.4 | Tool: `get_cluster` | `src/agent/tools/get_cluster.py` |
| 6.1.5 | Tool: `compare_segments` | `src/agent/tools/compare_segments.py` |
| 6.1.6 | Tool: `get_trends` | `src/agent/tools/get_trends.py` |
| 6.1.7 | Tool: `summarize_evidence` | `src/agent/tools/summarize_evidence.py` |
| 6.1.8 | `POST /api/v1/agent/query` | `src/api/routes/agent.py` |

#### Sprint 6.2 — Incremental ingestion (Days 7–8)

| # | Task | Files / output |
|---|------|--------------|
| 6.2.1 | Daily Celery Beat: `scrape_incremental` | `src/orchestration/schedules.py` |
| 6.2.2 | Pipeline trigger: new review → extract → embed → cluster | `src/orchestration/pipeline.py` |
| 6.2.3 | Update `thumbs_up` / `developer_reply` on existing rows | `src/scrape/scraper.py` |

#### Sprint 6.3 — Production scale (Days 9–12)

| # | Task | Files / output |
|---|------|--------------|
| 6.3.1 | Partitioned vector index by year | `src/embedding/indexer.py` |
| 6.3.2 | Redis cache for frequent RAG queries | `src/rag/cache.py` |
| 6.3.3 | Blue-green embedding reindex on model upgrade | `scripts/reindex_vectors.py` |
| 6.3.4 | API key auth middleware | `src/api/dependencies.py` |
| 6.3.5 | Prometheus metrics + Grafana dashboards | `config/deployment/monitoring/` |
| 6.3.6 | Langfuse LLM tracing | `src/shared/observability.py` |

#### Sprint 6.4 — Deployment (Days 13–14)

| # | Task | Files / output |
|---|------|--------------|
| 6.4.1 | Dockerfiles: API, worker | `config/deployment/` |
| 6.4.2 | docker-compose.prod.yml (API ×2, workers ×N, PG, Qdrant, Redis) | `config/docker-compose.prod.yml` |
| 6.4.3 | Load test: search + RAG at 1M+ review scale | `tests/phase-06/load_test.py` |
| 6.4.4 | Runbook: ops, alerts, scrape recovery | `phases/phase-06-agentic-scale/RUNBOOK.md` |

### 9.2 Phase 6 exit criteria

- [ ] Agent answers 3+ step analytical questions with citations
- [ ] Daily incremental scrape runs unattended
- [ ] Full corpus (~35M) validated and indexed
- [ ] Production SLAs: search < 500ms p95, RAG < 8s p95
- [ ] All problem statement success criteria met

---

## 10. Master Checklist — Success Criteria

From [problemstatement.md](../docs/problemstatement.md):

| # | Success criterion | Phase | Verification |
|---|-------------------|-------|--------------|
| 1 | Aggregate 6-month Google Play reviews into unified knowledge base | 1 | `scrape.py --validate` (zero out-of-window) |
| 2 | Transform unstructured → structured, searchable insights | 2 | `structured_reviews` populated |
| 3 | Identify recurring discovery issues with semantic accuracy | 3, 5 | Eval search + cluster coherence |
| 4 | Conversational RAG querying | 4 | 50-question eval set |
| 5 | Surface product opportunities with real evidence | 5 | Insight reports with `evidence_document_ids` |
| 6 | Distinguish user segments and unique challenges | 2, 4 | Segment filter queries work |
| 7 | Reveal hidden behavioral patterns | 5, 6 | Agent comparative analysis |
| 8 | Scale to large datasets | 6 | Load test on full corpus |

---

## 11. File Creation Order (Quick Reference)

Build in this sequence to avoid blocked dependencies:

```
1.  src/shared/config.py, constants.py
2.  src/database/models/, migrations/, repositories/
3.  src/scrape/normalizer.py → pagination.py → checkpoint.py → scraper.py → validator.py
4.  src/cleaning/pipeline.py
5.  scripts/scrape.py
6.  src/api/main.py, routes/scrape.py, routes/reviews.py
7.  src/extraction/schema.py → language.py → translation.py → extractor.py
8.  src/orchestration/celery_app.py, tasks/extract.py
9.  src/embedding/embedder.py → indexer.py
10. src/search/semantic_search.py
11. src/api/routes/search.py
12. src/rag/retriever.py → fusion.py → reranker.py → generator.py → pipeline.py
13. src/api/routes/query.py
14. src/clustering/clusterer.py → labeler.py
15. src/insights/aggregator.py → trends.py → root_cause.py
16. src/api/routes/clusters.py, insights.py, trends.py
17. src/agent/orchestrator.py, tools/
18. src/api/routes/agent.py
19. config/deployment/, docker-compose.prod.yml
```

---

## 12. Risk Register

| Risk | Impact | Mitigation | Phase |
|------|--------|------------|-------|
| Play Store rate limiting / IP block | Scrape stalls | Checkpoint resume, delays, SerpAPI fallback, proxies | 1 |
| 35M full listing scrape | Not in scope — 6-month window only | N/A | 1 |
| LLM extraction cost at scale | Moderate (6-month corpus only) | Batch processing, content-hash cache | 2 |
| Embedding index size | Storage/latency | Partition by year, pgvector vs Qdrant benchmark | 3, 6 |
| RAG hallucination | Wrong product decisions | Citation validator, NLI faithfulness check | 4 |
| Cluster drift over time | Stale themes | Weekly re-cluster + incremental assign | 5 |

---

## 13. Definition of Done (Per Phase)

A phase is **complete** when:

1. All tasks in the phase section are checked off
2. Exit criteria tests pass
3. `phases/phase-XX-*/REQUIREMENTS.md` checklist updated
4. Tests in `tests/phase-XX/` pass in CI
5. Relevant API endpoints documented and manually verified
6. Next phase can start without blocking dependencies

---

## 14. Related Documents

| Document | Path |
|----------|------|
| Architecture | [docs/ragarchitecture.md](../docs/ragarchitecture.md) |
| Problem statement | [docs/problemstatement.md](../docs/problemstatement.md) |
| Phase requirements | [phases/](../phases/) |
| Domain requirements | [requirements/](../requirements/) |
| Environment template | [config/.env.example](../config/.env.example) |

---

*Last updated: 6-month rolling window (SCRAPE_MONTHS_BACK=6), Google Play single-source, 6-phase delivery.*
