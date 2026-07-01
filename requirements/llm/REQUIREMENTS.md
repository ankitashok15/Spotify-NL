# LLM Requirements — Google Gemini

**Phases:** 2–6  
**Provider:** [Google Gemini API](https://ai.google.dev/) (not OpenAI)

## Credentials

| Variable | Required | Default | Purpose |
|----------|----------|---------|---------|
| `GEMINI_API_KEY` | Yes (Phase 2+) | — | Google AI Studio API key |
| `GEMINI_MODEL` | No | `gemini-2.0-flash` | Extraction, clustering, insights |
| `GEMINI_MODEL_RAG` | No | `gemini-2.0-flash` | RAG answers, agent |
| `GEMINI_EMBEDDING_MODEL` | No | `text-embedding-004` | Phase 3 embeddings |

Get a key at: https://aistudio.google.com/apikey

## Python SDK

```
google-generativeai>=0.8.0
```

## Model usage by phase

| Phase | Task | Model |
|-------|------|-------|
| 2 | Structured extraction | `gemini-2.0-flash` |
| 2 | Translation (optional) | `gemini-2.0-flash` |
| 3 | Embeddings | `text-embedding-004` |
| 4 | RAG generation | `gemini-2.0-flash` |
| 5 | Cluster labeling, root cause | `gemini-2.0-flash` |
| 6 | Agent orchestration | `gemini-2.0-flash` |

## Implementation

| Module | Path |
|--------|------|
| Provider abstraction | `phase02/shared/llm_provider.py` |
| Gemini client | `phase02/shared/llm_gemini.py` |

## Structured output

Use Gemini JSON mode / response schema for Phase 2 extraction:

```python
import google.generativeai as genai

genai.configure(api_key=settings.gemini_api_key)
model = genai.GenerativeModel(
    settings.gemini_model,
    generation_config={"response_mime_type": "application/json"},
)
```

## Not used

- OpenAI (`OPENAI_API_KEY`) — **not used in this project**
- Anthropic (`ANTHROPIC_API_KEY`) — **not used in this project**
