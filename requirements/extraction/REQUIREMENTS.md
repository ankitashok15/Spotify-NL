# Extraction Requirements

**Phase:** 2  
**Source:** `src/extraction/`  
**LLM:** Google Gemini only — see [requirements/llm/REQUIREMENTS.md](../llm/REQUIREMENTS.md)

## Pipeline

```
reviews (CLEANED) → language detect → translate → Gemini extract → structured_reviews
```

## Modules

| Module | Responsibility |
|--------|----------------|
| `language.py` | Detect language (langdetect / CLD3) |
| `translation.py` | Translate to `text_en` via Gemini when needed |
| `extractor.py` | Gemini structured JSON extraction |
| `schema.py` | Pydantic models for extraction JSON |
| `enrichment.py` | Feature name normalization, Play Store metadata cross-check |
| `batch.py` | Batch 20–50 reviews per Gemini call |

## Extraction fields

`summary`, `primary_issue`, `secondary_issues`, `emotions`, `sentiment`, `recommendation_quality`, `user_intent`, `listening_context`, `mentioned_features`, `feature_requests`, `pain_points`, `behaviors`, `severity`, `urgency`, `subscription_type`, `user_persona_signals`, `is_discovery_related`, `confidence`

## Gemini configuration

| Setting | Value |
|---------|-------|
| SDK | `google-generativeai` |
| Model | `GEMINI_MODEL` (default: `gemini-2.0-flash`) |
| Output | JSON schema / `response_mime_type: application/json` |
| Validation | Pydantic; retry on malformed output (max 3) |

## Output

- Table: `structured_reviews`
- State: `processing_state = EXTRACTED`
