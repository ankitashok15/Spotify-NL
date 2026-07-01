# Phase 6 Implementation Summary

**Status:** Code complete. Full-corpus scale validation and production SLAs require runtime infrastructure.

Maps [docs/ragarchitecture.md](../../docs/ragarchitecture.md) Phase 6 and [src/implementationplan.md](../../src/implementationplan.md) §9 to `phases/phase-06-agentic-scale/`.

---

## Folder layout

```
phases/phase-06-agentic-scale/
├── phase06/
│   ├── agent/                 # Orchestrator + 6 tools
│   ├── api/                   # POST /api/v1/agent/query (port 8004)
│   ├── orchestration/         # Celery app, schedules, incremental pipeline
│   ├── rag/cache.py           # Redis + in-memory query cache
│   ├── embedding/partition.py # Year-partitioned Qdrant collections
│   ├── database/              # agent_queries audit table
│   └── shared/                # config, observability (Langfuse stub)
├── cli/agent.py               # init-db | query | pipeline
├── cli/serve.py
├── docker-compose.prod.yml
├── IMPLEMENTATION.md
└── RUNBOOK.md
```

Repo-level deployment: `config/deployment/api.Dockerfile`, `worker.Dockerfile`, `monitoring/prometheus.yml`

---

## Sprint 6.1 — Agent orchestrator

| Task | File |
|------|------|
| 6.1.1 Agent loop | `phase06/agent/orchestrator.py` |
| 6.1.2 `semantic_search` | `phase06/agent/tools/semantic_search.py` |
| 6.1.3 `structured_query` | `phase06/agent/tools/structured_query.py` |
| 6.1.4 `get_cluster` | `phase06/agent/tools/get_cluster.py` |
| 6.1.5 `compare_segments` | `phase06/agent/tools/compare_segments.py` |
| 6.1.6 `get_trends` | `phase06/agent/tools/get_trends.py` |
| 6.1.7 `summarize_evidence` | `phase06/agent/tools/summarize_evidence.py` |
| 6.1.8 API route | `phase06/api/routes/agent.py` |

**Flow:** LLM planner (or heuristic fallback) → up to 6 tool calls → `summarize_evidence` → citations.

---

## Sprint 6.2 — Incremental ingestion

| Task | File |
|------|------|
| 6.2.1 Daily Celery Beat | `phase06/orchestration/schedules.py`, `tasks/scrape.py` |
| 6.2.2 Pipeline trigger | `phase06/orchestration/pipeline.py`, `tasks/pipeline.py` |
| 6.2.3 thumbs_up / reply updates | Phase 1 `scrape_incremental` (reused) |

**Pipeline:** scrape → extract → embed → cluster assign → (optional) insights.

---

## Sprint 6.3 — Production scale

| Task | File | Notes |
|------|------|-------|
| 6.3.1 Partitioned vectors | `phase06/embedding/partition.py` | `spotify_reviews_YYYY` collections |
| 6.3.2 Redis cache | `phase06/rag/cache.py` | Agent response cache |
| 6.3.3 Blue-green reindex | `scripts/reindex_vectors.py` | Suffix collections `_v2` |
| 6.3.4 API key auth | `phase06/api/dependencies.py` | Optional `API_KEY` |
| 6.3.5 Prometheus | `config/deployment/monitoring/prometheus.yml` | Health scrape skeleton |
| 6.3.6 Langfuse | `phase06/shared/observability.py` | No-op without keys |

---

## Sprint 6.4 — Deployment

| Task | File |
|------|------|
| 6.4.1 Dockerfiles | `config/deployment/api.Dockerfile`, `worker.Dockerfile` |
| 6.4.2 docker-compose.prod | `phases/phase-06-agentic-scale/docker-compose.prod.yml` |
| 6.4.3 Load test | `tests/phase-06/load_test.py` (Locust skeleton) |
| 6.4.4 Runbook | `RUNBOOK.md` |

---

## Environment variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `API_PORT` | `8004` | Phase 6 API |
| `API_KEY` | — | Optional `X-API-Key` auth |
| `REDIS_URL` | `redis://localhost:6379/0` | Cache + Celery broker |
| `CELERY_BROKER_URL` | same | Job queue |
| `AGENT_MAX_STEPS` | `6` | Tool loop limit |
| `LANGFUSE_*` | — | LLM tracing |
| `EMBEDDING_PARTITION_BY_YEAR` | `true` | Year-suffixed Qdrant collections |

---

## Tests

```powershell
python -m pytest tests/phase-06/ -v
```

---

## Exit criteria (runtime)

| Criterion | Code | Runtime |
|-----------|------|---------|
| 3+ step agent questions | ✅ | Needs Gemini + indexed data |
| Daily incremental scrape | ✅ Celery Beat | Needs Redis + worker |
| Full corpus indexed | ✅ partition + reindex script | Needs scale infra |
| Search <500ms / RAG <8s p95 | Load test skeleton | Run Locust against prod |
