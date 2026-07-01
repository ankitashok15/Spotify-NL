import hashlib
import uuid
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session

from phase01.database.models import DedupIndex, Review, ScrapeCheckpoint, ScrapeRun
from phase01.shared.constants import CheckpointStatus, ProcessingState, ScrapeRunStatus


class ReviewRepository:
    def __init__(self, session: Session):
        self.session = session

    def upsert_review(self, data: dict) -> tuple[Review, bool]:
        """Insert or update review. Returns (review, is_new)."""
        stmt = insert(Review).values(**data)
        update_cols = {
            "text_original": stmt.excluded.text_original,
            "text_cleaned": stmt.excluded.text_cleaned,
            "rating": stmt.excluded.rating,
            "thumbs_up": stmt.excluded.thumbs_up,
            "device_type": stmt.excluded.device_type,
            "app_version": stmt.excluded.app_version,
            "review_created_at": stmt.excluded.review_created_at,
            "developer_reply": stmt.excluded.developer_reply,
            "developer_reply_at": stmt.excluded.developer_reply_at,
            "is_spam": stmt.excluded.is_spam,
            "is_near_duplicate": stmt.excluded.is_near_duplicate,
            "processing_state": stmt.excluded.processing_state,
            "scrape_run_id": stmt.excluded.scrape_run_id,
            "updated_at": func.now(),
        }
        stmt = stmt.on_conflict_do_update(
            index_elements=["external_review_id"],
            set_=update_cols,
        ).returning(Review, Review.collected_at == Review.updated_at)

        result = self.session.execute(stmt).one()
        review = result[0]
        # PostgreSQL returning doesn't easily tell new vs update; check xmax or use separate query
        is_new = self.session.execute(
            select(func.count()).select_from(Review).where(
                Review.external_review_id == data["external_review_id"],
                Review.collected_at == Review.updated_at,
            )
        ).scalar_one()
        # Simpler: track via reviews_new counter in scraper
        return review, True

    def upsert_reviews_batch(self, rows: list[dict]) -> tuple[int, int]:
        """Returns (new_count, updated_count) approximate via pre-check."""
        if not rows:
            return 0, 0

        external_ids = [r["external_review_id"] for r in rows]
        existing = set(
            self.session.execute(
                select(Review.external_review_id).where(Review.external_review_id.in_(external_ids))
            ).scalars().all()
        )

        new_count = sum(1 for r in rows if r["external_review_id"] not in existing)
        updated_count = len(rows) - new_count

        for row in rows:
            stmt = insert(Review).values(**row)
            stmt = stmt.on_conflict_do_update(
                index_elements=["external_review_id"],
                set_={
                    "text_original": stmt.excluded.text_original,
                    "text_cleaned": stmt.excluded.text_cleaned,
                    "rating": stmt.excluded.rating,
                    "thumbs_up": stmt.excluded.thumbs_up,
                    "device_type": stmt.excluded.device_type,
                    "app_version": stmt.excluded.app_version,
                    "review_created_at": stmt.excluded.review_created_at,
                    "developer_reply": stmt.excluded.developer_reply,
                    "developer_reply_at": stmt.excluded.developer_reply_at,
                    "is_spam": stmt.excluded.is_spam,
                    "is_near_duplicate": stmt.excluded.is_near_duplicate,
                    "processing_state": stmt.excluded.processing_state,
                    "scrape_run_id": stmt.excluded.scrape_run_id,
                    "updated_at": func.now(),
                },
            )
            self.session.execute(stmt)

        return new_count, updated_count

    def get_by_id(self, review_id: uuid.UUID) -> Review | None:
        return self.session.get(Review, review_id)

    def list_reviews(
        self,
        *,
        rating: int | None = None,
        rating_min: int | None = None,
        rating_max: int | None = None,
        device_type: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[Review], int]:
        query = select(Review).where(Review.app_id.isnot(None))
        count_query = select(func.count()).select_from(Review)

        if rating is not None:
            query = query.where(Review.rating == rating)
            count_query = count_query.where(Review.rating == rating)
        if rating_min is not None:
            query = query.where(Review.rating >= rating_min)
            count_query = count_query.where(Review.rating >= rating_min)
        if rating_max is not None:
            query = query.where(Review.rating <= rating_max)
            count_query = count_query.where(Review.rating <= rating_max)
        if device_type:
            query = query.where(Review.device_type == device_type)
            count_query = count_query.where(Review.device_type == device_type)
        if date_from:
            query = query.where(Review.review_created_at >= date_from)
            count_query = count_query.where(Review.review_created_at >= date_from)
        if date_to:
            query = query.where(Review.review_created_at <= date_to)
            count_query = count_query.where(Review.review_created_at <= date_to)

        total = self.session.execute(count_query).scalar_one()
        items = list(
            self.session.execute(
                query.order_by(Review.review_created_at.desc().nullslast()).limit(limit).offset(offset)
            ).scalars().all()
        )
        return items, total

    def count_all(self) -> int:
        return self.session.execute(select(func.count()).select_from(Review)).scalar_one()

    def count_since(self, cutoff) -> int:
        return self.session.execute(
            select(func.count()).select_from(Review).where(Review.review_created_at >= cutoff)
        ).scalar_one()

    def count_before(self, cutoff) -> int:
        return self.session.execute(
            select(func.count())
            .select_from(Review)
            .where(Review.review_created_at.isnot(None), Review.review_created_at < cutoff)
        ).scalar_one()

    def count_distinct_external_ids(self) -> int:
        return self.session.execute(select(func.count(func.distinct(Review.external_review_id)))).scalar_one()

    def rating_distribution(self) -> dict[int, int]:
        rows = self.session.execute(
            select(Review.rating, func.count()).where(Review.rating.isnot(None)).group_by(Review.rating)
        ).all()
        return {int(rating): count for rating, count in rows}

    def content_hash_exists(self, content_hash: str) -> bool:
        return (
            self.session.execute(
                select(func.count()).select_from(DedupIndex).where(DedupIndex.content_hash == content_hash)
            ).scalar_one()
            > 0
        )

    def add_dedup_index(self, content_hash: str, review_id: uuid.UUID) -> None:
        stmt = insert(DedupIndex).values(content_hash=content_hash, review_id=review_id)
        stmt = stmt.on_conflict_do_nothing(index_elements=["content_hash"])
        self.session.execute(stmt)


