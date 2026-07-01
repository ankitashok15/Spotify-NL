from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from phase01.database.models import Review
from phase01.shared.constants import ProcessingState
from phase02.database.models import StructuredReview


@dataclass
class ReviewEmbedRow:
    review: Review
    structured: StructuredReview | None

    @property
    def review_id(self) -> uuid.UUID:
        return self.review.id

    def to_embed_input(self):
        from phase03.embedding.templates import ReviewEmbedInput

        text_en = None
        primary_issue = None
        secondary_issues = None
        mentioned_features = None
        subscription_type = None
        is_discovery_related = False

        if self.structured:
            text_en = self.structured.text_en
            primary_issue = self.structured.primary_issue
            secondary_issues = self.structured.secondary_issues
            mentioned_features = self.structured.mentioned_features
            subscription_type = self.structured.subscription_type
            is_discovery_related = bool(self.structured.is_discovery_related)

        text_en = text_en or self.review.text_cleaned or self.review.text_original or ""

        return ReviewEmbedInput(
            review_id=str(self.review.id),
            text_en=text_en,
            rating=self.review.rating,
            primary_issue=primary_issue,
            secondary_issues=secondary_issues or [],
            mentioned_features=mentioned_features or [],
        ), {
            "rating": self.review.rating,
            "device_type": self.review.device_type,
            "subscription_type": subscription_type,
            "primary_issue": primary_issue,
            "is_discovery_related": is_discovery_related,
            "review_created_at": self.review.review_created_at,
            "thumbs_up": self.review.thumbs_up,
            "external_review_id": self.review.external_review_id,
        }


class EmbeddingReviewRepository:
    def __init__(self, session: Session):
        self.session = session

    def fetch_pending(
        self,
        *,
        limit: int = 100,
        review_ids: list[uuid.UUID] | None = None,
    ) -> list[ReviewEmbedRow]:
        query = (
            select(Review, StructuredReview)
            .outerjoin(StructuredReview, StructuredReview.review_id == Review.id)
            .where(
                Review.processing_state.notin_(
                    [ProcessingState.INDEXED.value, ProcessingState.CLUSTERED.value]
                ),
                Review.is_spam.is_(False),
            )
            .order_by(Review.review_created_at.desc().nullslast())
            .limit(limit)
        )
        if review_ids:
            query = (
                select(Review, StructuredReview)
                .outerjoin(StructuredReview, StructuredReview.review_id == Review.id)
                .where(Review.id.in_(review_ids))
            )
        rows = self.session.execute(query).all()
        return [ReviewEmbedRow(review=r, structured=s) for r, s in rows]

    def count_pending(self) -> int:
        return self.session.execute(
            select(func.count())
            .select_from(Review)
            .where(
                Review.processing_state.notin_(
                    [ProcessingState.INDEXED.value, ProcessingState.CLUSTERED.value]
                ),
                Review.is_spam.is_(False),
            )
        ).scalar_one()

    def mark_embedded(self, review_ids: list[uuid.UUID]) -> None:
        if not review_ids:
            return
        self.session.execute(
            update(Review)
            .where(Review.id.in_(review_ids))
            .values(processing_state=ProcessingState.EMBEDDED.value)
        )

    def mark_indexed(self, review_ids: list[uuid.UUID]) -> None:
        if not review_ids:
            return
        self.session.execute(
            update(Review)
            .where(Review.id.in_(review_ids))
            .values(processing_state=ProcessingState.INDEXED.value)
        )

    def count_by_state(self, state: str) -> int:
        return self.session.execute(
            select(func.count()).select_from(Review).where(Review.processing_state == state)
        ).scalar_one()
