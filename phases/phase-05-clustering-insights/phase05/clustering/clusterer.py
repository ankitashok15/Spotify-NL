from __future__ import annotations

import logging
from dataclasses import dataclass

import numpy as np
from qdrant_client import QdrantClient

from phase05.shared.config import settings

logger = logging.getLogger(__name__)


@dataclass
class VectorPoint:
    review_id: str
    vector: list[float]
    payload: dict


class ReviewClusterer:
    """Cluster review embeddings from Qdrant using K-Means or HDBSCAN."""

    def __init__(self, qdrant: QdrantClient | None = None):
        key = settings.qdrant_api_key or None
        self.client = qdrant or QdrantClient(url=settings.qdrant_url, api_key=key)
        self.collection = settings.qdrant_collection

    def load_vectors(self, *, limit: int | None = None) -> list[VectorPoint]:
        if not self.client.collection_exists(self.collection):
            return []

        points: list[VectorPoint] = []
        offset = None
        while True:
            batch_limit = 100
            if limit is not None:
                remaining = limit - len(points)
                if remaining <= 0:
                    break
                batch_limit = min(batch_limit, remaining)

            records, offset = self.client.scroll(
                collection_name=self.collection,
                limit=batch_limit,
                offset=offset,
                with_vectors=True,
                with_payload=True,
            )
            for record in records:
                if record.vector is None:
                    continue
                vector = record.vector if isinstance(record.vector, list) else list(record.vector)
                review_id = str((record.payload or {}).get("document_id") or record.id)
                points.append(VectorPoint(review_id=review_id, vector=vector, payload=record.payload or {}))

            if not records or offset is None:
                break

        return points

    def fit(self, points: list[VectorPoint]) -> dict[str, int]:
        if len(points) < settings.cluster_min_size:
            raise ValueError(f"Need at least {settings.cluster_min_size} vectors to cluster")

        matrix = np.array([p.vector for p in points], dtype=np.float32)
        labels = self._cluster_labels(matrix)
        return {points[i].review_id: int(labels[i]) for i in range(len(points))}

    def _cluster_labels(self, matrix: np.ndarray) -> np.ndarray:
        algo = settings.cluster_algorithm.lower()
        if algo == "hdbscan":
            try:
                import hdbscan

                clusterer = hdbscan.HDBSCAN(min_cluster_size=settings.cluster_min_size)
                labels = clusterer.fit_predict(matrix)
                return labels
            except ImportError:
                logger.warning("hdbscan not installed; falling back to KMeans")

        from sklearn.cluster import KMeans

        k = min(settings.cluster_k, len(matrix))
        k = max(2, k)
        model = KMeans(n_clusters=k, random_state=42, n_init=10)
        return model.fit_predict(matrix)