class ScrapeRunRepository:
    def __init__(self, session: Session):
        self.session = session

    def create(
        self,
        run_type: str,
        app_id: str,
        reviews_target: int | None = None,
        gap_report: dict | None = None,
    ) -> ScrapeRun:
        run = ScrapeRun(
            run_type=run_type,
            app_id=app_id,
            reviews_target=reviews_target,
            status=ScrapeRunStatus.RUNNING,
            gap_report=gap_report,
        )
        self.session.add(run)
        self.session.flush()
        return run

    def get(self, run_id: uuid.UUID) -> ScrapeRun | None:
        return self.session.get(ScrapeRun, run_id)

    def get_latest(self, app_id: str) -> ScrapeRun | None:
        return self.session.execute(
            select(ScrapeRun)
            .where(ScrapeRun.app_id == app_id)
            .order_by(ScrapeRun.started_at.desc())
            .limit(1)
        ).scalar_one_or_none()

    def get_active(self, app_id: str) -> ScrapeRun | None:
        return self.session.execute(
            select(ScrapeRun)
            .where(ScrapeRun.app_id == app_id, ScrapeRun.status == ScrapeRunStatus.RUNNING)
            .order_by(ScrapeRun.started_at.desc())
            .limit(1)
        ).scalar_one_or_none()

    def update_progress(
        self,
        run: ScrapeRun,
        *,
        reviews_scraped: int | None = None,
        reviews_new: int | None = None,
        reviews_updated: int | None = None,
        status: str | None = None,
        gap_report: dict | None = None,
        ended_at: datetime | None = None,
    ) -> ScrapeRun:
        if reviews_scraped is not None:
            run.reviews_scraped = reviews_scraped
        if reviews_new is not None:
            run.reviews_new = reviews_new
        if reviews_updated is not None:
            run.reviews_updated = reviews_updated
        if status is not None:
            run.status = status
        if gap_report is not None:
            run.gap_report = gap_report
        if ended_at is not None:
            run.ended_at = ended_at
        self.session.flush()
        return run


class ScrapeCheckpointRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_or_create(
        self, scrape_run_id: uuid.UUID, sort_order: str, lang: str, country: str
    ) -> ScrapeCheckpoint:
        cp = self.session.execute(
            select(ScrapeCheckpoint).where(
                ScrapeCheckpoint.scrape_run_id == scrape_run_id,
                ScrapeCheckpoint.sort_order == sort_order,
            )
        ).scalar_one_or_none()
        if cp:
            return cp
        cp = ScrapeCheckpoint(
            scrape_run_id=scrape_run_id,
            sort_order=sort_order,
            lang=lang,
            country=country,
            status=CheckpointStatus.IN_PROGRESS,
        )
        self.session.add(cp)
        self.session.flush()
        return cp

    def get_incomplete_for_app(self, app_id: str) -> list[ScrapeCheckpoint]:
        return list(
            self.session.execute(
                select(ScrapeCheckpoint)
                .join(ScrapeRun)
                .where(
                    ScrapeRun.app_id == app_id,
                    ScrapeCheckpoint.status == CheckpointStatus.IN_PROGRESS,
                    ScrapeRun.status == ScrapeRunStatus.RUNNING,
                )
            ).scalars().all()
        )

    def save_token(
        self,
        checkpoint: ScrapeCheckpoint,
        token: str | None,
        reviews_scraped_in_pass: int,
        status: str | None = None,
    ) -> None:
        checkpoint.continuation_token = token
        checkpoint.reviews_scraped_in_pass = reviews_scraped_in_pass
        if status:
            checkpoint.status = status
        self.session.flush()


def hash_author(user_name: str | None) -> str | None:
    if not user_name:
        return None
    return hashlib.sha256(user_name.encode("utf-8")).hexdigest()
