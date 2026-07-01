from __future__ import annotations

import logging
import uuid

from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels

from phase03.embedding.embedder import EmbeddedReview
from phase03.embedding.provider import DEFAULT_EMBEDDING_MODEL, EMBEDDING_DIMENSION
from phase03.shared.config import settings

logger = logging.getLogger(__name__)


class QdrantIndexer:
    def __init__(
        self,
        url: str | None = None,
        api_key: str | None = None,
        collection_name: str | None = None,
    ) -> None:
        self.collection_name = collection_name or settings.qdrant_collection
        key = api_key if api_key is not None else settings.qdrant_api_key or None
        self.client = QdrantClient(
            url=url or settings.qdrant_url,
            api_key=key,
            check_compatibility=False,
        )

    def ensure_collection(self) -> None:
        if self.client.collection_exists(self.collection_name):
            info = self.client.get_collection(self.collection_name)
            current_size = info.config.params.vectors.size  # type: ignore[union-attr]
            points = int(info.points_count or 0)
            if current_size != EMBEDDING_DIMENSION:
                if points > 0:
                    raise ValueError(
                        f"Qdrant collection {self.collection_name} has dimension {current_size} "
                        f"but model expects {EMBEDDING_DIMENSION}. Reindex required."
                    )
                logger.warning(
                    "Recreating empty collection %s (%s -> %s dims)",
                    self.collection_name,
                    current_size,
                    EMBEDDING_DIMENSION,
                )
                self.client.delete_collection(self.collection_name)
            else:
                return

        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=qmodels.VectorParams(
                size=EMBEDDING_DIMENSION,
                distance=qmodels.Distance.COSINE,
            ),
        )
        self._ensure_payload_indexes()

    def _ensure_payload_indexes(self) -> None:
        for field_name, schema in (
            ("rating", qmodels.PayloadSchemaType.INTEGER),
            ("subscription_type", qmodels.PayloadSchemaType.KEYWORD),
            ("device_type", qmodels.PayloadSchemaType.KEYWORD),
            ("primary_issue", qmodels.PayloadSchemaType.KEYWORD),
            ("is_discovery_related", qmodels.PayloadSchemaType.BOOL),
            ("review_created_at", qmodels.PayloadSchemaType.DATETIME),
        ):
            try:
                self.client.create_payload_index(
                    collection_name=self.collection_name,
                    field_name=field_name,
                    field_schema=schema,
                )
            except Exception as exc:
                logger.debug("Payload index %s may already exist: %s", field_name, exc)

    def upsert_embeddings(self, items: list[EmbeddedReview]) -> int:
        if not items:
            return 0

        points = [
            qmodels.PointStruct(
                id=str(item.review_id),
                vector=item.vector,
                payload=item.payload,
            )
            for item in items
        ]
        self.client.upsert(collection_name=self.collection_name, points=points)
        return len(points)

    def count_indexed(self) -> int:
        if not self.client.collection_exists(self.collection_name):
            return 0
        info = self.client.get_collection(self.collection_name)
        return int(info.points_count or 0)

    def search(
        self,
        query_vector: list[float],
        *,
        top_k: int = 20,
        qdrant_filter: qmodels.Filter | None = None,
    ) -> list:
        response = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            limit=top_k,
            query_filter=qdrant_filter,
            with_payload=True,
        )
        return list(response.points or [])

    def get_by_id(self, review_id: uuid.UUID) -> qmodels.Record | None:
        records = self.client.retrieve(
            collection_name=self.collection_name,
            ids=[str(review_id)],
            with_payload=True,
            with_vectors=False,
        )
        return records[0] if records else None
