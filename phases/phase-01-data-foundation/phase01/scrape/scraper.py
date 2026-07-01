import logging
import uuid
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from phase01.cleaning.pipeline import clean_review_row
from phase01.database.repositories import (
    ReviewRepository,
    ScrapeCheckpointRepository,
    ScrapeRunRepository,
)
from phase01.scrape.batch_writer import write_raw_batch
from phase01.scrape.normalizer import deserialize_token, normalize_play_review, serialize_token
from phase01.scrape.pagination import fetch_review_page, get_sort_enum
from phase01.scrape.rate_limiter import RateLimiter
from phase01.scrape.validator import CorpusValidator
from phase01.scrape.window import batch_oldest_date, filter_reviews_in_window, review_in_window
from phase01.shared.config import settings
from phase01.shared.constants import (
    SORT_PASS_CONFIG,
    CheckpointStatus,
    ScrapeRunStatus,
    ScrapeRunType,
)

logger = logging.getLogger(__name__)


class GooglePlayReviewScraper:
    """Scrapes Spotify Google Play reviews within a rolling time window (default: 6 months)."""

    def __init__(self, session: Session):
        self.session = session
        self.review_repo = ReviewRepository(session)
        self.run_repo = ScrapeRunRepository(session)
        self.checkpoint_repo = ScrapeCheckpointRepository(session)
        self.rate_limiter = RateLimiter(delay_seconds=settings.scrape_delay_seconds)
        self.validator = CorpusValidator(self.review_repo)

    def scrape_all(
        self,
        app_id: str | None = None,
        limit: int | None = None,
        lang: str | None = None,
        country: str | None = None,
        months_back: int | None = None,
    ) -> uuid.UUID:
        app_id = app_id or settings.spotify_app_id
        lang = lang or settings.scrape_lang
        country = country or settings.scrape_country
        cutoff = self._cutoff(months_back)
        months = months_back or settings.scrape_months_back

        logger.info(
            "Starting window scrape for %s — last %s months (from %s)",
            app_id,
            months,
            cutoff.date().isoformat(),
        )

        run = self.run_repo.create(
            ScrapeRunType.WINDOW_BACKFILL,
            app_id,
            reviews_target=None,
            gap_report=self._window_metadata(cutoff, months),
        )

        total_new = 0
        total_updated = 0
        total_scraped = 0

        for sort_key, sort_name in SORT_PASS_CONFIG:
            if limit and total_scraped >= limit:
                break
            pass_limit = (limit - total_scraped) if limit else None
            new, updated, scraped = self._scrape_pass(
                run.id,
                app_id,
                sort_key,
                sort_name,
                lang,
                country,
                cutoff=cutoff,
                limit=pass_limit,
            )
            total_new += new
            total_updated += updated
            total_scraped += scraped

        report = self.validate_corpus(app_id, cutoff=cutoff, months_back=months)
        self.run_repo.update_progress(
            run,
            reviews_scraped=total_scraped,
            reviews_new=total_new,
            reviews_updated=total_updated,
            status=ScrapeRunStatus.COMPLETED,
            gap_report=report.to_dict(),
            ended_at=datetime.now(timezone.utc),
        )
        return run.id

    def resume(
        self,
        app_id: str | None = None,
        months_back: int | None = None,
    ) -> uuid.UUID | None:
        app_id = app_id or settings.spotify_app_id
        cutoff = self._cutoff(months_back)
        months = months_back or settings.scrape_months_back

        run = self.run_repo.get_active(app_id)
        if not run:
            checkpoints = self.checkpoint_repo.get_incomplete_for_app(app_id)
            if not checkpoints:
                logger.info("No active scrape run to resume for %s", app_id)
                return None
            run = self.run_repo.get(checkpoints[0].scrape_run_id)

        total_new = run.reviews_new
        total_updated = run.reviews_updated
        total_scraped = run.reviews_scraped

        sort_enum_names = {"newest": "NEWEST", "rating": "RATING", "most_relevant": "MOST_RELEVANT"}
        for cp in self.checkpoint_repo.get_incomplete_for_app(app_id):
            sort_name = sort_enum_names.get(cp.sort_order, "NEWEST")
            new, updated, scraped = self._scrape_pass(
                run.id,
                app_id,
                cp.sort_order,
                sort_name,
                cp.lang,
                cp.country,
                cutoff=cutoff,
                resume_checkpoint=cp,
            )
            total_new += new
            total_updated += updated
            total_scraped += scraped

        report = self.validate_corpus(app_id, cutoff=cutoff, months_back=months)
        self.run_repo.update_progress(
            run,
            reviews_scraped=total_scraped,
            reviews_new=total_new,
            reviews_updated=total_updated,
            status=ScrapeRunStatus.COMPLETED,
            gap_report=report.to_dict(),
            ended_at=datetime.now(timezone.utc),
        )
        return run.id

    def scrape_incremental(
        self,
        since: datetime | None = None,
        app_id: str | None = None,
        limit: int | None = None,
        months_back: int | None = None,
    ) -> uuid.UUID:
        app_id = app_id or settings.spotify_app_id
        cutoff = self._cutoff(months_back)
        months = months_back or settings.scrape_months_back
        effective_since = max(since, cutoff) if since else cutoff

        run = self.run_repo.create(
            ScrapeRunType.INCREMENTAL,
            app_id,
            gap_report=self._window_metadata(cutoff, months),
        )

        new, updated, scraped = self._scrape_pass(
            run.id,
            app_id,
            "newest",
            "NEWEST",
            settings.scrape_lang,
            settings.scrape_country,
            cutoff=cutoff,
            limit=limit,
            stop_when_older_than=effective_since,
        )

        report = self.validate_corpus(app_id, cutoff=cutoff, months_back=months)
        self.run_repo.update_progress(
            run,
            reviews_scraped=scraped,
            reviews_new=new,
            reviews_updated=updated,
            status=ScrapeRunStatus.COMPLETED,
            gap_report=report.to_dict(),
            ended_at=datetime.now(timezone.utc),
        )
        return run.id

    def validate_corpus(
        self,
        app_id: str | None = None,
        cutoff: datetime | None = None,
        months_back: int | None = None,
    ):
        app_id = app_id or settings.spotify_app_id
        cutoff = cutoff or self._cutoff(months_back)
        return self.validator.validate(
            app_id,
            cutoff,
            months_back or settings.scrape_months_back,
            settings.scrape_lang,
            settings.scrape_country,
        )

    def _cutoff(self, months_back: int | None = None) -> datetime:
        from phase01.scrape.window import scrape_cutoff_date

        return scrape_cutoff_date(months_back or settings.scrape_months_back)

    def _window_metadata(self, cutoff: datetime, months_back: int) -> dict:
        return {
            "window_months": months_back,
            "window_start": cutoff.isoformat(),
            "window_end": datetime.now(timezone.utc).isoformat(),
        }

    def _scrape_pass(
        self,
        run_id: uuid.UUID,
        app_id: str,
        sort_key: str,
        sort_name: str,
        lang: str,
        country: str,
        *,
        cutoff: datetime,
        limit: int | None = None,
        resume_checkpoint=None,
        stop_when_older_than: datetime | None = None,
    ) -> tuple[int, int, int]:
        checkpoint = resume_checkpoint or self.checkpoint_repo.get_or_create(
            run_id, sort_key, lang, country
        )
        token = deserialize_token(checkpoint.continuation_token)
        sort_enum = get_sort_enum(sort_name)

        pass_new = 0
        pass_updated = 0
        pass_scraped = checkpoint.reviews_scraped_in_pass

        while True:
            if limit and pass_scraped >= limit:
                break

            batch_count = min(
                settings.scrape_batch_size,
                (limit - pass_scraped) if limit else settings.scrape_batch_size,
            )

            raw_batch, token = self.rate_limiter.run_with_retry(
                fetch_review_page,
                app_id,
                sort=sort_enum,
                count=batch_count,
                lang=lang,
                country=country,
                continuation_token=token,
            )

            if not raw_batch:
                self.checkpoint_repo.save_token(
                    checkpoint, serialize_token(None), pass_scraped, status=CheckpointStatus.COMPLETED
                )
                self.session.commit()
                break

            # Stop when API pages are entirely before the window or incremental since-date
            raw_oldest = batch_oldest_date(raw_batch)
            if raw_oldest and raw_oldest < cutoff:
                # Last page may straddle the cutoff — keep in-window rows only
                in_window = filter_reviews_in_window(raw_batch, cutoff)
                if stop_when_older_than:
                    in_window = [
                        r for r in in_window if r.get("at") and r.get("at") >= stop_when_older_than
                    ]
                if in_window:
                    write_raw_batch(settings.raw_data_dir, in_window, run_id, sort_key)
                    new, updated = self._upsert_rows(in_window, app_id, run_id)
                    pass_new += new
                    pass_updated += updated
                    pass_scraped += len(in_window)
                self.checkpoint_repo.save_token(
                    checkpoint, None, pass_scraped, status=CheckpointStatus.COMPLETED
                )
                self.session.commit()
                break

            if stop_when_older_than and raw_oldest and raw_oldest < stop_when_older_than:
                in_window = [
                    r
                    for r in raw_batch
                    if review_in_window(r, cutoff)
                    and r.get("at")
                    and r.get("at") >= stop_when_older_than
                ]
                if in_window:
                    write_raw_batch(settings.raw_data_dir, in_window, run_id, sort_key)
                    new, updated = self._upsert_rows(in_window, app_id, run_id)
                    pass_new += new
                    pass_updated += updated
                    pass_scraped += len(in_window)
                self.checkpoint_repo.save_token(
                    checkpoint, None, pass_scraped, status=CheckpointStatus.COMPLETED
                )
                self.session.commit()
                break

            result = filter_reviews_in_window(raw_batch, cutoff)
            if stop_when_older_than:
                result = [r for r in result if r.get("at") and r.get("at") >= stop_when_older_than]

            if result:
                write_raw_batch(settings.raw_data_dir, result, run_id, sort_key)
                new, updated = self._upsert_rows(result, app_id, run_id)
                pass_new += new
                pass_updated += updated
                pass_scraped += len(result)

            status = CheckpointStatus.IN_PROGRESS if token else CheckpointStatus.COMPLETED
            self.checkpoint_repo.save_token(
                checkpoint,
                serialize_token(token),
                pass_scraped,
                status=status,
            )
            self.session.commit()

            logger.info(
                "Pass %s (from %s): batch=%s total_in_pass=%s new=%s updated=%s",
                sort_key,
                cutoff.date().isoformat(),
                len(result),
                pass_scraped,
                pass_new,
                pass_updated,
            )

            if not token:
                break

            self.rate_limiter.wait()

        return pass_new, pass_updated, pass_scraped

    def _upsert_rows(self, raw_batch: list[dict], app_id: str, run_id: uuid.UUID) -> tuple[int, int]:
        rows = []
        for raw in raw_batch:
            row = normalize_play_review(raw, app_id, str(run_id))
            row = clean_review_row(row, self.review_repo)
            row.pop("_content_hash", None)
            row["scrape_run_id"] = run_id
            rows.append(row)
        return self.review_repo.upsert_reviews_batch(rows)
