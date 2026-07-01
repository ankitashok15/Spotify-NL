# Cleaning pipeline requirements (Phase 1)

Part of [phase-01-data-foundation](../../phases/phase-01-data-foundation/REQUIREMENTS.md).

## Rules

- Normalize to `text_cleaned`; never overwrite `text_original`
- Tag `is_spam` and `is_near_duplicate`; do not delete rows
- Rating-only reviews: `text_cleaned = null`, row retained
- No relevance filtering at clean stage (deferred to Phase 2 `is_discovery_related`)

## Source

`src/cleaning/`
