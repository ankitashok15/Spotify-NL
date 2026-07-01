# Spotify NL — Google Play Review Discovery Engine

AI-powered review analysis for **Spotify** (`com.spotify.music`) on Google Play.

## Project structure

| Folder | Purpose |
|--------|---------|
| [docs/](./docs/) | Problem statement & architecture |
| [phases/phase-01-data-foundation/](./phases/phase-01-data-foundation/) | **Phase 1 implementation** (scraper, DB, API) |
| [requirements/](./requirements/) | Domain specs: API, Scrape, Database, RAG, etc. |
| [src/](./src/) | Implementation code |
| [scripts/](./scripts/) | CLI tools |
| [tests/](./tests/) | Phase-based tests |
| [data/](./data/) | Raw scrape storage |

## Phases

1. **Data Foundation** — scrape Play Store reviews (6-month window)
2. **AI Understanding** — structured Gemini extraction
3. **Semantic Search** — embeddings + search API
4. **RAG Q&A** — citation-backed answers
5. **Clustering & Insights** — themes and trends
6. **Agentic & Scale** — multi-step agent, production pipeline

All six phases are implemented under [phases/](./phases/). See [phases/README.md](./phases/README.md) and [docs/ragarchitecture.md](./docs/ragarchitecture.md).
