# Orchestration Requirements

**Phases:** 1 (scrape jobs), 2–5 (pipeline workers), 6 (production)  
**Source:** `src/orchestration/`

## Components

| Component | Technology | Use |
|-----------|------------|-----|
| Job queue | Celery + Redis | Async scrape, extract, embed jobs |
| Scheduler | Celery Beat / cron | Daily incremental scrape |
| Workflow | Prefect / Airflow (optional) | Multi-step DAG pipelines |
| Dead letter queue | Redis / DB | Failed job inspection |

## Job types

| Job | Phase | Trigger |
|-----|-------|---------|
| `scrape_full` | 1 | Manual / one-time |
| `scrape_incremental` | 6 | Daily cron |
| `clean_reviews` | 1 | After scrape batch |
| `extract_reviews` | 2 | After clean |
| `embed_reviews` | 3 | After extract |
| `cluster_reviews` | 5 | Weekly |
| `generate_insights` | 5 | Weekly |

## Processing state machine

```
RAW → CLEANED → TRANSLATED → EXTRACTED → EMBEDDED → CLUSTERED → INDEXED
```

Each transition: idempotent, keyed by `document_id + pipeline_version`.

## Deployment (Phase 6)

```
config/
├── docker-compose.yml
├── .env.example
└── deployment/
    ├── api.Dockerfile
    └── worker.Dockerfile
```

## Monitoring

- Prometheus metrics: job duration, queue depth, scrape rate
- Langfuse: LLM call traces
- Alerts: scrape failure, validation gap > 0.5%
