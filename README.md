# Spotify NL — Google Play Review Discovery Engine

AI-powered review analysis for **Spotify** (`com.spotify.music`) on Google Play.

## Project structure

| Folder | Purpose |
|--------|---------|
| [docs/](./docs/) | Problem statement & architecture |
| [phases/](./phases/) | Phase 1–6 implementations |
| [backend/](./backend/) | **Unified API** (port 8080) |
| [frontend/](./frontend/) | **React dashboard** (port 5173) |
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

## Quick start (UI)

```powershell
# 1. Infrastructure
docker compose -f docker-compose.dev.yml up -d

# 2. Backend API (port 8080)
.\.venv\Scripts\pip install -r requirements.txt
.\.venv\Scripts\python scripts\serve_api.py

# 3. Frontend (port 5173)
cd frontend
npm install
npm run dev
```

Open http://localhost:5173

## Production deployment

| App | Platform |
|-----|----------|
| Python backend UI | [Streamlit Cloud](https://share.streamlit.io) — `streamlit_app.py` |
| REST API (for React) | [Render](https://render.com) — `render.yaml` |
| React frontend | [Vercel](https://vercel.com) — `frontend/` |

See **[DEPLOY.md](./DEPLOY.md)** for step-by-step instructions.
