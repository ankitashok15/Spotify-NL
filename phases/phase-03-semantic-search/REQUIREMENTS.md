# Phase 3 Requirements — Semantic Search

## Scope

Generate vector embeddings for all reviews and enable meaning-based search with metadata filters.

## Functional requirements

### FR-3.1 Embedding generation

- [ ] Embed full corpus in batches (100–500 per batch)
- [ ] Input template: review text + rating + issues + features
- [ ] Store `embedding_model_version` per vector
- [ ] Update `processing_state` to `EMBEDDED`

### FR-3.2 Vector database

- [ ] Index document-level embeddings with metadata payload
- [ ] Payload: document_id, rating, device_type, subscription_type, primary_issue, is_discovery_related, review_created_at, thumbs_up

### FR-3.3 Semantic search API

- [ ] `POST /api/v1/search` — query + filters + top_k
- [ ] Return ranked reviews with similarity scores (no LLM generation)

### FR-3.4 Evaluation

- [ ] 20 test queries with expected relevant reviews
- [ ] Paraphrase matching verified (e.g. "same songs" ≈ "recommendations never change")

## Non-functional requirements

| ID | Requirement |
|----|-------------|
| NFR-3.1 | Search p95 latency < 500ms on dev corpus |

## Exit criteria

- Full corpus embedded and indexed
- Metadata filters (rating, subscription, date) work
- Semantic paraphrase retrieval validated
