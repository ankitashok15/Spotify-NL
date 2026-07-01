import uuid

from sqlalchemy import func, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from phase01.database.models import Review
from phase01.shared.constants import ProcessingState
from phase02.database.models import ExtractionCache, StructuredReview


class StructuredReviewRepository:
    def __init__(self, session: Session):
        self.session = session

    def upsert(self, data: dict) -> StructuredReview:
        stmt = insert(StructuredReview).values(**data)
        update_cols = {
            k: getattr(stmt.excluded, k)
            for k in data
            if k not in ("id", "review_id", "created_at")
        }
        update_cols["updated_at"] = func.now()
        stmt = stmt.on_conflict_do_update(
            index_elements=["review_id"],
            set_=update_cols,
        ).returning(StructuredReview)
        return self.session.execute(stmt).scalar_one()

    def get_by_review_id(self, review_id: uuid.UUID) -> StructuredReview | None:
        return self.session.execute(
            select(StructuredReview).where(StructuredReview.review_id == review_id)
        ).scalar_one_or_none()

    def count_all(self) -> int:
        return self.session.execute(select(func.count()).select_from(StructuredReview)).scalar_one()

    def count_discovery_related(self) -> int:
        return self.session.execute(
            select(func.count())
            .select_from(StructuredReview)
            .where(StructuredReview.is_discovery_related.is_(True))
        ).scalar_one()


class ExtractionCacheRepository:
    def __init__(self, session: Session):
        self.session = session

    def get(self, content_hash: str) -> dict | None:
        row = self.session.execute(
            select(ExtractionCache).where(ExtractionCache.content_hash == content_hash)
        ).scalar_one_or_none()
        return row.extraction_payload if row else None

    def put(self, content_hash: str, payload: dict, model_name: str | None = None) -> None:
        stmt = insert(ExtractionCache).values(
            content_hash=content_hash,
            extraction_payload=payload,
            model_name=model_name,
        )
        stmt = stmt.on_conflict_do_update(
            index_elements=["content_hash"],
            set_={
                "extraction_payload": stmt.excluded.extraction_payload,
                "model_name": stmt.excluded.model_name,
            },
        )
        self.session.execute(stmt)


class ReviewExtractionRepository:
    """Fetch reviews pending Phase 2 processing."""

    def __init__(self, session: Session):
        self.session = session

    def fetch_pending(
        self,
        *,
        limit: int = 100,
        skip_spam: bool = True,
        review_ids: list[uuid.UUID] | None = None,
    ) -> list[Review]:
        states = [
            ProcessingState.CLEANED.value,
            ProcessingState.RAW.value,
            ProcessingState.TRANSLATED.value,
        ]
        query = (
            select(Review)
            .outerjoin(StructuredReview, StructuredReview.review_id == Review.id)
            .where(
                Review.processing_state.in_(states),
                StructuredReview.id.is_(None),
            )
            .order_by(Review.review_created_at.desc().nullslast())
            .limit(limit)
        )
        if skip_spam:
            query = query.where(Review.is_spam.is_(False))
        if review_ids:
            query = (
                select(Review)
                .outerjoin(StructuredReview, StructuredReview.review_id == Review.id)
                .where(
                    Review.id.in_(review_ids),
                    StructuredReview.id.is_(None),
                )
            )
        return list(self.session.execute(query).scalars().all())

    def mark_translated(self, review_id: uuid.UUID) -> None:
        self.session.execute(
            update(Review)
            .where(Review.id == review_id)
            .values(processing_state=ProcessingState.TRANSLATED.value)
        )

    def mark_extracted(self, review_id: uuid.UUID) -> None:
        self.session.execute(
            update(Review)
            .where(Review.id == review_id)
            .values(processing_state=ProcessingState.EXTRACTED.value)
        )

    def count_pending(self, *, skip_spam: bool = True) -> int:
        states = [
            ProcessingState.CLEANED.value,
            ProcessingState.RAW.value,
            ProcessingState.TRANSLATED.value,
        ]
        query = (
            select(func.count())
            .select_from(Review)
            .outerjoin(StructuredReview, StructuredReview.review_id == Review.id)
            .where(
                Review.processing_state.in_(states),
                StructuredReview.id.is_(None),
            )
        )
        if skip_spam:
            query = query.where(Review.is_spam.is_(False))
        return self.session.execute(query).scalar_one()
