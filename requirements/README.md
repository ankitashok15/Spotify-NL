# Requirements Index

Cross-cutting requirement specs for the Spotify Google Play Review Discovery Engine.

Each folder defines **what** must be built for a domain. Phase folders under `phases/` define **when** those domains are delivered.

| Folder | Domain | Primary phase |
|--------|--------|---------------|
| [scrape](./scrape/) | Full corpus Google Play scraping | Phase 1 |
| [database](./database/) | PostgreSQL, vector DB, schemas | Phase 1, 3 |
| [api](./api/) | REST API endpoints | Phase 1–6 |
| [cleaning](./cleaning/) | Review normalization (no deletion) | Phase 1 |
| [llm](./llm/) | Google Gemini (extraction, RAG, insights) | Phase 2–6 |
| [extraction](./extraction/) | Language detection, Gemini structured extraction | Phase 2 |
| [embedding](./embedding/) | Gemini embeddings (`text-embedding-004`) | Phase 3 |
| [rag](./rag/) | Hybrid retrieval, reranking, grounded Q&A | Phase 4 |
| [clustering](./clustering/) | Theme clustering, taxonomy | Phase 5 |
| [insights](./insights/) | Trend analysis, product intelligence reports | Phase 5 |
| [agent](./agent/) | Multi-step agentic workflows | Phase 6 |
| [orchestration](./orchestration/) | Jobs, queues, scheduling, deployment | Phase 1, 6 |

See also: [phases/README.md](../phases/README.md) | [docs/ragarchitecture.md](../docs/ragarchitecture.md)
