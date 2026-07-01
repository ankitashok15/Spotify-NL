import backend.app.bootstrap  # noqa: F401 — path setup before phase imports

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.config import settings
from backend.app.routes import dashboard
from phase01.api.routes import ingest, reviews, scrape
from phase01.database.models import init_db
from phase01.shared.config import settings as phase1_settings
from phase03.api.routes import search
from phase04.api.routes import query
from phase05.api.routes import clusters, insights, trends
from phase06.api.routes import agent
from phase06.database.models import init_phase6_tables

app = FastAPI(
    title="Spotify NL API",
    description="Unified API — scrape, search, RAG, clusters, insights, agent",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    phase1_settings.raw_data_dir.mkdir(parents=True, exist_ok=True)
    init_db(settings.database_url)
    init_phase6_tables(settings.database_url)


app.include_router(dashboard.router)
app.include_router(scrape.router)
app.include_router(reviews.router)
app.include_router(ingest.router)
app.include_router(search.router)
app.include_router(query.router)
app.include_router(clusters.router)
app.include_router(insights.router)
app.include_router(trends.router)
app.include_router(agent.router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "spotify-nl-api"}
