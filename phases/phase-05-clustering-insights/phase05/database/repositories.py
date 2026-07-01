from __future__ import annotations

import uuid

from sqlalchemy import delete, func, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from phase01.database.models import Review
from phase01.shared.constants import ProcessingState
from phase05.database.models import Cluster, ClusterMembership, Insight


class ClusterRepository:
    def __init__(self, session: Session):
        self.session = session

    def clear_all(self) -> None:
        self.session.execute(delete(ClusterMembership))
        self.session.execute(delete(Cluster))

    def upsert_cluster(self, cluster_key: str, data: dict) -> Cluster:
        stmt = insert(Cluster).values(cluster_key=cluster_key, **data)
        update_cols = {k: getattr(stmt.excluded, k) for k in data if k != "cluster_key"}
        update_cols["updated_at"] = func.now()
        stmt = stmt.on_conflict_do_update(index_elements=["cluster_key"], set_=update_cols).returning(Cluster)
        return self.session.execute(stmt).scalar_one()

    def add_membership(self, cluster_id: uuid.UUID, review_id: uuid.UUID) -> None:
        stmt = insert(ClusterMembership).values(cluster_id=cluster_id, review_id=review_id)
        stmt = stmt.on_conflict_do_update(
            index_elements=["review_id"],
            set_={"cluster_id": stmt.excluded.cluster_id, "assigned_at": func.now()},
        )
        self.session.execute(stmt)

    def membership_exists(self, review_id: str | uuid.UUID) -> bool:
        rid = uuid.UUID(str(review_id))
        return (
            self.session.execute(
                select(func.count()).select_from(ClusterMembership).where(ClusterMembership.review_id == rid)
            ).scalar_one()
            > 0
        )

    def mark_review_clustered(self, review_id: uuid.UUID) -> None:
        self.session.execute(
            update(Review).where(Review.id == review_id).values(processing_state=ProcessingState.CLUSTERED.value)
        )

    def list_clusters(self, *, limit: int = 50, offset: int = 0) -> list[Cluster]:
        return list(
            self.session.execute(
                select(Cluster).order_by(Cluster.member_count.desc()).limit(limit).offset(offset)
            ).scalars().all()
        )

    def get_cluster(self, cluster_id: uuid.UUID) -> Cluster | None:
        return self.session.get(Cluster, cluster_id)

    def get_by_key(self, cluster_key: str) -> Cluster | None:
        return self.session.execute(
            select(Cluster).where(Cluster.cluster_key == cluster_key)
        ).scalar_one_or_none()

    def cluster_centroids(self) -> dict[str, list[float]]:
        rows = self.session.execute(select(Cluster.id, Cluster.centroid).where(Cluster.centroid.isnot(None))).all()
        return {str(row[0]): row[1] for row in rows if row[1]}

    def members_for_cluster(self, cluster_id: uuid.UUID, *, limit: int = 20) -> list[uuid.UUID]:
        return list(
            self.session.execute(
                select(ClusterMembership.review_id)
                .where(ClusterMembership.cluster_id == cluster_id)
                .limit(limit)
            ).scalars().all()
        )


class InsightRepository:
    def __init__(self, session: Session):
        self.session = session

    def save(self, data: dict) -> Insight:
        row = Insight(id=uuid.uuid4(), **data)
        self.session.add(row)
        self.session.flush()
        return row

    def list_insights(self, *, insight_type: str | None = None, limit: int = 50) -> list[Insight]:
        query = select(Insight).order_by(Insight.generated_at.desc()).limit(limit)
        if insight_type:
            query = query.where(Insight.insight_type == insight_type)
        return list(self.session.execute(query).scalars().all())

    def latest_report(self) -> Insight | None:
        return self.session.execute(
            select(Insight)
            .where(Insight.insight_type == "weekly_report")
            .order_by(Insight.generated_at.desc())
            .limit(1)
        ).scalar_one_or_none()
