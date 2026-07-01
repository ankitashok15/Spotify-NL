# Phase 2 — AI Understanding

**Goal:** Extract structured product intelligence from every review via language detection, translation, and **Google Gemini** extraction.

## Related requirements

- [requirements/llm](../../requirements/llm/REQUIREMENTS.md) — Gemini API key & models
- [requirements/extraction](../../requirements/extraction/REQUIREMENTS.md)
- [requirements/database](../../requirements/database/REQUIREMENTS.md)

## Source code

- `phase02/extraction/` — language, translation, Gemini extractor, pipeline
- `phase02/shared/` — config, `llm_gemini.py`, `llm_provider.py`
- `phase02/database/` — `structured_reviews`, `extraction_cache`
- `cli/extract.py` — init-db, extract, status

## Prerequisite

Phase 1 complete — 6-month review corpus in PostgreSQL.  
**LLM:** Google Gemini (`GEMINI_API_KEY`) — not OpenAI.

See [REQUIREMENTS.md](./REQUIREMENTS.md).
