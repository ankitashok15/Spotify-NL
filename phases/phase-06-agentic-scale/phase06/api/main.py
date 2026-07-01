from fastapi import FastAPI

from phase06.api.routes import agent
from phase06.database.models import init_phase6_tables
from phase06.shared.config import settings

app = FastAPI(
    title="Spotify NL — Phase 6 API",
    description="Agent orchestrator, incremental pipeline, production scale",
    version="0.6.0",
)


@app.on_event("startup")
def on_startup():
    init_phase6_tables(settings.database_url)


app.include_router(agent.router)


@app.get("/health")
def health():
    return {"status": "ok", "phase": 6, "model": settings.gemini_model_rag}
