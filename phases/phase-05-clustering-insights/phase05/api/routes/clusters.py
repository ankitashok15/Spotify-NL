from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from phase05.api.schemas import ClusterDetailResponse, ClusterListResponse, ClusterSummary
from phase05.database.repositories import ClusterRepository
from phase05.database.session import get_db_session

router = APIRouter(prefix="/api/v1", tags=["clusters"])


def get_session():
    with get_db_session() as session:
        yield session


@router.get("/clusters", response_model=ClusterListResponse)
def list_clusters(limit: int = 50, offset: int = 0, session: Session = Depends(get_session)):
    repo = ClusterRepository(session)
    items = repo.list_clusters(limit=limit, offset=offset)
    return ClusterListResponse(
        items=[ClusterSummary.model_validate(c) for c in items],
        total=len(items),
    )


@router.get("/clusters/{cluster_id}", response_model=ClusterDetailResponse)
def get_cluster(cluster_id: UUID, session: Session = Depends(get_session)):
    repo = ClusterRepository(session)
    cluster = repo.get_cluster(cluster_id)
    if not cluster:
        raise HTTPException(status_code=404, detail="Cluster not found")
    members = [str(rid) for rid in repo.members_for_cluster(cluster_id)]
    data = ClusterSummary.model_validate(cluster).model_dump()
    return ClusterDetailResponse(**data, member_review_ids=members)
