# Phase 6 — Agentic Workflows & Production Scale

**Goal:** Multi-step analytical agent, incremental ingestion, and production hardening.

## Related requirements

- [requirements/agent](../../requirements/agent/REQUIREMENTS.md)
- [requirements/orchestration](../../requirements/orchestration/REQUIREMENTS.md)

## Source code

- `phase06/agent/` — orchestrator + 6 tools
- `phase06/api/` — `POST /api/v1/agent/query` on port **8004**
- `phase06/orchestration/` — Celery Beat, incremental pipeline
- `cli/agent.py` — init-db, query, pipeline
- `docker-compose.prod.yml` — API ×2, workers, Redis, PG, Qdrant

## Prerequisite

Phases 1–5 (scrape, extract, embed, RAG, cluster/insights).

See [RUNBOOK.md](./RUNBOOK.md) and [IMPLEMENTATION.md](./IMPLEMENTATION.md).
