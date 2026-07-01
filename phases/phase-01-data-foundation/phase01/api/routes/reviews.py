import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from phase01.api.schemas import ReviewListResponse, ReviewResponse
from phase01.database.repositories import ReviewRepository
from phase01.database.session import get_db

router = APIRouter(prefix="/api/v1", tags=["reviews"])


@router.get("/reviews", response_model=ReviewListResponse)
def list_reviews(
    rating: int | None = None,
    rating_min: int | None = Query(None, ge=1, le=5),
    rating_max: int | None = Query(None, ge=1, le=5),
    device_type: str | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    repo = ReviewRepository(db)
    items, total = repo.list_reviews(
        rating=rating,
        rating_min=rating_min,
        rating_max=rating_max,
        device_type=device_type,
        date_from=date_from,
        date_to=date_to,
        limit=limit,
        offset=offset,
    )
    return ReviewListResponse(
        items=[ReviewResponse.model_validate(r) for r in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/reviews/{review_id}", response_model=ReviewResponse)
def get_review(review_id: uuid.UUID, db: Session = Depends(get_db)):
    repo = ReviewRepository(db)
    review = repo.get_by_id(review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return ReviewResponse.model_validate(review)
