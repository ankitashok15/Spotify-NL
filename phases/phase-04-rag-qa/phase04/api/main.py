from fastapi import FastAPI

from phase04.api.routes import query
from phase04.database.models import init_phase4_tables
from phase04.shared.config import settings

app = FastAPI(
    title="Spotify NL — Phase 4 API",
    description="RAG Q&A over Google Play reviews with citations",
    version="0.4.0",
)


@app.on_event("startup")
def on_startup():
    init_phase4_tables(settings.database_url)


app.include_router(query.router)


@app.get("/health")
def health():
    return {"status": "ok", "phase": 4, "model": settings.gemini_model_rag}
