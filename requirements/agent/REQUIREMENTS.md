# Agent Requirements

**Phase:** 6  
**Source:** `src/agent/`

## Orchestrator

Plan → tool call → observe → iterate → final synthesis with citations.

Framework options: LangGraph, custom tool-calling loop.

## Tools

| Tool | Input | Output |
|------|-------|--------|
| `semantic_search` | query, filters | ranked reviews |
| `structured_query` | SQL-like aggregation spec | counts, rankings |
| `get_cluster` | cluster_id | cluster + samples |
| `compare_segments` | segment A, segment B, topic | parallel evidence |
| `get_trends` | theme, date range | time-series |
| `summarize_evidence` | document_ids[] | synthesis |

## When to use agent vs simple RAG

| Complexity | Path |
|------------|------|
| Single-topic lookup | Direct RAG (`/query`) |
| Comparative / multi-step | Agent (`/agent/query`) |
| Dashboard metrics | Structured SQL API |

## Example query

*"What discovery issues do free phone users report most, and how has that changed in 2026?"*

1. `structured_query` — top issues, free + phone
2. `get_trends` — 2026 filter
3. `semantic_search` — sample reviews per issue
4. `summarize_evidence` — final report

## API

`POST /api/v1/agent/query` — returns answer, citations, tool trace (optional debug mode)
