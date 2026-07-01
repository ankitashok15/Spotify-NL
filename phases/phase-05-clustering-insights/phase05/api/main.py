from fastapi import FastAPI

from phase05.api.routes import clusters, insights, trends
from phase05.database.models import init_phase5_tables
from phase05.shared.config import settings

app = FastAPI(
    title="Spotify NL — Phase 5 API",
    description="Clustering, insights, and trends over Google Play reviews",
    version="0.5.0",
)


@app.on_event("startup")
def on_startup():
    init_phase5_tables(settings.database_url)


app.include_router(clusters.router)
app.include_router(insights.router)
app.include_router(trends.router)


@app.get("/health")
def health():
    return {"status": "ok", "phase": 5}
