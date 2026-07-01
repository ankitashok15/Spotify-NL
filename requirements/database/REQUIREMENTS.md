# Database Requirements

**Phases:** 1 (PostgreSQL), 3 (vector DB), 5 (cluster tables)  
**Source:** `src/database/`

## PostgreSQL tables

### Phase 1

| Table | Purpose |
|-------|---------|
| `reviews` | All scraped reviews (system of record) |
| `scrape_runs` | Backfill/incremental run metadata |
| `scrape_checkpoints` | Resumable pagination tokens |
| `dedup_index` | Content hash → review_id |

### Phase 2

| Table | Purpose |
|-------|---------|
| `structured_reviews` | LLM-extracted fields per review |

### Phase 5

| Table | Purpose |
|-------|---------|
| `clusters` | Theme definitions |
| `cluster_memberships` | review ↔ cluster mapping |
| `insights` | Generated insight records |
| `queries` | RAG query audit log |

## Vector database (Phase 3+)

| Option | Notes |
|--------|-------|
| Qdrant | Recommended for scale |
| pgvector | Simpler single-DB setup |

**Index:** document-level embeddings with metadata payload.

## Migrations

- `src/database/migrations/` — Alembic or SQL migration files per phase
- `src/database/models/` — SQLAlchemy / Pydantic models
- `src/database/repositories/` — data access layer

## Key constraints

- `reviews.external_review_id` UNIQUE
- `processing_state` enum: `RAW | CLEANED | TRANSLATED | EXTRACTED | EMBEDDED | CLUSTERED | INDEXED`
- Foreign keys: `structured_reviews.review_id` → `reviews.id`

## Object storage

- `data/raw/play_store/` — raw scrape JSON (local dev)
- S3/MinIO for production
