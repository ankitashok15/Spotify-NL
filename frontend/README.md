# Spotify NL — Frontend

React + Vite dashboard for the review discovery engine.

## Pages

- **Dashboard** — corpus stats, top issues
- **Semantic Search** — vector search over reviews
- **Ask (RAG)** — citation-backed Q&A
- **Agent** — multi-step analytical queries
- **Themes** — cluster explorer
- **Insights** — generated reports
- **Reviews** — raw review browser

## Run

```powershell
cd frontend
npm install
npm run dev
```

Open http://localhost:5173 — Vite proxies `/api` to the backend on port 8080.

Start the backend first: `python scripts/serve_api.py`
