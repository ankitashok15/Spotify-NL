# Embedding Requirements

**Phase:** 3  
**Source:** `src/embedding/`  
**Provider:** Google Gemini embeddings (not OpenAI)

## Models

| Model | Provider | Notes |
|-------|----------|-------|
| `text-embedding-004` | **Google Gemini** (primary) | Same `GEMINI_API_KEY` |
| `bge-m3` | Local open-source | Optional offline fallback |

## Modules

| Module | Responsibility |
|--------|----------------|
| `embedder.py` | Batch + online embedding via Gemini |
| `templates.py` | Input text template for review + metadata |
| `indexer.py` | Write vectors to Qdrant/pgvector |
| `versioning.py` | Track `embedding_model_version` |

## Input template

```
Review: {text_en}
Rating: {rating}/5
Issues: {primary_issue}, {secondary_issues}
Features: {mentioned_features}
```

## Environment

```env
GEMINI_API_KEY=...
GEMINI_EMBEDDING_MODEL=text-embedding-004
```

## Batch processing

- Batch size: 100–500
- Job queue for 6-month corpus backfill
- Online embedding for query-time search

## Vector payload

`document_id`, `rating`, `device_type`, `subscription_type`, `primary_issue`, `is_discovery_related`, `review_created_at`, `thumbs_up`, `cluster_ids[]`

## Output

- Vector DB indexed
- `processing_state = EMBEDDED` → `INDEXED`
