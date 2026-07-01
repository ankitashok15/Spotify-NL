# Deployment Guide — Streamlit + Vercel

This project uses **two hosting platforms** plus a small REST API service for the React UI.

| Component | Platform | Purpose |
|-----------|----------|---------|
| **Python backend UI** | [Streamlit Community Cloud](https://streamlit.io/cloud) | Dashboard, search, RAG, agent (in-process Python) |
| **REST API** | [Render](https://render.com) (free tier) | Powers the Vercel React app via HTTP |
| **React frontend** | [Vercel](https://vercel.com) | Production web UI |

> Streamlit Cloud cannot expose a FastAPI REST API. The Vercel frontend needs the Render API URL.

---

## 1. Streamlit Cloud (Python backend)

1. Push this repo to GitHub (already done: `ankitashok15/Spotify-NL`).
2. Go to [share.streamlit.io](https://share.streamlit.io) → **New app**.
3. Repository: `ankitashok15/Spotify-NL`, branch `master`.
4. **Main file path:** `streamlit_app.py`
5. **App settings → Secrets** — paste from `.streamlit/secrets.toml.example`:

```toml
DATABASE_URL = "postgresql://..."
GEMINI_API_KEY = "..."
QDRANT_URL = "https://..."
GEMINI_MODEL = "gemini-2.5-flash"
GEMINI_EMBEDDING_MODEL = "gemini-embedding-001"
```

6. Deploy. Your app URL will look like: `https://spotify-nl-xxxxx.streamlit.app`

### Streamlit requirements

- Hosted **PostgreSQL** (Neon, Supabase, or Render Postgres)
- Hosted **Qdrant Cloud** (or reachable Qdrant instance)
- `GEMINI_API_KEY` from [Google AI Studio](https://aistudio.google.com/apikey)

---

## 2. Render (REST API for Vercel)

1. Go to [dashboard.render.com](https://dashboard.render.com) → **New → Blueprint**.
2. Connect repo `ankitashok15/Spotify-NL` — Render reads `render.yaml`.
3. Set secret env vars when prompted:
   - `DATABASE_URL`
   - `GEMINI_API_KEY`
   - `QDRANT_URL`
4. Deploy. Note the API URL, e.g. `https://spotify-nl-api.onrender.com`

Test: `curl https://spotify-nl-api.onrender.com/health`

---

## 3. Vercel (React frontend)

1. Go to [vercel.com/new](https://vercel.com/new) → Import `ankitashok15/Spotify-NL`.
2. **Root Directory:** `frontend`
3. Framework: **Vite** (auto-detected via `vercel.json`)
4. **Environment variables** (required — without this you get HTTP 405):

| Name | Value |
|------|-------|
| `VITE_API_URL` | `https://spotify-nl-api.onrender.com` (your **Render** API URL — **not** the Streamlit URL) |

5. Deploy. Your app URL: `https://spotify-nl.vercel.app` (or custom name)

Set `GEMINI_EMBEDDING_MODEL=gemini-embedding-001` on Render and Streamlit (not `text-embedding-004`).

In Render dashboard, set `CORS_ORIGINS` to include your Vercel URL:

```
https://your-app.vercel.app
```

---

## Architecture

```
┌─────────────────────┐     ┌─────────────────────┐
│  Streamlit Cloud    │     │  Vercel (React)      │
│  streamlit_app.py   │     │  frontend/           │
│  Direct Python/DB   │     │  VITE_API_URL ───────┼──┐
└─────────────────────┘     └─────────────────────┘  │
                                                        ▼
                                           ┌─────────────────────┐
                                           │  Render (FastAPI)    │
                                           │  scripts/serve_api.py│
                                           └──────────┬──────────┘
                                                      │
                              ┌────────────────────────┼────────────────────────┐
                              ▼                        ▼                        ▼
                         PostgreSQL               Qdrant Cloud              Gemini API
```

---

## Local development

```powershell
# API
python scripts/serve_api.py

# Streamlit
streamlit run streamlit_app.py

# Frontend
cd frontend && npm run dev
```

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Vercel shows API errors | Set `VITE_API_URL` to Render URL; redeploy Vercel |
| CORS blocked | Add Vercel URL to `CORS_ORIGINS` on Render |
| Streamlit DB error | Check `DATABASE_URL` in Streamlit secrets |
| Render cold start | Free tier sleeps after 15 min — first request may take ~30s |
