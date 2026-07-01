from __future__ import annotations

import logging
import uuid
from collections import Counter, defaultdict

import numpy as np
from qdrant_client import QdrantClient
from sqlalchemy.orm import Session

from phase01.shared.constants import ProcessingState
from phase05.clustering.clusterer import ReviewClusterer, VectorPoint
from phase05.database.repositories import ClusterRepository
from phase05.shared.config import settings

logger = logging.getLogger(__name__)


class IncrementalClusterAssigner:
    """Assign new embedded reviews to nearest existing cluster centroid."""

    def __init__(self, session: Session, qdrant: QdrantClient | None = None):
        self.session = session
        self.repo = ClusterRepository(session)
        key = settings.qdrant_api_key or None
        self.client = qdrant or QdrantClient(url=settings.qdrant_url, api_key=key)
        self.clusterer = ReviewClusterer(self.client)

    def assign_pending(self, *, limit: int = 200) -> int:
        centroids = self.repo.cluster_centroids()
        if not centroids:
            logger.info("No cluster centroids found; run full cluster job first")
            return 0

        points = self.clusterer.load_vectors(limit=limit)
        assigned = 0
        for point in points:
            if self.repo.membership_exists(point.review_id):
                continue
            cluster_id = self._nearest_cluster(point, centroids)
            if cluster_id:
                self.repo.add_membership(uuid.UUID(cluster_id), uuid.UUID(point.review_id))
                self.repo.mark_review_clustered(uuid.UUID(point.review_id))
                assigned += 1
        self.session.commit()
        return assigned

    def _nearest_cluster(self, point: VectorPoint, centroids: dict[str, list[float]]) -> str | None:
        if not centroids:
            return None
        vec = np.array(point.vector, dtype=np.float32)
        best_id = None
        best_sim = -1.0
        for cluster_id, centroid in centroids.items():
            c = np.array(centroid, dtype=np.float32)
            denom = (np.linalg.norm(vec) * np.linalg.norm(c)) or 1.0
            sim = float(np.dot(vec, c) / denom)
            if sim > best_sim:
                best_sim = sim
                best_id = cluster_id
        return best_id


def aggregate_cluster_stats(
    assignments: dict[str, int],
    points: list[VectorPoint],
) -> dict[int, dict]:
    by_cluster: dict[int, list[VectorPoint]] = defaultdict(list)
    point_map = {p.review_id: p for p in points}
    for review_id, label in assignments.items():
        if review_id in point_map:
            by_cluster[label].append(point_map[review_id])

    stats: dict[int, dict] = {}
    for label, members in by_cluster.items():
        ratings = [m.payload.get("rating") for m in members if m.payload.get("rating") is not None]
        thumbs = [m.payload.get("thumbs_up") or 0 for m in members]
        subs = Counter(m.payload.get("subscription_type") or "unknown" for m in members)
        devices = Counter(m.payload.get("device_type") or "unknown" for m in members)
        vectors = [m.vector for m in members]
        centroid = np.mean(np.array(vectors, dtype=np.float32), axis=0).tolist() if vectors else []
        stats[label] = {
            "member_count": len(members),
            "avg_rating": round(sum(ratings) / len(ratings), 2) if ratings else None,
            "avg_thumbs_up": round(sum(thumbs) / len(thumbs), 2) if thumbs else 0,
            "top_subscription_types": [k for k, _ in subs.most_common(3)],
            "top_device_types": [k for k, _ in devices.most_common(3)],
            "representative_review_ids": [m.review_id for m in members[:5]],
            "centroid": centroid,
            "sample_texts": [
                (m.payload.get("text_en") or "")[:400]
                for m in members[:8]
            ],
            "primary_issues": [m.payload.get("primary_issue") for m in members[:8]],
        }
    return stats
