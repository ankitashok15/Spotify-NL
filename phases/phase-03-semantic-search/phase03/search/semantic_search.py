from __future__ import annotations

import time
from datetime import datetime

from phase03.embedding.embedder import ReviewEmbedder
from phase03.embedding.indexer import QdrantIndexer
from phase03.search.schemas import SearchFilters, SearchHit, SearchResponse, build_qdrant_filter


class SemanticSearchService:
    def __init__(
        self,
        embedder: ReviewEmbedder | None = None,
        indexer: QdrantIndexer | None = None,
    ):
        self.embedder = embedder or ReviewEmbedder()
        self.indexer = indexer or QdrantIndexer()
        self.indexer.ensure_collection()

    def search(
        self,
        query: str,
        *,
        filters: SearchFilters | None = None,
        top_k: int = 20,
    ) -> SearchResponse:
        started = time.perf_counter()
        vector = self.embedder.embed_query(query)
        qdrant_filter = build_qdrant_filter(filters)
        hits = self.indexer.search(vector, top_k=top_k, qdrant_filter=qdrant_filter)

        results: list[SearchHit] = []
        for hit in hits:
            payload = hit.payload or {}
            created = payload.get("review_created_at")
            created_dt = None
            if isinstance(created, str):
                created_dt = datetime.fromisoformat(created.replace("Z", "+00:00"))

            results.append(
                SearchHit(
                    review_id=str(payload.get("document_id") or hit.id),
                    score=float(hit.score),
                    rating=payload.get("rating"),
                    device_type=payload.get("device_type"),
                    subscription_type=payload.get("subscription_type"),
                    primary_issue=payload.get("primary_issue"),
                    is_discovery_related=payload.get("is_discovery_related"),
                    review_created_at=created_dt,
                    thumbs_up=payload.get("thumbs_up"),
                    text_en=payload.get("text_en"),
                    external_review_id=payload.get("external_review_id"),
                )
            )

        took_ms = (time.perf_counter() - started) * 1000
        return SearchResponse(query=query, top_k=top_k, took_ms=round(took_ms, 2), results=results)
