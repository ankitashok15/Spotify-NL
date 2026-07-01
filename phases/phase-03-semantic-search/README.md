# Phase 3 — Semantic Search

**Goal:** Embed all reviews and expose semantic similarity search over the corpus.

## Related requirements

- [requirements/embedding](../../requirements/embedding/REQUIREMENTS.md)
- [requirements/database](../../requirements/database/REQUIREMENTS.md) (vector store)
- [requirements/api](../../requirements/api/REQUIREMENTS.md) (`/search`)

## Source code

- `phase03/embedding/` — Gemini embeddings, templates, Qdrant indexer
- `phase03/search/` — semantic search service + filters
- `phase03/api/` — `POST /api/v1/search`
- `cli/embed.py` — init-qdrant, embed, status
- `cli/serve.py` — search API (port 8001)
- `docker-compose.yml` — Qdrant

## Prerequisite

Phase 1 corpus required; Phase 2 structured fields recommended.

See [RUNBOOK.md](./RUNBOOK.md) and [REQUIREMENTS.md](./REQUIREMENTS.md).
