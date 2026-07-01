from fastapi import FastAPI

from phase01.api.routes import ingest, reviews, scrape
from phase01.database.models import init_db
from phase01.shared.config import settings

app = FastAPI(
    title="Spotify NL — Phase 1 API",
    description="Google Play review scraping and storage",
    version="0.1.0",
)


@app.on_event("startup")
def on_startup():
    settings.raw_data_dir.mkdir(parents=True, exist_ok=True)
    init_db(settings.database_url)


app.include_router(scrape.router)
app.include_router(reviews.router)
app.include_router(ingest.router)


@app.get("/health")
def health():
    return {"status": "ok", "phase": 1}
