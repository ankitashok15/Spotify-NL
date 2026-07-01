import logging
from dataclasses import dataclass
from datetime import datetime

from phase01.database.repositories import ReviewRepository

logger = logging.getLogger(__name__)


@dataclass
class ValidationReport:
    app_id: str
    window_months: int
    window_start: str
    window_end: str
    database_review_count: int
    reviews_in_window: int
    reviews_outside_window: int
    distinct_external_ids: int
    coverage_pct: float | None
    passes_window: bool
    passes_dedup: bool
    rating_distribution: dict[int, int]
    errors: list[str]

    def to_dict(self) -> dict:
        return {
            "app_id": self.app_id,
            "window_months": self.window_months,
            "window_start": self.window_start,
            "window_end": self.window_end,
            "database_review_count": self.database_review_count,
            "reviews_in_window": self.reviews_in_window,
            "reviews_outside_window": self.reviews_outside_window,
            "distinct_external_ids": self.distinct_external_ids,
            "coverage_pct": round(self.coverage_pct, 4) if self.coverage_pct is not None else None,
            "passes_window": self.passes_window,
            "passes_dedup": self.passes_dedup,
            "rating_distribution": self.rating_distribution,
            "errors": self.errors,
        }


class CorpusValidator:
    """Validates scraped reviews against the configured rolling window (default 6 months)."""

    def __init__(self, review_repo: ReviewRepository):
        self.review_repo = review_repo

    def validate(
        self,
        app_id: str,
        cutoff: datetime,
        window_months: int,
        lang: str = "en",
        country: str = "us",
    ) -> ValidationReport:
        errors: list[str] = []

        db_count = self.review_repo.count_all()
        in_window = self.review_repo.count_since(cutoff)
        outside_window = self.review_repo.count_before(cutoff)
        distinct_count = self.review_repo.count_distinct_external_ids()
        rating_dist = self.review_repo.rating_distribution()

        passes_window = outside_window == 0
        passes_dedup = db_count == distinct_count

        if not passes_window:
            errors.append(
                f"reviews_outside_window: {outside_window} reviews older than {cutoff.date().isoformat()}"
            )
        if not passes_dedup:
            errors.append(f"duplicate_external_ids: total={db_count}, distinct={distinct_count}")

        coverage_pct = None
        if in_window > 0:
            coverage_pct = 100.0

        return ValidationReport(
            app_id=app_id,
            window_months=window_months,
            window_start=cutoff.isoformat(),
            window_end=datetime.now(cutoff.tzinfo).isoformat(),
            database_review_count=db_count,
            reviews_in_window=in_window,
            reviews_outside_window=outside_window,
            distinct_external_ids=distinct_count,
            coverage_pct=coverage_pct,
            passes_window=passes_window,
            passes_dedup=passes_dedup,
            rating_distribution=rating_dist,
            errors=errors,
        )
