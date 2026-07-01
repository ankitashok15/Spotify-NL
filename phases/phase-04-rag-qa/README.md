# Phase 4 — RAG Q&A

**Goal:** Natural-language product questions with grounded, citation-backed answers from Google Play reviews.

## Related requirements

- [requirements/rag](../../requirements/rag/REQUIREMENTS.md)
- [requirements/llm](../../requirements/llm/REQUIREMENTS.md)
- [requirements/api](../../requirements/api/REQUIREMENTS.md)

## Source code

- `phase04/rag/` — router, hybrid retrieval, fusion, reranker, generator, citations
- `phase04/api/` — `POST /api/v1/query`
- `phase04/database/` — `queries` audit log
- `cli/query.py` — init-db, ask
- `cli/serve.py` — RAG API (port 8002)

## Prerequisite

Phase 3 semantic search operational (Qdrant indexed). Phase 2 structured fields strongly recommended.

See [RUNBOOK.md](./RUNBOOK.md) and [REQUIREMENTS.md](./REQUIREMENTS.md).
