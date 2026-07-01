from fastapi import FastAPI

from phase03.api.routes import search
from phase03.embedding.indexer import QdrantIndexer
from phase03.shared.config import settings

app = FastAPI(
    title="Spotify NL — Phase 3 API",
    description="Semantic search over Google Play reviews",
    version="0.3.0",
)


@app.on_event("startup")
def on_startup():
    QdrantIndexer().ensure_collection()


app.include_router(search.router)


@app.get("/health")
def health():
    indexer = QdrantIndexer()
    return {
        "status": "ok",
        "phase": 3,
        "qdrant_collection": settings.qdrant_collection,
        "qdrant_points": indexer.count_indexed(),
    }
