from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from phase05.database.repositories import ClusterRepository
from phase06.agent.tools.base import AgentTool


class GetClusterTool(AgentTool):
    name = "get_cluster"
    description = "Fetch cluster details and representative review IDs."

    def __init__(self, session: Session) -> None:
        self.session = session
        self.repo = ClusterRepository(session)

    def run(self, args: dict) -> dict:
        cluster_id = args.get("cluster_id")
        cluster_key = args.get("cluster_key")
        cluster = None
        if cluster_id:
            cluster = self.repo.get_cluster(uuid.UUID(str(cluster_id)))
        elif cluster_key:
            cluster = self.repo.get_by_key(str(cluster_key))
        else:
            raise ValueError("get_cluster requires cluster_id or cluster_key")
        if not cluster:
            return {"error": "Cluster not found"}

        members = [str(rid) for rid in self.repo.members_for_cluster(cluster.id, limit=20)]
        return {
            "id": str(cluster.id),
            "cluster_key": cluster.cluster_key,
            "label": cluster.label,
            "description": cluster.description,
            "taxonomy_theme_id": cluster.taxonomy_theme_id,
            "member_count": cluster.member_count,
            "avg_rating": cluster.avg_rating,
            "representative_review_ids": cluster.representative_review_ids or members[:5],
            "member_review_ids": members,
        }
