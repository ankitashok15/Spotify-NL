# RAG Requirements

**Phase:** 4  
**Source:** `src/rag/`

## Pipeline

```
Question → Router → Enhancement → Hybrid Retrieve → Rerank → Context Build → Gemini → Citation Validate
```

## Modules

| Module | Responsibility |
|--------|----------------|
| `router.py` | Intent + filter extraction |
| `enhancement.py` | Query rewrite, optional HyDE |
| `retriever.py` | Dense + BM25 + SQL pre-filter |
| `fusion.py` | Reciprocal Rank Fusion |
| `reranker.py` | Cross-encoder re-scoring |
| `context.py` | Evidence pack assembly |
| `generator.py` | Gemini grounded answer |
| `citations.py` | Citation validation |

## Retrieval config

| Parameter | Value |
|-----------|-------|
| top-K (retrieve) | 50–100 |
| top-N (rerank) | 10–20 |

## Generation (Google Gemini)

- Model: `GEMINI_MODEL_RAG` (default: `gemini-2.0-flash`)
- Answer ONLY from retrieved evidence
- Mandatory `[1]`, `[2]` citations
- State insufficient evidence when applicable
- Synthesize patterns; distinguish segments when supported

## Evaluation

- 50-question eval set
- Citation accuracy > 90%
- Faithfulness scoring (optional NLI)
