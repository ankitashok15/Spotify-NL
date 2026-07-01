# Phase 6 Requirements — Agentic & Production Scale

## Scope

Agent workflows for complex analysis, incremental scraping, and production hardening for the full ~35M review corpus.

## Functional requirements

### FR-6.1 Agent orchestrator

- [ ] Tools: `semantic_search`, `structured_query`, `get_cluster`, `compare_segments`, `get_trends`, `summarize_evidence`
- [ ] Multi-step plan → execute → synthesize with citations
- [ ] `POST /api/v1/agent/query`

### FR-6.2 Incremental scraping

- [ ] Daily job: fetch new reviews since `last_scraped_at`
- [ ] Upsert new rows; update thumbs_up / developer_reply on existing
- [ ] Enqueue new reviews into Phase 2+ pipeline

### FR-6.3 Production scale

- [ ] Partitioned vector index by year
- [ ] Batch backfill for embeddings/extraction at scale
- [ ] Redis cache for frequent queries
- [ ] LLM extraction cache by content hash

### FR-6.4 Deployment & monitoring

- [ ] Docker / cloud deployment
- [ ] Prometheus + Grafana metrics
- [ ] Langfuse LLM observability
- [ ] Alerting on scrape failures

## Non-functional requirements

| ID | Requirement |
|----|-------------|
| NFR-6.1 | Handle full ~35M review corpus |
| NFR-6.2 | Daily incremental scrape unattended |
| NFR-6.3 | Agent answers 3+ step analytical questions |

## Exit criteria

- Full corpus scrape validated (≥ 99.5%)
- Agent handles comparative segment questions
- Production SLAs met at scale
