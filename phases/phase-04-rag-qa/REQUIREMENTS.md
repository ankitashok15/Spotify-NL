# Phase 4 Requirements — RAG Q&A

## Scope

Hybrid retrieval + LLM generation with mandatory citations from Play Store review evidence.

## Functional requirements

### FR-4.1 Query routing

- [ ] Parse intent and extract filters (subscription, rating, date, feature, persona)

### FR-4.2 Hybrid retrieval

- [ ] Dense vector search
- [ ] Sparse BM25 on text + pain_points
- [ ] SQL metadata pre-filters
- [ ] Reciprocal Rank Fusion (RRF) merge
- [ ] Cross-encoder reranking → top 10–20

### FR-4.3 Grounded generation

- [ ] LLM answers only from retrieved context
- [ ] Inline citations `[1]`, `[2]`, etc.
- [ ] Evidence pack includes rating, device, thumbs_up, date

### FR-4.4 Citation validation

- [ ] Every citation maps to a retrieved document
- [ ] Flag unsupported claims

### FR-4.5 API

- [ ] `POST /api/v1/query` — question + optional filters

### FR-4.6 Supported question types

- [ ] "Why do users dislike X?"
- [ ] "Show reviews mentioning Y"
- [ ] "What do Premium users complain about?"
- [ ] "Top discovery issues among 1-star reviews"
- [ ] "Most frequent feature requests"
- [ ] "How have complaints changed this year?"

## Non-functional requirements

| ID | Requirement |
|----|-------------|
| NFR-4.1 | RAG p95 latency < 8s |
| NFR-4.2 | Citation accuracy > 90% on eval set |

## Exit criteria

- 50-question eval set passes human review
- All answers cite only retrieved Play Store reviews
